from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from core.database import Document, get_db
from core.data_processor import DataProcessor
import aiofiles

router = APIRouter()
data_processor = DataProcessor()

@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload a document for analysis"""
    try:
        # Read file content
        content = await file.read()
        content_str = content.decode('utf-8', errors='ignore')
        
        # Save to database
        doc = Document(
            filename=file.filename,
            content=content_str,
            file_type=file.content_type,
            processed=False
        )
        
        db.add(doc)
        db.commit()
        db.refresh(doc)
        
        # Process document
        processed = await data_processor.process_documents(
            [{"filename": file.filename, "content": content_str}],
            db
        )
        
        doc.processed = True
        db.commit()
        
        return {
            "status": "success",
            "document_id": doc.id,
            "filename": doc.filename,
            "processed": processed
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def list_documents(db: Session = Depends(get_db)):
    """List all uploaded documents"""
    documents = db.query(Document).all()
    return {
        "documents": [
            {
                "id": doc.id,
                "filename": doc.filename,
                "file_type": doc.file_type,
                "uploaded_at": doc.uploaded_at.isoformat() if doc.uploaded_at else None,
                "processed": doc.processed
            }
            for doc in documents
        ]
    }

@router.get("/{document_id}")
async def get_document(document_id: int, db: Session = Depends(get_db)):
    """Get a specific document"""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {
        "id": doc.id,
        "filename": doc.filename,
        "content": doc.content,
        "file_type": doc.file_type,
        "uploaded_at": doc.uploaded_at.isoformat() if doc.uploaded_at else None,
        "processed": doc.processed,
        "metadata": doc.extra_metadata
    }

