import boto3
import json
import os
from typing import List, Dict, Any
from langchain_chroma import Chroma

def generate_multimodal_embeddings(prompt=None, image=None):
    try:
        # Use environment variables for security (don't hardcode credentials)
        aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        
        client = boto3.client(
            service_name="bedrock-runtime",
            region_name="us-west-2",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )
        model_id = "amazon.titan-embed-image-v1"
        body = {}

        if prompt:
            body["inputText"] = prompt
        if image:
            body["inputImage"] = image

        response = client.invoke_model(
            modelId=model_id,
            body=json.dumps(body),
            accept="application/json",
            contentType="application/json"
        )
        result = json.loads(response.get("body").read())
        return result.get("embedding")
    
    except Exception as e:
        print(f"Couldn't invoke Titan embedding model. Error: {str(e)}")
        return None
    
def get_embeddings(dataState: List[Dict[str, Any]]):
    # Ensure the directory exists
    os.makedirs("./data/chroma", exist_ok=True)
    
    vector_store = Chroma(
        collection_name="rag_collection",
        persist_directory="./data/chroma"
    )

    embeddings = []
    texts = []
    ids = []

    for i, item in enumerate(dataState):
        item_type = item.get("type", "")
        
        embedding = None
        text_content = ""
        
        if item_type in ["text", "table"]:
            text_content = item.get("text", "")
            if text_content:
                embedding = generate_multimodal_embeddings(prompt=text_content)
        elif item_type == "image":
            image_content = item.get("image", "")
            if image_content:
                embedding = generate_multimodal_embeddings(image=image_content)
        
        if embedding is not None:
            embeddings.append(embedding)
            texts.append(text_content if text_content else f"Image from page {item.get('page', 0)}")
            ids.append(str(i))

    if embeddings and texts and ids:
        try:
            vector_store._collection.add(
                ids=ids,
                documents=texts,
                embeddings=embeddings
            )
        except Exception as e:
            print(f"Error adding to vector store: {e}")

    return vector_store._collection

def get_sql_embeddings(chunks):
    chunk_embeddings = []
    
    for chunk in chunks:
        result = generate_multimodal_embeddings(prompt=chunk)
        chunk_embeddings.append(result)

    ids = [str(i) for i in range(0, len(chunk_embeddings))]
    
    vector_store = Chroma(
        collection_name="rag_collection",
        persist_directory="./data/chroma"
    )

    vector_store._collection.add(
        ids=ids,
        documents=chunks,
        embeddings=chunk_embeddings
    )

    return vector_store._collection