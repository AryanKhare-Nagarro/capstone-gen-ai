from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List
from state import DataState
import pymupdf
from tqdm import tqdm
from .tables import process_tables
from .text_chunks import process_text_chunks
from .images import process_images
from .pages import process_page_images

def pdf_handler(filePath, dataState: List[DataState]) -> List[DataState]:
    doc = pymupdf.open(filePath)
    num_pages = len(doc)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=700, chunk_overlap=200, length_function=len)

    for page_num in tqdm(range(num_pages)):
        page = doc[page_num]
        text = page.get_text()

        dataState = process_tables(filepath=filePath, page_num=page_num, dataState=dataState)
        dataState = process_text_chunks(text=text, text_splitter=text_splitter, page_num=page_num, dataState=dataState)
        dataState = process_images(page=page, page_num=page_num, dataState=dataState)
        dataState = process_page_images(page=page, page_num=page_num, dataState=dataState)

    return dataState