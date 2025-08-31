from typing import List
from state import DataState

def process_text_chunks(text, text_splitter, page_num, dataState: List[DataState]) -> List[DataState]:
    chunks = text_splitter.split_text(text)
    for i, chunk in enumerate(chunks):
        dataState.append({
            "page": page_num,
            "type": "text",
            "text": chunk
        })    
    return dataState