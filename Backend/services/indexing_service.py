import os
import faiss
import numpy as np
from fastembed import TextEmbedding
from langchain_text_splitters import RecursiveCharacterTextSplitter
from database.db_manager import insert_chunk, update_document_status

STORE_PATH = "faiss_store"

class IndexingService:
    def __init__(self):
        os.makedirs(STORE_PATH, exist_ok=True)
        self.index_path = f"{STORE_PATH}/index.faiss"
        self.model = TextEmbedding()
        self.dim = 384 # FastEmbed default
        
        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
        else:
            # We use IndexIDMap to store custom IDs (SQLite chunk IDs)
            self.index = faiss.IndexIDMap(faiss.IndexFlatL2(self.dim))

    def index_document(self, doc_id, text):
        try:
            # 1. Chunking
            splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=150,
                separators=["\n\n", "\n", " ", ""]
            )
            chunks = splitter.split_text(text)
            
            if not chunks:
                update_document_status(doc_id, 'completed')
                return
            
            # 2. Insert into SQLite to get chunk IDs
            chunk_ids = []
            for i, chunk_text in enumerate(chunks):
                chunk_id = insert_chunk(doc_id, chunk_text, i)
                chunk_ids.append(chunk_id)
            
            # 3. Embed
            embeddings = list(self.model.embed(chunks))
            embeddings = np.array(embeddings).astype("float32")
            ids_array = np.array(chunk_ids).astype("int64")
            
            # 4. Add to FAISS
            self.index.add_with_ids(embeddings, ids_array)
            faiss.write_index(self.index, self.index_path)
            
            # 5. Update status
            update_document_status(doc_id, 'completed')
            print(f"Document {doc_id} indexed successfully with {len(chunks)} chunks.")
            
        except Exception as e:
            print(f"Failed to index document {doc_id}: {e}")
            update_document_status(doc_id, 'failed')

indexing_service = IndexingService()
