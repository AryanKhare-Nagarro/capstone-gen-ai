from typing import List, Optional, Dict, Any
from typing_extensions import TypedDict

class DataState(TypedDict):
    user_query: str
    context_docs: Optional[str]
    final_answer: Optional[str]
    next: Optional[str]
    data_items: List[Dict[str, Any]]
    sql_query: Optional[str]  # Added for SQL workflow