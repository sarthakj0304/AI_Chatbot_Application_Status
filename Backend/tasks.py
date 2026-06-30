import os
from celery import Celery
from database.db_manager import get_db_ctx, Document
from utils.file_parsers import parse_file 
from services.indexing_service import indexing_service
import hashlib

# Docker compose passes these names automatically
broker_url = os.getenv("REDIS_URL", "redis://redis_broker:6379/0")

app = Celery('worker', broker=broker_url, backend=broker_url)

@app.task(name="tasks.process_document_task")
def process_document_task(doc_id : int, filepath: str):
    print(f"🔹 Celery Worker: Starting background processing for Document ID {doc_id}...")
    
    # This is a temporary access to the posgtress session using "with" operator, need to pass the Session:db with this
    with get_db_ctx() as db:
        
        
        db_record=db.query(Document).filter(Document.id==doc_id).first()
        if not db_record:
                print(f"Error: Document ID {doc_id} not found.")
                # Clean up the orphaned file anyway so it doesn't leak storage
                if os.path.exists(filepath):
                    os.remove(filepath)
                return
        
        try:
            
            # Extract text
            text = parse_file(filepath)
            
            if not text or not text.strip():
                db_record.status = 'failed'
                db.commit()
                return
            
            file_hash = hashlib.md5(text.encode('utf-8')).hexdigest()
            
            # 3. Check if this exact hash ALREADY exists in another COMPLETED document
            duplicate = db.query(Document).filter(
                Document.hash_file == file_hash, 
                Document.status == 'completed'
            ).first()
            
            # if the current file hash already exists, do nothing 
            if duplicate:
                
                print(f"Duplicate found! Doc ID {doc_id} matches existing Doc ID {duplicate.id}. Skipping.")
                # Mark this new redundant entry as failed/duplicate so it doesn't stay 'queued'
                db_record.status = 'failed'
                db_record.hash_file = file_hash # Track it anyway
                db.commit()
                return # Triggers the 'finally' block automatically to delete the file!
                
            # 4. No duplicate found: Proceed to index normally
            db_record.status = 'processing'
            db_record.hash_file = file_hash
            db.commit()
            
            # Is the document is new, we index it
            indexing_service.index_document(doc_id, text, db)
                
            db_record.status = 'completed'
            db.commit()
            
            
        except Exception as e:
            print(f"Error in background processing: {e}")
            db.rollback() # Rollback any corrupted partial database changes
            
            # Re-fetch or reuse record to save the failure state safely
            db_record.status = 'failed'
            db.commit()
        finally:
        # Cleanup file
            if os.path.exists(filepath):
                os.remove(filepath)
                db.refresh(db_record)
        