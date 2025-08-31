from state import DataState
from tools.embeddings import get_sql_embeddings, generate_multimodal_embeddings
from tools.llm import get_llm
import sqlite3
import os
from typing import List, Dict, Any

def sql_retriever_agent(state: DataState):
    """
    Retrieves relevant database schema information and generates SQL queries.
    """
    try:
        # Get data items from state (should contain schema information)
        data_items = state.get("data_items", [])
        
        if not data_items:
            return {**state, "context_docs": "No database schema available for query generation."}
        
        # Filter for schema data only
        schema_items = [item for item in data_items if item.get("type") == "schema"]
        
        if not schema_items:
            return {**state, "context_docs": "No database schema information found."}
        
        # Extract schema texts for embedding
        schema_texts = [item.get("text", "") for item in schema_items if item.get("text")]
        
        if not schema_texts:
            return {**state, "context_docs": "No valid schema text found for processing."}
        
        # Get embeddings for the schema data
        vector_collection = get_sql_embeddings(schema_texts)
        
        user_query = state["user_query"]
        query_embedding = generate_multimodal_embeddings(prompt=user_query)
        
        if query_embedding is None:
            return {**state, "context_docs": "Failed to generate query embeddings."}
        
        # Query the vector database to find relevant schema chunks
        nearest_results = vector_collection.query(
            query_embeddings=query_embedding,
            n_results=min(2, len(schema_texts))
        )
        
        # Extract relevant schema information
        relevant_schema = ""
        if hasattr(nearest_results, 'documents') and nearest_results.documents:
            if isinstance(nearest_results.documents, list):
                if len(nearest_results.documents) > 0:
                    if isinstance(nearest_results.documents[0], list):
                        # Double nested case
                        relevant_schema = "\n\n".join([item for sublist in nearest_results.documents for item in sublist])
                    else:
                        # Single nested case
                        relevant_schema = "\n\n".join(nearest_results.documents)
                else:
                    # Fallback to all schema data
                    relevant_schema = "\n\n".join(schema_texts[:2])
            else:
                relevant_schema = str(nearest_results.documents)
        else:
            # Fallback to all schema data
            relevant_schema = "\n\n".join(schema_texts[:2])
        
        # Generate SQL query using LLM
        sql_query = generate_sql_query(user_query, relevant_schema)
        
        if sql_query and not sql_query.startswith("ERROR"):
            # Store both the schema context and generated SQL
            context_with_sql = f"Relevant Schema:\n{relevant_schema}\n\nGenerated SQL Query:\n{sql_query}"
            return {**state, "context_docs": context_with_sql, "sql_query": sql_query}
        else:
            # If SQL generation failed, pass the schema context for presentation
            error_context = f"Relevant Schema Information:\n{relevant_schema}\n\nNote: Unable to generate SQL query automatically."
            return {**state, "context_docs": error_context, "sql_query": None}
        
    except Exception as e:
        error_msg = f"Error in SQL retriever agent: {str(e)}"
        return {**state, "context_docs": error_msg, "sql_query": None}

def generate_sql_query(user_query: str, schema_info: str) -> str:
    """
    Generate SQL query based on user question and schema information.
    """
    try:
        llm = get_llm()
        
        sql_prompt = f"""
        You are a SQLite expert. Generate a valid SQLite query based on the user question and database schema.
        
        Database Schema:
        {schema_info}
        
        Rules:
        1. Generate only valid SQLite syntax
        2. Return ONLY the SQL query, nothing else
        3. Make sure table and column names match exactly from the schema
        4. Handle potential NULL values appropriately
        5. Always limit results to reasonable number (max 50 rows) unless specifically asked
        6. If the query cannot be answered with available schema, return: "SELECT 'Insufficient schema information to generate query' AS result;"
        7. Never return explanations, only the SQLite query
        
        User Query: {user_query}
        
        SQLite Query:
        """
        
        response = llm.invoke(sql_prompt)
        sql_query = response.content.strip()
        
        # Basic validation - ensure it's a SELECT statement or valid SQL
        if sql_query.upper().startswith('SELECT') or sql_query.upper().startswith('PRAGMA'):
            return sql_query
        else:
            return f"SELECT 'Generated query is not a valid SELECT statement: {sql_query}' AS result;"
            
    except Exception as e:
        return f"ERROR: Failed to generate SQL query - {str(e)}"