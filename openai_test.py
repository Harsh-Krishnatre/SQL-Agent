from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

model = ChatOpenAI(
  model="gpt-4.1-2025-04-14",
  temperature=0.3,
  max_tokens=1024
)
prompt = "write a short note of numbers"
result = model.invoke(prompt)
print(result)

query = "Write a short note on culture"

model.invoke(query)