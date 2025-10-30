"""
Document Management Router
API endpoints for document upload, processing, and management.
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query
from typing import List, Optional
import uuid

from ..document_processor import DocumentProcessor
from ..config import Settings

# Create router
router = APIRouter(prefix="/documents", tags=["documents"])

# Initialize document processor
config = Settings()
doc_processor = DocumentProcessor(config)


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    user_id: Optional[str] = Query(None, description="User ID for personal vector store")
):
    """
    Upload and process a document (PDF, DOCX, TXT, MD).
    Creates chunks and adds to vector store for RAG functionality.
    """
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")
    
    # Generate user_id if not provided
    if not user_id:
        user_id = str(uuid.uuid4())
    
    result = await doc_processor.process_and_store_document(file, user_id)
    result["user_id"] = user_id
    
    return result


@router.get("/list/{user_id}")
async def list_user_documents(user_id: str):
    """
    List all documents in a user's personal vector store.
    """
    documents = doc_processor.list_user_documents(user_id)
    return {
        "user_id": user_id,
        "documents": documents,
        "total_documents": len(documents)
    }


@router.delete("/{user_id}/{document_name}")
async def delete_document(user_id: str, document_name: str):
    """
    Delete a specific document from user's vector store.
    """
    result = doc_processor.delete_user_document(user_id, document_name)
    return result


@router.post("/upload-multiple")
async def upload_multiple_documents(
    files: List[UploadFile] = File(...),
    user_id: Optional[str] = Query(None, description="User ID for personal vector store")
):
    """
    Upload and process multiple documents at once.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    # Generate user_id if not provided
    if not user_id:
        user_id = str(uuid.uuid4())
    
    results = []
    for file in files:
        try:
            result = await doc_processor.process_and_store_document(file, user_id)
            result["user_id"] = user_id
            results.append(result)
        except Exception as e:
            results.append({
                "status": "error",
                "document_name": file.filename,
                "error": str(e)
            })
    
    successful_uploads = [r for r in results if r.get("status") == "success"]
    failed_uploads = [r for r in results if r.get("status") == "error"]
    
    return {
        "user_id": user_id,
        "total_files": len(files),
        "successful_uploads": len(successful_uploads),
        "failed_uploads": len(failed_uploads),
        "results": results
    }


@router.get("/vectorstore/info/{user_id}")
async def get_vectorstore_info(user_id: str):
    """
    Get information about user's vector store.
    """
    try:
        documents = doc_processor.list_user_documents(user_id)
        
        total_chunks = sum(doc.get("chunks", 0) for doc in documents)
        
        return {
            "user_id": user_id,
            "total_documents": len(documents),
            "total_chunks": total_chunks,
            "documents": documents,
            "status": "exists" if documents else "empty"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting vectorstore info: {str(e)}")


@router.post("/clear/{user_id}")
async def clear_user_vectorstore(user_id: str):
    """
    Clear all documents from user's vector store.
    """
    try:
        import shutil
        from pathlib import Path
        
        user_vectorstore_path = Path(f"data/user_vectorstores/{user_id}")
        
        if user_vectorstore_path.exists():
            shutil.rmtree(user_vectorstore_path)
            return {
                "status": "success",
                "message": f"Cleared all documents for user {user_id}"
            }
        else:
            return {
                "status": "success",
                "message": f"No vector store found for user {user_id}"
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing vectorstore: {str(e)}")