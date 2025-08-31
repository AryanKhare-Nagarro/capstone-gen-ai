from typing import List, Dict, Any

def db_handler(filePath: str) -> List[Dict[str, Any]]:
    """
    Handle DB file processing and return structured data for the workflow
    """
    try:
        # Convert file path to SQLite URI format
        db_uri = f"sqlite:///{filePath}"
        
        # Import here to avoid circular imports
        from handle_sql.table_info import get_table_info
        from handle_sql.table_chunk import table_chunks
        
        # Initialize empty state (we'll create a minimal state for get_table_info)
        state = {}  # This can be expanded if needed
        
        # Get table information
        table_info = get_table_info(db_uri, state)
        
        # Chunk the table information
        schema_chunks = table_chunks(table_info)
        
        # Convert chunks to the format expected by the workflow
        data_items = []
        for i, chunk in enumerate(schema_chunks):
            data_items.append({
                "page": i,  # Using page as chunk index
                "type": "schema",
                "text": chunk,
                "embeddings": None
            })
        
        return data_items
        
    except Exception as e:
        print(f"Error processing DB file: {e}")
        import traceback
        traceback.print_exc()
        # Return empty data state in case of error
        return [{
            "page": 0,
            "type": "error",
            "text": f"Error processing database: {str(e)}",
            "embeddings": None
        }]