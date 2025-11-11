from Backend.schema import Category, Query
from Backend.prompts import Prompts
from Database.database import get_db_schema
from Backend.decomposer import decompose_request
from Backend.utils import extract_json, get_chat_model
import json
from typing import List
import os

def classify_operation(natural_request: str) -> Category:
    chat = get_chat_model()
    msgs = [
        ("system", Prompts.INTENT_SYSTEM_PROMPT),
        ("human", natural_request),
    ]
    
    response = chat.invoke(msgs)
    content = response.content if hasattr(response, 'content') else str(response)

    try:
        json_data = extract_json(content)
        return Category(**json_data)
    except json.JSONDecodeError:
        # Bubble up with context so caller can fail or fallback
        raise ValueError(f"Could not parse category JSON: {content!r}")

def generate_sql(natural_request: str, category: Category) -> Query:
    chat = get_chat_model()
    db_name = os.getenv("DB_NAME")
    if not db_name:
        raise ValueError("DB_NAME environment variable not set.")

    db_schema = get_db_schema(db_name)
    
    system_prompt = Prompts.PROMPTS.get(category.category, Prompts.PROMPTS["OTHER"])
    full_prompt = (
        f"You are an expert in converting English questions to SQL queries.\n"
        f"Database Schema:\n{db_schema}\n\n{system_prompt}\n\n"
        f"Return ONLY a valid JSON object with two fields: 'query' (the SQL statement) and 'category' (the operation type)."
    )
    
    msgs = [
        ("system", full_prompt),
        ("human", f"Request: {natural_request}\n"),
    ]
    response = chat.invoke(msgs)
    content = response.content if hasattr(response, 'content') else str(response)
    try:
        json_data = extract_json(content)
        return Query(**json_data)
    except Exception as e:
        print(f"Error parsing SQL response: {content}")
        raise e

def get_llm_response(request):
    """
    Sends a query and a prompt to the configured Hugging Face language model 
    and returns the model's response.

    Args:
        request (str): The user's natural language query.

    Returns:
        str: The content of the model's response.
    """
    subqueries = decompose_request(request)
    results: List[Query] = []
    for req in subqueries:
        op = classify_operation(req)
        q = generate_sql(req, op)
        results.append(q)
        
    return results
