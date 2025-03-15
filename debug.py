from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import os

load_dotenv()

with open("debug_output.txt", "w") as f:
    try:
        f.write(f"OPENAI_API_KEY present: {bool(os.getenv('OPENAI_API_KEY'))}\n")
        llm = ChatOpenAI(model="gpt-4o")
        f.write(f"LLM initialized successfully: {llm}\n")
    except Exception as e:
        f.write(f"Error initializing LLM: {str(e)}\n") 