import os
import threading
from werkzeug.utils import secure_filename
from utils.file_parsers import parse_file
from database.db_manager import insert_document, update_document_status
from services.indexing_service import indexing_service

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def process_file_background(doc_id, filepath):
    try:
        update_document_status(doc_id, 'processing')
        # Extract text
        text = parse_file(filepath)
        
        # Index document
        if text.strip():
            indexing_service.index_document(doc_id, text)
        else:
            update_document_status(doc_id, 'failed')
            
    except Exception as e:
        print(f"Error in background processing: {e}")
        update_document_status(doc_id, 'failed')
    finally:
        # Cleanup file
        if os.path.exists(filepath):
            os.remove(filepath)

def handle_upload(file):
    if not file or file.filename == '':
        return {"error": "No file provided"}, 400
        
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    
    # Check file size (e.g. max 5MB for free tier safety, though Flask config can handle it too)
    if os.path.getsize(filepath) > 5 * 1024 * 1024:
        os.remove(filepath)
        return {"error": "File exceeds 5MB limit"}, 400

    # Insert document record
    doc_id = insert_document(filename)
    
    # Start background thread
    thread = threading.Thread(target=process_file_background, args=(doc_id, filepath))
    thread.daemon = True
    thread.start()
    
    return {"message": "File uploaded and queued for indexing", "doc_id": doc_id}, 202
