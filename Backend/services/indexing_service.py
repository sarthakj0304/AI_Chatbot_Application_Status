import os
import faiss
import numpy as np
from fastembed import TextEmbedding
from langchain_text_splitters import RecursiveCharacterTextSplitter
from database.db_manager import  get_db, Document, Chunk
from sqlalchemy.orm import Session
from fastapi import FastAPI, Depends
STORE_PATH = "faiss_store"

class IndexingService:
    def __init__(self):
        os.makedirs(STORE_PATH, exist_ok=True)
        self.index_path = f"{STORE_PATH}/index.faiss"
        self.model = TextEmbedding()
        self.dim = 384 # FastEmbed default
        
        dir_name = os.path.dirname(self.index_path)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name, exist_ok=True)
            print(f"🔹 Created missing storage path: {dir_name}")
        
        sub_index = faiss.IndexFlatIP(self.dim)
        self.index = faiss.IndexIDMap(sub_index)

    def index_document(self, doc_id, text, db : Session):
        try:
            # 1. Chunking
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=150,
                separators=["\n\n", "\n", " ", ""]
            )
            chunks = splitter.split_text(text)
            
            document = db.query(Document).filter(Document.id == doc_id).first()
            if not document:
                print(f"Error: Document ID {doc_id} not found in database.")
                return
            
            if not chunks:
                return
            
            # 2. Insert into postgress to get chunk IDs
            chunk_ids = []
            for i, chunk_text in enumerate(chunks):
                new_chunk = Chunk(doc_id=doc_id, text=chunk_text, chunk_index=i)
                db.add(new_chunk)
                db.commit()  # Saves it to Postgres to generate the ID
                db.refresh(new_chunk)  # Pulls the fresh auto-incremented ID back to Python
                
                chunk_ids.append(new_chunk.id)
            
            # 3. Embed
            embeddings = list(self.model.embed(chunks))
            embeddings = np.array(embeddings).astype("float32")
            
            # Normalise the embedding so that the max and min value remains between 0 and 1 
            faiss.normalize_L2(embeddings)
            
            ids_array = np.array(chunk_ids).astype("int64")
            
            # 4. Add to FAISS
            self.index.add_with_ids(embeddings, ids_array)
            faiss.write_index(self.index, self.index_path)
            
            print(f"🔹 Document {doc_id} indexed successfully with {len(chunks)} chunks.")
            
        except Exception as e:
            print(f"Failed to index document {doc_id}: {e}")
            # If things crash, fetch the document and change status to failed
            document = db.query(Document).filter(Document.id == doc_id).first()
            if document:
                return

indexing_service = IndexingService()
