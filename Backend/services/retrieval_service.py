import numpy as np
from rank_bm25 import BM25Okapi
from database.db_manager import get_all_chunks
from services.indexing_service import indexing_service

class RetrievalService:
    def __init__(self):
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
        query_embedding = np.array(list(indexing_service.model.embed([query]))).astype("float32")
        k_vector = min(10, len(self.corpus_chunks))
        distances, indices = indexing_service.index.search(query_embedding, k_vector)
        
        vector_candidates = []
        best_faiss_distance = float('inf')
        
        for i, chunk_id in enumerate(indices[0]):
            if chunk_id != -1:
                if i == 0:
                    best_faiss_distance = float(distances[0][i])
                chunk_match = next((c for c in self.corpus_chunks if c[0] == chunk_id), None)
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
            
        # 4. Confidence Thresholding
        # If BM25 has no strong keyword match AND FAISS distance is very high (L2 > 1.2 typically means poor semantic match)
        confidence_score = 1.0
        if best_bm25_score < 2.0 and best_faiss_distance > 1.0:
            confidence_score = -10.0 # Force rejection in generation service
            
        top_results = []
        for item in ranked_candidates[:top_k]:
            c = item["chunk"]
            top_results.append({
                "id": c[0],
                "text": c[1],
                "filename": c[2],
                # Pass confidence_score as the 'score' to maintain compatibility with generation_service threshold logic
                "score": confidence_score if len(top_results) == 0 else 0.0 
            })
            
        return top_results

retrieval_service = RetrievalService()
