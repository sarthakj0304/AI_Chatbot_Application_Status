import faiss
import pickle
import numpy as np
from fastembed import TextEmbedding

class RAGSearch:
    def __init__(self, store_path):
        self.model = TextEmbedding()
        self.index = faiss.read_index(f"{store_path}/index.faiss")

        with open(f"{store_path}/metadata.pkl", "rb") as f:
            self.metadata = pickle.load(f)

    def search(self, query, top_k=1, threshold=0.7):
        query_embedding = np.array(
            list(self.model.embed([query]))
        ).astype("float32")

        distances, indices = self.index.search(query_embedding, top_k)

        if len(indices[0]) == 0:
            return "No relevant information found."

        best_distance = distances[0][0]

        # FAISS IndexFlatL2 → smaller distance = better match
        if best_distance > threshold:
            return "I don’t have the specific context for your answer."

        return self.metadata[indices[0][0]]
    # def search(self, query, top_k=1):
    #     query_embedding = np.array(
    #         list(self.model.embed([query]))
    #     ).astype("float32")

    #     distances, indices = self.index.search(query_embedding, top_k)

    #     print("Distance:", distances[0][0])  # DEBUG

    #     return self.metadata[indices[0][0]]