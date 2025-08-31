from state import DataState
from tools.embeddings import get_embeddings, generate_multimodal_embeddings

def retriever_agent(state: DataState):
    """
    Retrieves relevant information from the vector database based on the user query.
    """
    try:
        # Get data items from state
        data_items = state.get("data_items", [])
        
        if not data_items:
            return {**state, "context_docs": "No data available for retrieval."}
        
        # Get embeddings for the data
        vector_collection = get_embeddings(dataState=data_items)
        
        user_query = state["user_query"]
        query_embedding = generate_multimodal_embeddings(prompt=user_query)
        
        if query_embedding is None:
            return {**state, "context_docs": "Failed to generate query embeddings."}
        
        # Query the vector database
        nearest_results = vector_collection.query(
            query_embeddings=query_embedding,
            n_results=min(2, len(data_items))  # Don't exceed available items
        )
        
        # Extract context
        context_docs = ""
        if hasattr(nearest_results, 'documents') and nearest_results.documents:
            if isinstance(nearest_results.documents, list):
                if len(nearest_results.documents) > 0 and isinstance(nearest_results.documents[0], list):
                    # Double nested case
                    context_docs = " ".join([item for sublist in nearest_results.documents for item in sublist])
                else:
                    # Single nested case
                    context_docs = " ".join(nearest_results.documents)
            else:
                context_docs = str(nearest_results.documents)
        else:
            # Fallback: use the raw data items
            context_docs = " ".join([item.get("text", "") for item in data_items[:3] if item.get("text")])
        
        return {**state, "context_docs": context_docs}
        
    except Exception as e:
        error_msg = f"Error in retriever agent: {str(e)}"
        return {**state, "context_docs": error_msg}