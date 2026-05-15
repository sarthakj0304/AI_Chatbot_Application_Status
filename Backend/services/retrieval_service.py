import numpy as np
from fastembed import TextEmbedding
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder
from database.db_manager import get_all_chunks
from services.indexing_service import indexing_service

class RetrievalService:
    def __init__(self):
        self.embed_model = TextEmbedding()
        # Extremely lightweight cross-encoder
        self.reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
        self.bm25 = None
        self.corpus_chunks = [] # List of tuples: (id, text, filename)
        self.tokenized_corpus = []
        self._refresh_bm25()
        
    def _refresh_bm25(self):
        # In a real heavy production, we'd trigger this on a schedule or after batch uploads.
        # For lightweight Render app, we reload from SQLite.
        self.corpus_chunks = get_all_chunks()
        if self.corpus_chunks:
            self.tokenized_corpus = [chunk[1].lower().split() for chunk in self.corpus_chunks]
            self.bm25 = BM25Okapi(self.tokenized_corpus)
            
    def search(self, query, top_k=3):
        self._refresh_bm25() # Ensure we have latest documents
        
        if not self.corpus_chunks:
            return []
            
        # 1. Vector Search (FAISS)
        query_embedding = np.array(list(self.embed_model.embed([query]))).astype("float32")
        k_vector = min(10, len(self.corpus_chunks))
        distances, indices = indexing_service.index.search(query_embedding, k_vector)
        
        vector_candidates = []
        for i, chunk_id in enumerate(indices[0]):
            if chunk_id != -1:
                # Find the chunk details from corpus
                chunk_match = next((c for c in self.corpus_chunks if c[0] == chunk_id), None)
                if chunk_match:
                    vector_candidates.append(chunk_match)
                    
        # 2. BM25 Keyword Search
        bm25_candidates = []
        if self.bm25:
            tokenized_query = query.lower().split()
            bm25_scores = self.bm25.get_scores(tokenized_query)
            # Get top 10 indices
            top_bm25_idx = np.argsort(bm25_scores)[::-1][:10]
            bm25_candidates = [self.corpus_chunks[i] for i in top_bm25_idx if bm25_scores[i] > 0]
            
        # 3. Combine Candidates (Unique by ID)
        unique_candidates = {}
        for c in vector_candidates + bm25_candidates:
            unique_candidates[c[0]] = c
            
        candidates_list = list(unique_candidates.values())
        if not candidates_list:
            return []
            
        # 4. Reranking (Cross-Encoder)
        cross_inp = [[query, c[1]] for c in candidates_list]
        cross_scores = self.reranker.predict(cross_inp)
        
        # Sort by score descending
        ranked_indices = np.argsort(cross_scores)[::-1]
        
        top_results = []
        for idx in ranked_indices[:top_k]:
            c = candidates_list[idx]
            top_results.append({
                "id": c[0],
                "text": c[1],
                "filename": c[2],
                "score": float(cross_scores[idx])
            })
            
        return top_results

retrieval_service = RetrievalService()
