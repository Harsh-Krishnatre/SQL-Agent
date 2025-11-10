import sqlite3

def retrieve_sql_query(sql, db):
  """
  Executes a SQL query on the specified database and returns the results.

  Args:
    sql (str): The SQL query to execute.
    db (str): The path to the SQLite database file.

  Returns:
    list: A list of tuples representing the rows returned by the query.
  """
  conn = sqlite3.connect(db)
  cursor = conn.cursor()
  cursor.execute(sql)
  rows = cursor.fetchall()
  conn.commit()
  conn.close()
  return rows
