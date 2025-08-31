from handle_docs.handler import pdf_handler
from handle_sql.handler_sql import db_handler
import os
from agents.workflow import create_workflow
from database_mcp.client import mcp_client
from typing import List, Dict, Any

def get_file_extension(filepath: str) -> str:
    """Get file extension from filepath"""
    return os.path.splitext(filepath)[1].lower()

def process_file(filepath: str) -> List[Dict[str, Any]]:
    """Process file based on its extension"""
    file_extension = get_file_extension(filepath)
    
    if file_extension == '.pdf':
        print("Processing PDF file...")
        initial_data_state: List[Dict[str, Any]] = []
        processed_data = pdf_handler(filePath=filepath, dataState=initial_data_state)
        print(f"Processed {len(processed_data)} PDF data items")
        return processed_data
    
    elif file_extension == '.db':
        print("Processing DB file...")
        # Set database path for MCP client
        mcp_client.set_database_path(filepath)
        processed_data = db_handler(filePath=filepath)
        print(f"Processed DB file with {len(processed_data)} schema chunks")
        return processed_data
    
    else:
        raise ValueError(f"Unsupported file type: {file_extension}")

if __name__ == "__main__":
    try:
        base_dir = os.path.dirname(__file__)
        
        # Test with PDF file
        # filepath = os.path.join(base_dir, "attention.pdf")
        
        # Or test with DB file (uncomment below line and comment above line)
        filepath = os.path.join(base_dir, "sakila_master.db")
        
        # Check if file exists
        if not os.path.exists(filepath):
            print(f"Error: File not found at {filepath}")
            exit(1)

        # Process file based on extension
        processed_data = process_file(filepath)

        # Create workflow with proper state
        print("Creating workflow...")
        workflow = create_workflow()
        
        # Run workflow
        print("Running workflow...")
        
        # Different query based on file type
        if get_file_extension(filepath) == '.pdf':
            user_query = "What is the transformer-model architecture?"
        else:
            user_query = "Find the actor who worked in highest number of movies"
        
        result = workflow.invoke({
            "user_query": user_query,
            "context_docs": "",
            "final_answer": "",
            "next": None,
            "data_items": processed_data,
            "sql_query": None  # Added for SQL workflow
        })

        print("\nFinal Answer:")
        print(result.get("final_answer", "No answer generated"))
        
    except Exception as e:
        print(f"Error running application: {e}")
        import traceback
        traceback.print_exc()