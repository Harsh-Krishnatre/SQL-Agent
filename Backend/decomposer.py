from typing import List
from Backend.schema import Decomposition
from Backend.prompts import Prompts
from Backend.utils import get_chat_model, extract_json

DECOMPOSE_SYSTEM = Prompts.DECOMPOSE_SYSTEM

def decompose_request(natural_request: str) -> List[str]:
  chat = get_chat_model()
  msgs = [
      ("system", DECOMPOSE_SYSTEM),
      ("human", natural_request),
  ]
  resp = chat.invoke(msgs)
  content = resp.content if hasattr(resp, "content") else str(resp)

  try:
    data = extract_json(content)
    deco = Decomposition(**data)
    return deco.subqueries or [natural_request]
  
  except Exception:
        # Robust fallback when parsing fails
        return [natural_request]

