from state import DataState
from tools.llm import get_llm

def supervisor_agent(state: DataState):
    user_query = state["user_query"]
    
    # Check if we're dealing with DB data (check data_items for schema type)
    data_items = state.get("data_items", [])
    has_schema_data = any(item.get("type") == "schema" for item in data_items)
    has_pdf_data = any(item.get("type") in ["text", "table", "image"] for item in data_items)
    
    supervisor_prompt = f"""
    You are a supervisor agent responsible for routing user queries in a multimodal system.
    Your job:
    1. Decide whether to send the query to a specialized agent.
    2. Choose only ONE option from the list below.
    3. Output the decision as a **single word** ONLY (no extra explanation).

    Available agents:
    - retriever_agent : retrieve relevant information from PDF documents using vector search.
    - sql_retriever_agent : handle database queries and generate SQL statements.
    - presenter_agent : format or finalize the data for user presentation.

    Context Information:
    - Schema/Database data available: {has_schema_data}
    - PDF document data available: {has_pdf_data}

    Routing Logic:
    - If the query is about database structure, tables, SQL operations, or data extraction AND schema data is available, choose sql_retriever_agent
    - If the query is about PDF content, document text, images, or general information, choose retriever_agent
    - If the query is about formatting, summarizing, or final presentation, choose presenter_agent

    Examples:
    User Query: "What is the transformer architecture in the paper?" (PDF content)
    Output: retriever_agent

    User Query: "Show me all customers from USA" (Database query)
    Output: sql_retriever_agent

    User Query: "List all tables and their columns" (Database schema)
    Output: sql_retriever_agent

    User Query: "Format this information as a report"
    Output: presenter_agent

    User Query: "Find all records where salary > 50000" (Database query)
    Output: sql_retriever_agent

    User Query: {user_query}
    Output:
    """

    llm = get_llm()
    response = llm.invoke(supervisor_prompt)
    
    # Clean the response to ensure it's a single word
    next_agent = response.content.strip().split()[0] if response.content.strip() else "retriever_agent"
    
    # Validate the agent name
    valid_agents = ["retriever_agent", "sql_retriever_agent", "presenter_agent"]
    if next_agent not in valid_agents:
        # Smart fallback based on data type and query keywords
        db_keywords = ["table", "database", "select", "query", "sql", "row", "column", "data", "record"]
        pdf_keywords = ["document", "paper", "text", "image", "page", "paragraph", "section"]
        
        user_query_lower = user_query.lower()
        has_db_keywords = any(keyword in user_query_lower for keyword in db_keywords)
        has_pdf_keywords = any(keyword in user_query_lower for keyword in pdf_keywords)
        
        if has_schema_data and has_db_keywords and not has_pdf_keywords:
            next_agent = "sql_retriever_agent"
        elif has_pdf_data and has_pdf_keywords:
            next_agent = "retriever_agent"
        else:
            # Default fallback
            next_agent = "retriever_agent"
    
    return {**state, "next": next_agent}