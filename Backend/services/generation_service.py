import os
from google import genai
from services.retrieval_service import retrieval_service

class GenerationService:
    def __init__(self):
        # We will initialize the client dynamically to ensure env vars are loaded
        self.client = None

    def _get_client(self):
        if not self.client:
            # Requires GEMINI_API_KEY to be set in environment
            self.client = genai.Client()
        return self.client

    def generate_answer(self, query):
        
        clean_query = query.strip().lower()
        if not clean_query or len(clean_query) < 4:
            return {"answer": "Please provide a valid question.", "citations": []}
    
        # Retrieve context
        top_chunks = retrieval_service.search(query, top_k=3)
        
        
        if not top_chunks or len(top_chunks) == 0:
            
            return {
                "answer": "I don't have the specific context to answer that question.",
                "citations": []
            }
            
        # Extract our metric indicators from the top match
        best_bm25 = top_chunks[0]['bm25_score']
        best_faiss = top_chunks[0]['faiss_score']
        
        print("best_bm25", best_bm25, " best faiss", best_faiss)
        # 🛑 THE GATEKEEPER: Tighten these parameters based on your testing log data
        # If using L2 Distance: higher numbers mean worse matches. 
        # If a query has NO keywords (BM25 == 0) and the semantic match is weak (L2 > 0.85), BLOCK IT.
        if best_bm25 == 0.0 and best_faiss < 0.60:
            print(f"🛑 Gating Out-of-Context Query. (BM25: {best_bm25}, Cosine: {best_faiss})")
            return {
                "answer": "I don't have the specific context to answer that question.",
                "citations": []
            }
        
        # Prepare context text and citations
        context_text = ""
        citations = []
        for i, chunk in enumerate(top_chunks):
            context_text += f"\n--- Chunk {i+1} (Source: {chunk['filename']}) ---\n{chunk['text']}\n"
            citations.append({
                "filename": chunk['filename'],
                "text_snippet": chunk['text'][:100] + "..."
            })
            
        
        
        
        # Generate answer grounded in context
        prompt = f"""
        You are an AI Careers Assistant. Answer the user's query based ONLY on the provided context.
        If the context does not contain the answer, say "I don't have the specific context for your answer."
        Keep the answer concise and professional.
        
        Context:
        {context_text}
        
        User Query: {query}
        """
        
        try:
            client = self._get_client()
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            answer = response.text
            print("gemini key used")
        except Exception as e:
            print(f"Gemini generation failed: {e}")
            # Fallback to returning just the top chunk text if LLM fails
            answer = f"Found relevant information:\n\n{top_chunks[0]['text']}"

        return {
            "answer": answer,
            "citations": citations
        }

generation_service = GenerationService()
