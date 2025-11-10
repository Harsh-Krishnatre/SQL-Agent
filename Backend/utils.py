import json
from langchain_huggingface import ChatHuggingFace, HuggingFaceEndpoint
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