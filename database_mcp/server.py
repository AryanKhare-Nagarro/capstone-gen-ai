
import sqlite3
import json
from typing import List, Dict, Any
import os

class DatabaseMCPServer:
    """
    Simplified MCP-like server for database operations.
    """
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path
    
    def set_database_path(self, db_path: str):
        """Set the database path for this server instance"""
        self.db_path = db_path
    
    def execute_query(self, query: str) -> Dict[str, Any]:
        """
        Execute SQL query and return results.
        """
        if not self.db_path or not os.path.exists(self.db_path):
            return {
                "success": False,
                "error": "Database not found or not set",
                "results": []
            }
        
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(query)
            results = cursor.fetchall()
            
            # Convert to list of dictionaries
            rows = [dict(row) for row in results]
            
            conn.close()
            
            return {
                "success": True,
                "results": rows,
                "row_count": len(rows)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "results": []
            }
    
    def get_database_info(self) -> Dict[str, Any]:
        """
        Get database schema information.
        """
        if not self.db_path or not os.path.exists(self.db_path):
            return {
                "success": False,
                "error": "Database not found or not set",
                "tables": []
            }
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get table names
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            table_info = []
            for table in tables:
                table_name = table[0]
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = cursor.fetchall()
                column_info = [{"name": col[1], "type": col[2], "pk": bool(col[5])} for col in columns]
                table_info.append({
                    "name": table_name,
                    "columns": column_info
                })
            
            conn.close()
            
            return {
                "success": True,
                "tables": table_info
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "tables": []
            }

# Global server instance
mcp_server = DatabaseMCPServer()