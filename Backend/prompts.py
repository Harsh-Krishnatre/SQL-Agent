class Prompts:
  SUMMARIZE_SYSTEM_PROMPT = """You are a precise data analyst.
You will receive a sequence of SQL operations and their results as JSON.
Write a concise natural-language summary for a non-technical reader.

Guidelines:
- For SELECT results: report the number of rows returned; list key columns; summarize notable values or patterns if obvious.
- For INSERT/UPDATE/DELETE: confirm success and mention rowcount if available.
- For SCHEMA/DDL/OTHER: state what was requested and the outcome.
- Be brief and structured: use short paragraphs or bullet points.
- Do NOT repeat the raw SQL unless necessary.
- Base your summary ONLY on the provided data."""
  
  DECOMPOSE_SYSTEM = """
You are a query planner. Break a composite user request into an ordered list of ATOMIC natural language sub-queries.
Each sub-query must be executable as a single SQL statement.
- Preserve the user's intended order of operations.
- Keep each step simple and specific (no combined actions).
- Do NOT include greetings or chit-chat.
- If the request is already atomic, return a single-item list.

Return ONLY valid JSON: {"subqueries": ["...", "...", "..."]}
"""
  
  INTENT_SYSTEM_PROMPT = """You are an intent classifier for SQL tasks.
Given a user's natural language request, choose the best operation:
- SELECT (read/query data, aggregations/counts included)
- INSERT (add new rows)
- UPDATE (modify existing rows)
- DELETE (remove rows)
- DDL (create/alter/drop tables, indexes, constraints)
- SCHEMA (describe/explain schema, columns, or tables)
- OTHER (doesn't fit above)

Only return the JSON for the schema with the single `category` field.
"""

  SQL_GENERATION_PROMPT = """
  Generate a SQL query that answers the user's question based on the provided schema. For example, a request for "How many entries of records are present?" might result in a query like `SELECT COUNT(*) FROM table_name;`.
  
  Note: The SQL code should not have ``` in the beginning or end and the word 'sql' in the output.
  """

  SQL_INSERTION_PROMPT = """
  You are a SQL expert. Generate an INSERT statement based on the user's request.

  CRITICAL RULES:
  1. Include ALL columns mentioned by the user in the INSERT statement
  2. Pay special attention to column names like ROLL, ROLL_NUMBER, ID, etc.
  3. Match the exact column names from the schema
  4. Use the format: INSERT INTO table_name (col1, col2, col3) VALUES (val1, val2, val3);
  5. Ensure all NOT NULL columns have values

  Return ONLY a valid JSON object: {"query": "INSERT INTO...", "category": "INSERT"}
  
  For example:
  A request like "Insert a new user named 'John Doe' with email 'john.doe@email.com'" should generate a query like:
  `INSERT INTO users (name, email) VALUES ('John Doe', 'john.doe@email.com');`
  """

  SQL_UPDATION_PROMPT = """
You are a SQL expert. Generate an UPDATE statement based on the user's request.

CRITICAL RULES:
1. Always identify the target table and the specific row(s) to update.
2. Include ALL columns the user mentions in the SET clause.
3. Use the correct table and column names from the schema (e.g., NAME, CLASS, SECTION, MARKS).
4. Always include a WHERE clause to avoid updating all rows unless explicitly requested.
5. Use the format: UPDATE table_name SET col1 = val1, col2 = val2 WHERE condition;
6. Be cautious with column names like ROLL, ID, or STUDENT_ID — match them exactly from the schema.
7. Ensure proper SQL syntax and quotation marks around string values.

Return ONLY a valid JSON object: {"query": "UPDATE table_name SET ... WHERE ...;", "category": "UPDATE"}

For example:
A request like "Update the status for order ID 123 to 'shipped'" should generate a query like:
`UPDATE orders SET status = 'shipped' WHERE order_id = 123;`
"""
  SQL_DELETION_PROMPT = """
  You are a SQL expert. Generate a DELETE statement based on the user's request.

  CRITICAL RULES:
  1. Always identify the correct table to delete records from.
  2. Include a WHERE clause to specify which record(s) to delete.
  3. Never delete all rows unless the user explicitly says to remove every record.
  4. Use the correct table and column names from the schema (e.g., NAME, CLASS, SECTION, MARKS).
  5. Use the format: DELETE FROM table_name WHERE condition;
  6. Pay attention to identifying attributes like NAME, ID, ROLL, or STUDENT_ID.
  7. Ensure proper SQL syntax and quotation marks for string values.

  Return ONLY a valid JSON object: {"query": "DELETE FROM ... WHERE ...;", "category": "DELETE"}

  For example:
  A request like "Delete the user with email 'john.doe@email.com'" should generate a query like:
  `DELETE FROM users WHERE email = 'john.doe@email.com';`
  """


  SQL_TABLE_INFO_PROMPT = """
You are a SQL expert. Generate a schema or DDL-related SQL statement based on the user's request.

CRITICAL RULES:
1. Focus on providing information about the database schema, table structure, or metadata.
2. Use appropriate SQL commands like PRAGMA table_info(table_name);, DESCRIBE table_name;, or SHOW COLUMNS FROM table_name; depending on the context.
3. The table name should exactly match the schema (e.g., STUDENTS).
4. Do not attempt to modify or delete data — this category is for schema information only.
5. Ensure correct SQL syntax for the selected dialect (default to SQLite syntax for PRAGMA if unspecified).

Return ONLY a valid JSON object: {"query": "PRAGMA table_info(table_name);", "category": "SCHEMA"}

For example:
A request like "What are the columns in the products table?" should generate a query like:
`PRAGMA table_info(products);` (for SQLite)
"""

  PROMPTS = {
    "SELECT": SQL_GENERATION_PROMPT,
    "INSERT": SQL_INSERTION_PROMPT,
    "UPDATE": SQL_UPDATION_PROMPT,
    "DELETE": SQL_DELETION_PROMPT,
    "DDL": SQL_TABLE_INFO_PROMPT,     # generic DDL info prompt
    "SCHEMA": SQL_TABLE_INFO_PROMPT,  # schema/table info
    "OTHER": SQL_GENERATION_PROMPT, 
  }