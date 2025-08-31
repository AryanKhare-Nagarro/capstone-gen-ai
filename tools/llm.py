import os
from langchain_groq import ChatGroq

def get_llm():
    # Use environment variable for API key security
    api_key = os.getenv("GROQ_API_KEY")
    
    llm = ChatGroq(
        model="llama3-8b-8192",  # Using a more standard model
        api_key=api_key
    )
    return llm