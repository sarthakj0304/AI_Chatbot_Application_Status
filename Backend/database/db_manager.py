import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, func
from contextlib import contextmanager
from sqlalchemy.orm import sessionmaker, declarative_base, relationship, Session
from pathlib import Path
parent_env_path = Path(__file__).resolve().parents[1] / '.env'


load_dotenv(dotenv_path=parent_env_path)
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    status = Column(String, default="pending")
    
    # This sets up an automatic link to the Chunk model
    chunks = relationship("Chunk", back_populates="document")
    
    hash_file= Column(String)
    
    
    
class Chunk(Base):
    __tablename__ = "chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    chunk_index = Column(Integer, nullable=False)
    
    # 1. Physical foreign key in PostgreSQL
    doc_id = Column(Integer, ForeignKey("documents.id"))
    
    # 2. Virtual link in Python to jump from a chunk straight to its parent document
    document = relationship("Document", back_populates="chunks")

class Lead(Base):
    __tablename__ = "leads"
    id = Column(Integer, primary_key=True, index=True, )
    email = Column(String, nullable=False)
    role = Column(String, nullable=False)
    timestamp = Column(DateTime, server_default=func.now())

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True, index=True)
    query = Column(String, nullable=False)
    answer = Column(String, nullable=False)
    timestamp = Column(DateTime, server_default=func.now())
    
def init_db():
    print("Tables to be created:", Base.metadata.tables.keys())
    Base.metadata.create_all(bind=engine)


def get_db():
    """
    Dual-purpose generator:
    1. Works as a FastAPI Dependency: db = Depends(get_db)
    2. Works as a Python Context Manager: with get_db() as db:
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
get_db_ctx = contextmanager(get_db)

def get_all_chunks(db: Session = None):
    if db is not None:
        return db.query(Chunk.id, Chunk.text, Document.filename).join(Document).all()
    
    # Use the specific context manager helper here
    with get_db_ctx() as dynamic_db:
        return dynamic_db.query(Chunk.id, Chunk.text, Document.filename).join(Document).all()
    
