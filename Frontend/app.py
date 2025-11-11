import os, sys, streamlit as st, pandas as pd
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from Backend.llm import get_llm_response
from Database.database import retrieve_sql_query
from Backend.nlp import summarize_nlg


# Streamlit app setup
st.set_page_config(page_title="Retrieve SQL Queries",layout='wide')
st.header("GENAI APP To Retrieve SQL Data")

# User input
query = st.text_input("Input: ", key="input")

# Submit button
submit = st.button("Generate")

# Process query on submit
if submit:
    if not query.strip():
        st.warning("Please enter a query.")
        st.stop()
    # Get SQL query from LLM
    try:
        result = get_llm_response(query)
    except Exception as e:
        st.error(f"LLM error: {e}")
        st.stop()
    
    sql_queries = result if isinstance(result, list) else [result]
    
    print(sql_queries)
    
    db_name = os.getenv("DB_NAME")
    
    if not db_name:
        st.info("Environment variable DB_NAME is not set. Using default DB configuration (if any).")

    st.subheader("Generated Results:")
    
    steps_summary = []
    for i, q in enumerate(sql_queries, start=1):
        # q is a Pydantic Query model: has .query and .category
        st.markdown(f"#### Step {i} — `{q.category}` Operation")
        st.code(q.query, language="sql")

        # --- Confirmation for Destructive Operations ---
        destructive_categories = ["DELETE", "UPDATE", "INSERT", "DDL"]
        is_destructive = q.category in destructive_categories
        proceed = True

        if is_destructive:
            st.warning(f"**Warning:** This is a potentially destructive `{q.category}` operation.")
            # Use a unique key for the button inside the loop
            if not st.button(f"Confirm and Execute Step {i}", key=f"confirm_{i}"):
                proceed = False
        
        if not proceed:
            st.info("Execution skipped by user.")
            continue # Move to the next query in the list
        # --- End of Confirmation Logic ---

        try:
            rows = retrieve_sql_query(q.query, db=db_name)
        except Exception as e:
            st.error(f"Execution error on Step {i}: {e}")
            rows = []
        
        if rows:
            # Prefer list-of-dicts for nice headers
            if isinstance(rows, list) and isinstance(rows[0], dict):
                df = pd.DataFrame(rows)
                st.dataframe(df, use_container_width=True)
            else:
                # Fallback: show whatever came back (e.g., message dicts/strings)
                st.write(rows)
        else:
            st.write("_No results returned._")
            
        steps_summary.append({
            "category": getattr(q, "category", None),
            "sql": getattr(q, "query", None),
            "rows": rows if isinstance(rows, list) and (not rows or isinstance(rows[0], dict)) else [],
            "rowcount": None,  # populate if your DB layer returns affected row counts
        })
        
    if steps_summary:
        st.subheader("Summary (Natural Language)")
        try:
            summary_text = summarize_nlg(steps_summary)
            st.write(summary_text)
        except Exception as e:
            st.error(f"NLG summary error: {e}")

        
