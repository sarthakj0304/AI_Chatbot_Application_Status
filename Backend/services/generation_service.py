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
        # Retrieve context
        top_chunks = retrieval_service.search(query, top_k=3)
        
        if not top_chunks:
            return {
                "answer": "I don't have the specific context to answer that question.",
                "citations": []
            }
            
        # Check confidence (Cross Encoder scores typically range from roughly -10 to +10)
        # We can set a threshold. If the best score is very low, it's a hallucination risk.
        best_score = top_chunks[0]['score']
        
        # Prepare context text and citations
        context_text = ""
        citations = []
        for i, chunk in enumerate(top_chunks):
            context_text += f"\n--- Chunk {i+1} (Source: {chunk['filename']}) ---\n{chunk['text']}\n"
            citations.append({
                "filename": chunk['filename'],
                "text_snippet": chunk['text'][:100] + "..."
            })
            
        # If confidence is exceptionally low, strictly deny the answer instead of hallucinating.
        if best_score < -2.0:
            print(f"Low confidence ({best_score}). Denying answer.")
            return {
                "answer": "The information was not provided in the documents",
                "citations": []
            }
        
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
