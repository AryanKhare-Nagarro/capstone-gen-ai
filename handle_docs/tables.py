from state import DataState
import pdfplumber
from typing import List

def process_tables(filepath, page_num, dataState: List[DataState]) -> List[DataState]:
    try:
        with pdfplumber.open(filepath) as pdf:
            page = pdf.pages[page_num]
            tables = page.extract_tables()
        
            if not tables:
                return dataState
        
            for table_index, table in enumerate(tables):
                table_text = "\n".join(
                    [" | ".join([str(cell) if cell is not None else "" for cell in row]) for row in table]
                )
                dataState.append({
                    "page": page_num,
                    "type": "table",
                    "text": table_text
                })
    
    except Exception as e:
        dataState.append({
            "page": page_num,
            "type": "error",
            "text": f"Error extracting tables: {str(e)}"
        })
    
    return dataState