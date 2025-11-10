from typing import List, Dict, Any, Union
from sqlalchemy import text
from Backend.schema import Decomposition
from Backend.prompts import Prompts
from Backend.llm import classify_operation, generate_sql,_get_chat_model, _extract_json

DECOMPOSE_SYSTEM = Prompts.DECOMPOSE_SYSTEM

def decompose_request(natural_request: str) -> List[str]:
    chat = _get_chat_model()
    msgs = [
        ("system", DECOMPOSE_SYSTEM),
        ("human", natural_request),
    ]
    resp = chat.invoke(msgs)
    content = resp.content if hasattr(resp, "content") else str(resp)

    data = _extract_json(content)
    deco = Decomposition(**data)
    return deco.subqueries

# --- 2) SQL execution helpers ---
def _ensure_single_statement(sql: str) -> str:
    """Reject multi-statement SQL for safety; allow trailing semicolon."""
    s = sql.strip()
    # crude but effective: more than one semicolon with non-empty after split
    parts = [p.strip() for p in s.split(";") if p.strip()]
    if len(parts) > 1:
        raise ValueError("Multi-statement SQL is not allowed.")
    return s

def _execute_sql(conn, sql: str, category: str) -> Dict[str, Any]:
    """Execute SQL and return a normalized result payload."""
    sql = _ensure_single_statement(sql)
    if category == "SELECT":
        rows = conn.execute(text(sql)).fetchall()
        # Convert Row objects to dicts where possible
        try:
            cols = rows[0].keys() if rows else []
            data = [dict(zip(cols, r)) for r in rows]
        except Exception:
            data = [tuple(r) for r in rows]
        return {"rowcount": len(rows), "rows": data}
    else:
        res = conn.execute(text(sql))
        return {"rowcount": getattr(res, "rowcount", None)}

# --- 3) End-to-end for one basic natural sub-query ---
def run_basic_query(natural_request: str, conn) -> Dict[str, Any]:
    """
    Classify → generate SQL → execute.
    Returns dict: { 'subquery', 'category', 'sql', 'result' }
    """
    op = classify_operation(natural_request)          # Category model
    q = generate_sql(natural_request, op)             # Query model

    exec_result = _execute_sql(conn, q.query, q.category)
    return {
        "subquery": natural_request,
        "category": q.category,
        "sql": q.query,
        "result": exec_result,
    }

# --- 4) Composite runner (atomic transaction by default) ---
def run_composite_query(natural_request: str, engine, atomic: bool = True) -> List[Dict[str, Any]]:
    """
    Decompose a composite natural request into atomic steps, convert each to SQL,
    and execute them in order.

    Args:
        natural_request: The composite user instruction.
        engine: SQLAlchemy Engine.
        atomic: If True, run all steps in a single transaction (rollback on error).
                If False, each step runs in its own auto-commit context.

    Returns:
        List of dicts with per-step details: subquery, category, sql, result.
    """
    subqueries = decompose_request(natural_request)
    if not subqueries:
        return []

    results: List[Dict[str, Any]] = []

    if atomic:
        # One transaction for all steps
        with engine.begin() as conn:
            for sq in subqueries:
                step = run_basic_query(sq, conn)
                results.append(step)
    else:
        # Each step independent
        for sq in subqueries:
            with engine.begin() as conn:
                step = run_basic_query(sq, conn)
                results.append(step)

    return results
