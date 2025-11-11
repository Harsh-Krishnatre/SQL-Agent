# Text-to-SQL GENAI App

This project is a web-based application that leverages Generative AI to convert natural language questions into SQL queries. It allows users to interact with a database using plain English, and it can handle both data retrieval and modification tasks.

**Deployed Project URL:** [https://sql-agent-harsh.streamlit.app/](https://sql-agent-harsh.streamlit.app/)

## Features

-   **Natural Language to SQL:** Converts complex English questions into accurate SQL queries.
-   **Query Decomposition:** Automatically breaks down multi-step requests into a sequence of smaller, executable SQL queries.
-   **Operation Classification:** Intelligently identifies the user's intent, such as `SELECT`, `INSERT`, `UPDATE`, or `DELETE`.
-   **Safety First - Destructive Operation Confirmation:** Before executing potentially harmful queries (like `DELETE` or `UPDATE`), the application prompts the user for confirmation to prevent accidental data loss.
-   **Direct Database Interaction:** Executes the generated SQL queries against the connected database.
-   **Interactive Results Display:** Displays query results in a clean, tabular format using dataframes.
-   **Natural Language Summarization:** After execution, the application provides a clear, natural language summary of the actions performed and the results obtained.

## Program Life Cycle

The application follows a structured, multi-step process to translate a user's request into a database result:

1.  **User Input:** The user enters a natural language query into the web interface (e.g., "Show me all customers from New York and then count how many there are").
2.  **Decomposition:** The backend receives the request and the `decomposer` module breaks it down into logical sub-queries.
    -   *Example:* "Show me all customers from New York" and "count how many customers there are".
3.  **Classification:** For each sub-query, an LLM classifies the intent (e.g., `SELECT`, `COUNT`).
4.  **SQL Generation:** The application feeds the sub-query, its classification, and the database schema to another LLM, which generates the precise SQL code.
5.  **Execution with Confirmation:**
    -   The generated SQL query is displayed to the user.
    -   If the operation is destructive (`INSERT`, `UPDATE`, `DELETE`), the user must explicitly confirm the action.
    -   The query is then executed against the database.
6.  **Display Results:** The results from the database are fetched and displayed in a user-friendly table.
7.  **Summarization:** A final Natural Language Generation (NLG) step creates a summary of the entire process (e.g., "First, I retrieved all customers from New York, which returned 5 results. Then, I counted the total number of customers, which is 5.").

## Technologies Used

-   **Frontend:**
    -   [Streamlit](https://streamlit.io/)
-   **Backend & AI:**
    -   [LangChain](https://www.langchain.com/) for orchestrating the AI components.
    -   [Google Generative AI](https://ai.google/) and [Hugging Face](https://huggingface.co/) for the underlying Large Language Models (LLMs).
    -   [SQLAlchemy](https://www.sqlalchemy.org/) for database interaction.
-   **Data Handling:**
    -   [Pandas](https://pandas.pydata.org/) for data manipulation and display.
