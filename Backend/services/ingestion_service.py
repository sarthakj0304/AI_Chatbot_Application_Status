import os
import threading
import shutil

from utils.file_parsers import parse_file 
from database.db_manager import get_db, Document
from services.indexing_service import indexing_service
from sqlalchemy.orm import Session
from fastapi import UploadFile, File, status, HTTPException, BackgroundTasks
from tasks import process_document_task

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)



def handle_upload(file : UploadFile, db : Session):

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    
    
    db_doc = Document(filename=file.filename, status="queued")
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    
    # we store the document locally temporarily 
    try:
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {str(e)}"
        )
    
    # the celery broker sends the task to the redis queue using the delay function from which it will be consumed by the celery worker
    process_document_task.delay(db_doc.id, filepath)
    
    
    
    # 4. Return immediately to the user (Takes less than 5 milliseconds!)
    return {
        "message": "File received safely! Processing started in the background.",
        "document_id": db_doc.id,
        "status": "queued"
    }
