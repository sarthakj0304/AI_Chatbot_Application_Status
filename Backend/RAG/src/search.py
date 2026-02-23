import os

from dotenv import load_dotenv
from RAG.src.vectorstore import FaissVectorStore


load_dotenv()

class RAGSearch:
    def __init__(self, persist_dir: str = "RAG/faiss_store", embedding_model: str = "all-MiniLM-L6-v2"):
        self.vectorstore = FaissVectorStore(persist_dir, embedding_model)
        # Load or build vectorstore
        faiss_path = os.path.join(persist_dir, "faiss.index")
        meta_path = os.path.join(persist_dir, "metadata.pkl")
        # if not (os.path.exists(faiss_path) and os.path.exists(meta_path)):
        #     from data_loader import load_all_documents
        #     docs = load_all_documents("data")
        #     self.vectorstore.build_from_documents(docs)
        # else:
        self.vectorstore.load()
        

    def search(self, query: str, top_k: int = 1, threshold: float = 0.30) -> str:
        results = self.vectorstore.query(query, top_k=top_k)

        if not results:
            return "I don’t have the specific context for your answer."
        # Filter by threshold
        filtered = [r for r in results if r["distance"] >= threshold]

        if not filtered:
            return "I don’t have the specific context for your answer."

        # Take top 2 relevant chunks
        top_chunks = filtered[:2]

        texts = [r["metadata"].get("text", "") for r in top_chunks]

        return "\n\n".join(texts)

# # Example usage
# if __name__ == "__main__":
#     rag_search = RAGSearch()
#     query = "What is attention mechanism?"
#     summary = rag_search.search_and_summarize(query, top_k=3)
#     print("Summary:", summary)
