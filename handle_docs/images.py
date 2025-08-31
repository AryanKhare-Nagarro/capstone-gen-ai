from typing import List
from state import DataState
import base64
import fitz

def process_images(page, page_num, dataState: List[DataState]) -> List[DataState]:
    images = page.get_images()
    
    for index, image in enumerate(images):
        xref = image[0]
        pix = fitz.Pixmap(page.parent, xref)
        img_bytes = pix.tobytes("png")
        encoded_image = base64.b64encode(img_bytes).decode("utf-8")
        
        dataState.append({
            "page": page_num,
            "type": "image",
            "image": encoded_image
        })
    return dataState