import os
from langchain_groq import ChatGroq

def get_llm():
    # Use environment variable for API key security
    api_key = os.getenv("GROQ_API_KEY")
    
    llm = ChatGroq(
        model="llama-3.3-70b-versatile",  # Using a more standard model
        api_key=api_key
    )
    return llm
