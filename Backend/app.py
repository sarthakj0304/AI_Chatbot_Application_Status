import os
from dotenv import load_dotenv
import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File
from pydantic import BaseModel
from sqlalchemy.orm import Session
from services.redis_cache_service import check_semantic_cache, save_to_cache
import warnings
# Silence annoying library deprecation warnings

warnings.filterwarnings("ignore", category=UserWarning)

from services.ingestion_service import handle_upload
from services.generation_service import generation_service

from fastapi.middleware.cors import CORSMiddleware

from database.db_manager import init_db, get_db, Document, Conversation, Lead
from contextlib import asynccontextmanager
from sqlalchemy import func
# Load env variables first
load_dotenv()

# ==============================
# Initialize Database (Must happen before service imports)
# ==============================
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🔹 Initializing PostgreSQL Database Schema...")
    init_db()  # Automatically checks Postgres and creates all tables
    yield


#Creating Fast API endpoint
app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# ==============================
# Document Upload Endpoint
# ==============================
@app.post("/upload")
def upload_file(file : UploadFile = File(...), db : Session = Depends(get_db)):
    result = handle_upload(file, db)
    return result

@app.get("/admin/documents")
def get_documents(db: Session = Depends(get_db)):
    docs = db.query(Document).order_by(Document.id.desc()).all()
    return [{"id": d.id, "filename": d.filename, "status": d.status, "upload_time": d.upload_time} for d in docs]

# ==============================
# Chat Endpoint
# ==============================
@app.post("/chat")
def chat(payload : dict , db : Session = Depends(get_db) ):
    
    query = payload.get("query")

    if not query:
        raise HTTPException(status_code=400, detail="No query provided.")
    
    
    cached_data = check_semantic_cache(query)
    # If cache hit - return it
    if cached_data:
        return cached_data

    
    result = generation_service.generate_answer(query)
    
    answer = result["answer"]
    citations = result["citations"]
    
    new_convo = Conversation(query=query, answer=answer)
    db.add(new_convo)
    db.commit()
    
    if "context for your answer" not in result["answer"]:
        save_to_cache(query, result)

    return {"answer": answer, "citations": citations}


# ==============================
# Lead Capture Endpoint
# ==============================
@app.post("/lead")
def lead(data : dict, db : Session = Depends(get_db) ):
    
    email = data.get("email")
    role = data.get("role")

    if not email or not role:
        raise HTTPException(status_code=400, detail= "Missing email or role")
    
    new_convo = Lead(email=email, role=role)
    db.add(new_convo)
    db.commit()
    
    return {"message": "Lead captured successfully"}
    

# ==============================
# Admin - Conversation Logs
# ==============================
@app.get("/admin/logs")
def admin_logs(db: Session = Depends(get_db)):
    
    rows = db.query(Conversation).order_by(Conversation.id.desc()).all()
    return [{"query": r.query, "answer": r.answer, "timestamp": r.timestamp} for r in rows]

    

# ==============================
# Admin - Most Asked Questions
# ==============================
@app.get("/admin/stats")
def admin_stats(db: Session = Depends(get_db)):
    # Counts top 5 most asked questions
    stats = (
        db.query(Conversation.query, func.count(Conversation.id).label("count"))
        .group_by(Conversation.query)
        .order_by(func.count(Conversation.id).desc())
        .limit(5)
        .all()
    )
    return [{"query": s[0], "count": s[1]} for s in stats]

@app.get("/admin/analytics")
def admin_analytics(db: Session = Depends(get_db)):
    total = db.query(Conversation).count()
    
    # Matches your old string check logic
    unanswered = db.query(Conversation).filter(Conversation.answer.like("%don't have the specific context%")).count()
    
    success_rate = round(((total - unanswered) / total * 100) if total > 0 else 100, 2)
    
    return {
        "total_queries": total,
        "unanswered_queries": unanswered,
        "success_rate": success_rate
    }

# ==============================
# Run App
# ==============================
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)