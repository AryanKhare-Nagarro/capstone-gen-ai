from typing import Dict, Any
from database_mcp.server import mcp_server

class DatabaseMCPClient:
    """
    Simplified MCP-like client for database operations.
    """
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path
        if db_path:
            mcp_server.set_database_path(db_path)
    
    def set_database_path(self, db_path: str):
        """Set database path for the client"""
        self.db_path = db_path
        mcp_server.set_database_path(db_path)
    
    def execute_query(self, sql_query: str) -> Dict[str, Any]:
        """
        Execute SQL query through server and return results.
        """
        if not sql_query:
            return {
                "success": False,
                "error": "No SQL query provided",
                "results": []
            }
        
        # Call server function
        result = mcp_server.execute_query(sql_query)
        return result
    
    def get_database_info(self) -> Dict[str, Any]:
        """
        Get database information through server.
        """
        result = mcp_server.get_database_info()
        return result

# Global client instance
mcp_client = DatabaseMCPClient()