from state import DataState
from tools.llm import get_llm

def presenter_agent(state: DataState):
    """
    The presenter agent's role is to take the intermediate results 
    (from retriever_agent) and craft a final, well-formatted 
    response for the end user.
    """

    user_query = state.get("user_query", "")
    retrieved_info = state.get("context_docs", "")

    llm = get_llm()

    presenter_prompt = f"""
    You are a presenter agent.
    Your job is to generate a clear, concise, and helpful final answer 
    for the user based on the information retrieved from the document.

    - Summarize the retrieved information clearly and concisely
    - Make the response human-friendly (like a helpful assistant)
    - Focus on answering the user's specific query
    - If the information is not available, say so politely

    --------------------------------------------
    User Query: {user_query}

    Retrieved Info: {retrieved_info}
    --------------------------------------------

    Final Answer:
    """

    try:
        response = llm.invoke(presenter_prompt)
        final_answer = response.content if hasattr(response, 'content') else str(response)
    except Exception as e:
        final_answer = f"Error generating final answer: {str(e)}"

    return {**state, "final_answer": final_answer}