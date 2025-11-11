from typing import List, Dict, Any
from Backend.utils import get_chat_model
from Backend.prompts import Prompts
import json

SUMMARIZE_SYSTEM_PROMPT = Prompts.SUMMARIZE_SYSTEM_PROMPT

def _truncate_rows(rows: List[Dict[str, Any]], max_rows: int = 20) -> List[Dict[str, Any]]:
  if not isinstance(rows, list):
      return []
  if not rows:
    return []
  if not isinstance(rows[0], dict):
    return [{"value" : str(r) for r in rows(max_rows)}]
  return rows[:max_rows]

def _summarize_prompt(steps: List[Dict[str, Any]]) -> List[tuple]:
  """
    steps: list of {
      "step": int,
      "category": "SELECT|INSERT|UPDATE|DELETE|DDL|SCHEMA|OTHER",
      "sql": "SELECT ...",
      "rowcount": int | None,
      "rows_sample": [ {col: val, ...}, ... ],
      "columns": [ ... ]
    }
    """
  user = (
    "Here are the steps and their results JSON:\n\n"
    +json.dumps(steps, ensure_ascii=False, indent=2)
    + "\n\nPlease provide a clear, concise summary."
  )
  return [('system', SUMMARIZE_SYSTEM_PROMPT), ('human', user)]

def summarize_nlg(steps: List[Dict[str, Any]]) -> str:
  """
    steps: list of dicts with keys:
      - category: str (SELECT/INSERT/UPDATE/DELETE/DDL/SCHEMA/OTHER)
      - sql: str
      - rows: list[dict] for SELECT (from retrieve_sql_query)
      - rowcount: int | None (optional; for DML if you capture it)
    Returns: natural language summary (str)
  """
  payload = []
  
  for i, step in enumerate(steps,start=1):
    category= step.get("category")
    sql = step.get("sql")
    rows = step.get("rows") or []
    rowcount = step.get("rowcount")
    
    row_sample = _truncate_rows(rows)
    
    cols = list(row_sample[0].keys()) if row_sample else []
    
    payload.append({
      "step": i,
      "category": category,
      "sql": sql,
      "rowcount": rowcount,
      "columns": cols,
      "rows_sample": row_sample,
      "total_rows": len(rows) if isinstance(rows, list) else None,
      "note": "rows_sample truncated to at most 20 rows"
    })
    
  # The summary should be generated AFTER all steps are processed.
  # This was a bug where it returned after the first step.
  chat = get_chat_model()
  msgs = _summarize_prompt(payload)
  resp = chat.invoke(msgs)
  return getattr(resp, "content", str(resp))