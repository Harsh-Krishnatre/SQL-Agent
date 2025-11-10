import streamlit as st
from Backend.llm import get_llm_response
from Database.database import retrieve_sql_query
import os, sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Streamlit app setup
st.set_page_config(page_title="Retrieve SQL Queries")
st.header("GENAI APP To Retrieve SQL Data")

# User input
query = st.text_input("Input: ", key="input")

# Submit button
submit = st.button("Ask the question")

# Process query on submit
if submit:
    # Get SQL query from LLM
    sql_query = get_llm_response(query)
    print(f"Generated SQL Query: {sql_query}")

    # Retrieve data from database
    result = retrieve_sql_query(sql_query.query, db=os.getenv("DB_NAME"))

    # Display results
    st.subheader("Response is:")
    if result:
        for row in result:
            st.write(row)
    else:
        st.write("No results found.")
        
