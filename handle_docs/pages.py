from state import DataState
from typing import List
import base64

def process_page_images(page, page_num, dataState: List[DataState]) -> List[DataState]:
    pix = page.get_pixmap()
    page_bytes = pix.tobytes("png")
    encoded_page = base64.b64encode(page_bytes).decode("utf-8")
    dataState.append({
            "page": page_num,
            "type": "page",
            "image": encoded_page
        })
    return dataState