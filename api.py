from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
import tempfile
import shutil
import traceback
import time

app = FastAPI(title="Multimodal RAG API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables
processed_data = []
current_workflow = None
temp_db_files = []

# Create necessary directories at startup
os.makedirs("uploads", exist_ok=True)
os.makedirs("data", exist_ok=True)
os.makedirs("temp_dbs", exist_ok=True)

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    answer: str
    context: Optional[str] = None

class FileUploadResponse(BaseModel):
    message: str
    file_type: str
    data_items_count: int

@app.get("/")
async def root():
    return {"message": "Multimodal RAG API is running!"}

@app.post("/upload/", response_model=FileUploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Upload and process PDF or DB files
    """
    global processed_data, current_workflow
    
    try:
        # Create uploads directory if it doesn't exist
        os.makedirs("uploads", exist_ok=True)
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            shutil.copyfileobj(file.file, temp_file)
            temp_file_path = temp_file.name
        
        # Process file based on extension
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension == '.pdf':
            print("Processing PDF file...")
            try:
                from handle_docs.handler import pdf_handler
                initial_data_state: List[Dict[str, Any]] = []
                processed_data = pdf_handler(filePath=temp_file_path, dataState=initial_data_state)
                print(f"Processed {len(processed_data)} PDF data items")
                file_type = "PDF"
                
                # Clean up temp file immediately for PDF
                try:
                    os.unlink(temp_file_path)
                except:
                    pass  # Ignore cleanup errors for PDF
                    
            except Exception as e:
                print(f"Error importing or processing PDF: {e}")
                traceback.print_exc()
                # Clean up temp file
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
                raise HTTPException(status_code=500, detail=f"PDF processing error: {str(e)}")
            
        elif file_extension == '.db':
            print("Processing DB file...")
            try:
                from handle_sql.handler_sql import db_handler
                from database_mcp.client import mcp_client  # Fixed import path
                
                # For DB files, we need to keep the file accessible
                # Move to uploads directory for persistence
                db_filename = f"db_{os.path.basename(temp_file_path)}"
                db_file_path = os.path.join("uploads", db_filename)
                
                # Move temp file to uploads directory
                shutil.move(temp_file_path, db_file_path)
                
                # Set database path for MCP client
                mcp_client.set_database_path(db_file_path)
                processed_data = db_handler(filePath=db_file_path)
                print(f"Processed DB file with {len(processed_data)} schema chunks")
                file_type = "Database"
                
                # Keep track of DB file for later cleanup
                global temp_db_files
                temp_db_files.append(db_file_path)
                
            except Exception as e:
                print(f"Error importing or processing DB: {e}")
                traceback.print_exc()
                # Clean up temp file
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
                raise HTTPException(status_code=500, detail=f"DB processing error: {str(e)}")
            
        else:
            # Clean up temp file
            try:
                os.unlink(temp_file_path)
            except:
                pass
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_extension}")
        
        # Create workflow
        try:
            from agents.workflow import create_workflow
            current_workflow = create_workflow()
        except Exception as e:
            print(f"Error creating workflow: {e}")
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Workflow creation error: {str(e)}")
        
        return FileUploadResponse(
            message=f"Successfully processed {file.filename}",
            file_type=file_type,
            data_items_count=len(processed_data)
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@app.post("/query/", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """
    Query the processed documents or database
    """
    global processed_data, current_workflow
    
    if not processed_data or not current_workflow:
        raise HTTPException(status_code=400, detail="No file has been processed yet. Please upload a file first.")
    
    try:
        # Run workflow
        result = current_workflow.invoke({
            "user_query": request.query,
            "context_docs": "",
            "final_answer": "",
            "next": None,
            "data_items": processed_data,
            "sql_query": None
        })
        
        final_answer = result.get("final_answer", "No answer generated")
        context_docs = result.get("context_docs", "")
        
        return QueryResponse(
            answer=final_answer,
            context=context_docs
        )
        
    except Exception as e:
        print(f"Query error: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.get("/health/")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.on_event("shutdown")
async def cleanup_temp_files():
    """Clean up temporary database files on shutdown"""
    global temp_db_files
    for db_file in temp_db_files:
        try:
            if os.path.exists(db_file):
                os.unlink(db_file)
        except:
            pass  # Ignore cleanup errors
    temp_db_files = []