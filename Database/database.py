from sqlalchemy import create_engine, text
import traceback

def retrieve_sql_query(sql: str, db: str):
    """
    Executes a SQL query and returns results as a list of dictionaries
    with proper column names. Works for both read (SELECT) and write operations.
    """
    try:
        db_url = f"sqlite:///{db}" if not db.startswith("sqlite:///") else db
        engine = create_engine(db_url)

        with engine.connect() as conn:
            sql_upper = sql.strip().split()[0].upper()

            # DML: autocommit in a transaction
            if sql_upper in {"INSERT", "UPDATE", "DELETE"}:
                with conn.begin():
                    conn.execute(text(sql))
                return [{"message": f"{sql_upper} executed successfully"}]

            # SELECT (or other statements that return rows)
            result = conn.execute(text(sql))

            if not result.returns_rows:
                # e.g., PRAGMA without result set
                return [{"message": "Statement executed successfully (no rows)"}]

            # ✅ Return dicts with real column names
            # This is the key change
            data = [dict(row) for row in result.mappings().all()]
            return data

    except Exception as e:
        print("Database error:", e)
        traceback.print_exc()
        return []
