from Backend.schema import Category, Query
from Backend.prompts import Prompts
from Backend.decomposer import decompose_request
from Backend.utils import extract_json, get_chat_model
import json
from typing import List


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
    
    system_prompt = Prompts.PROMPTS.get(category.category, Prompts.PROMPTS["OTHER"])
    system_prompt += "\n\nReturn ONLY a valid JSON object with two fields: 'query' (the SQL statement) and 'category' (the operation type)."
    system_prompt += '\nExample: {"query": "SELECT * FROM users;", "category": "SELECT"}'
    
    msgs = [
        ("system", system_prompt),
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
