from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
from Backend.schema import Category, Query
from Backend.prompts import Prompts
import json

load_dotenv()


def _get_chat_model():
    """
    Initializes and returns a ChatHuggingFace model connected to a Hugging Face Endpoint.

    This function sets up a connection to a specified Llama-3.1-8B-Instruct model
    on the Hugging Face platform, configuring it with a temperature of 0.3 and
    a maximum of 1024 new tokens for generation.

    Returns:
        ChatHuggingFace: An initialized ChatHuggingFace model instance.
    """

    endpoint = HuggingFaceEndpoint(
        repo_id="meta-llama/Llama-3.1-8B-Instruct",
        temperature=0.3,
        max_new_tokens=1024,
    )
    chat_model = ChatHuggingFace(llm=endpoint, verbose=True)
    return chat_model


def _extract_json(text: str) -> dict:
    """Extract JSON from model output, handling markdown code blocks."""
    text = text.strip()
    
    # Remove markdown code blocks if present
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0].strip()
    elif "```" in text:
        text = text.split("```")[1].split("```")[0].strip()
    
    # Find JSON object in text
    start_idx = text.find("{")
    end_idx = text.rfind("}") + 1
    
    if start_idx != -1 and end_idx > start_idx:
        json_str = text[start_idx:end_idx]
        return json.loads(json_str)
    
    # If no braces found, try parsing the whole text
    return json.loads(text)

def classify_operation(natural_request: str) -> Category:
    chat = _get_chat_model()
    msgs = [
        ("system", Prompts.INTENT_SYSTEM_PROMPT),
        ("human", natural_request),
    ]
    
    response = chat.invoke(msgs)
    content = response.content if hasattr(response, 'content') else str(response)

    try:
        json_data = _extract_json(content)
        return Category(**json_data)
    except json.JSONDecodeError:
        print(f"Error parsing category response: {content}")

def generate_sql(natural_request: str, category: Category) -> Query:
    chat = _get_chat_model()
    
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
        json_data = _extract_json(content)
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
    
    operation = classify_operation(request)
    result = generate_sql(request, operation)
    
    return result
