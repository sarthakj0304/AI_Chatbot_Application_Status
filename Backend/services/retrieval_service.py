# In services/retrieval_service.py
import os
import numpy as np
from rank_bm25 import BM25Okapi
from database.db_manager import get_all_chunks
from services.indexing_service import indexing_service
import faiss

class RetrievalService:
    def __init__(self):
        self.bm25 = None
        self.corpus_chunks = []
        self.tokenized_corpus = []

    def _refresh_bm25(self):
        self.corpus_chunks = get_all_chunks()
        if self.corpus_chunks:
            self.tokenized_corpus = [chunk[1].lower().split() for chunk in self.corpus_chunks]
            self.bm25 = BM25Okapi(self.tokenized_corpus)

    def search(self, query, top_k=3):
        self._refresh_bm25()
        
        if not self.corpus_chunks:
            return []

        # THE CORRECTION HOOK: Load the latest index from disk into memory
        # =====================================================================
        # THE STATE RECONCILIATION HOOK
        # =====================================================================
        # PROBLEM BEFORE: FastAPI and Celery run in completely isolated containers.
        # When Celery indexed a document, it updated its own memory and wrote to disk,
        # but FastAPI's memory index remained blank. FastAPI was searching an empty index.
        #
        # SOLUTION (live_index): We bypass the static in-memory index. Every time a user 
        # submits a query, we read the raw, updated binary vector file directly from the 
        # shared volume. This synchronizes the vector state between Celery and FastAPI.
        index_path = "faiss_store/index.faiss"
        if os.path.exists(index_path):
            try:
                # Read the fresh vector binaries written by Celery
                live_index = faiss.read_index(index_path)
            except Exception as e:
                print(f"Error reading FAISS index from disk: {e}")
                live_index = indexing_service.index
        else:
            print("FAISS index file not found on disk yet.")
            # Fallback if no documents have ever been uploaded yet
            live_index = indexing_service.index

        # 1. Vector Search (Using the live_index)
        query_embedding = np.array(list(indexing_service.model.embed([query]))).astype("float32")
        faiss.normalize_L2(query_embedding)
        
        k_vector = min(10, len(self.corpus_chunks))
        
        # Query the live index
        # Query our freshly loaded disk index. 
        # distances: matrix of similarity scores (higher is better, 1.0 is identical)
        # indices: matrix of corresponding relational database Chunk IDs
        distances, indices = live_index.search(query_embedding, k_vector)
        
        # Create an empty list to collect the fully resolved database text chunks
        vector_candidates = []
        best_faiss_score = 0.0
        
        # indices[0] contains the array of closest matching chunk IDs (e.g., [14, 2, 9])
        for i, chunk_id in enumerate(indices[0]):
            if chunk_id != -1:
                
                # Capture the very first item (index 0) because FAISS sorts matches by quality.
                # This gives us our absolute highest semantic similarity score for threshold gating.
                if i == 0:
                    best_faiss_score = float(distances[0][i])
                    
                # FAISS only returns numeric IDs. We must match the FAISS ID (chunk_id) 
                # against our PostgreSQL records (self.corpus_chunks) to find the actual text.
                # c[0] is the database Chunk ID, c[1] is the text content, c[2] is the filename.
                chunk_match = next((c for c in self.corpus_chunks if c[0] == chunk_id), None)
                
                # If the ID exists in our PostgreSQL cache, append the text tuple to our candidates
                if chunk_match:
                    vector_candidates.append(chunk_match)

        # 2. BM25 Keyword Search
        bm25_candidates = []
        best_bm25_score = 0.0
        
        if self.bm25:
            tokenized_query = query.lower().split()
            bm25_scores = self.bm25.get_scores(tokenized_query)
            best_bm25_score = float(max(bm25_scores)) if len(bm25_scores) > 0 else 0.0
            
            top_bm25_idx = np.argsort(bm25_scores)[::-1][:10]
            bm25_candidates = [self.corpus_chunks[i] for i in top_bm25_idx if bm25_scores[i] > 0]

        # 3. Reciprocal Rank Fusion (RRF)
        rrf_k = 60
        rrf_scores = {}
        
        for rank, c in enumerate(vector_candidates):
            cid = c[0]
            if cid not in rrf_scores:
                rrf_scores[cid] = {"chunk": c, "score": 0.0}
            rrf_scores[cid]["score"] += 1.0 / (rrf_k + rank + 1)
            
        for rank, c in enumerate(bm25_candidates):
            cid = c[0]
            if cid not in rrf_scores:
                rrf_scores[cid] = {"chunk": c, "score": 0.0}
            rrf_scores[cid]["score"] += 1.0 / (rrf_k + rank + 1)
            
        ranked_candidates = sorted(list(rrf_scores.values()), key=lambda x: x["score"], reverse=True)
        
        if not ranked_candidates:
            return []

        top_results = []
        for item in ranked_candidates[:top_k]:
            c = item["chunk"]
            top_results.append({
                "id": c[0],
                "text": c[1],
                "filename": c[2],
                "bm25_score": best_bm25_score,       
                "faiss_score": best_faiss_score 
            })
            
        return top_results

retrieval_service = RetrievalService()