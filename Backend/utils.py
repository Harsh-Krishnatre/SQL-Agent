import json
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

def extract_json(text: str) -> dict:
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
  

def get_chat_model():
    """
    Initializes and returns a ChatGoogleGenerativeAI model instance.

    Returns:
        ChatGoogleGenerativeAI: An instance of the Gemini 2.5 Flash model.
    """
    
    chat_model = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
    return chat_model