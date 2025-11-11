from sqlalchemy import create_engine, text, inspect
import traceback,os

def get_db_connection(db_name=None):
    db_path = db_name or os.getenv("DB_NAME")
    if not db_path:
        raise ValueError("Database name not provided and DB_NAME environment variable is not set.")
    db_url = f"sqlite:///{db_path}" if not db_path.startswith("sqlite:///") else db_path
    return create_engine(db_url)

def get_db_schema(db: str) -> str:
    """
    Retrieves the schema of all tables in the database as a string of CREATE TABLE statements.
    """
    engine = get_db_connection(db)
    schema_str = ""
    
    # For SQLite, we can directly query the master table to get the CREATE statements,
    # which is very convenient for LLMs.
    if engine.dialect.name == 'sqlite':
        with engine.connect() as connection:
            query = "SELECT sql FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';"
            tables_sql = connection.execute(text(query)).fetchall()
            for (table_sql,) in tables_sql:
                schema_str += f"{table_sql};\n\n"
    return schema_str

def retrieve_sql_query(sql: str, db: str):
    """
    Executes a SQL query and returns results as a list of dictionaries
    with proper column names. Works for both read (SELECT) and write operations.
    """
    try:
        engine = get_db_connection(db)

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

            # This is the key change
            data = [dict(row) for row in result.mappings().all()]
            return data

    except Exception as e:
        print("Database error:", e)
        traceback.print_exc()
        raise  # Re-raise the exception to be handled by the frontend
