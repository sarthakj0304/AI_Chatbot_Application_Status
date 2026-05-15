import faiss
import numpy as np

index = faiss.IndexIDMap(faiss.IndexFlatL2(384))
embeddings = np.ascontiguousarray(np.random.rand(2, 384).astype("float32"))
ids = np.ascontiguousarray(np.array([1, 2]).astype("int64"))
index.add_with_ids(embeddings, ids)

query = np.ascontiguousarray(np.random.rand(1, 384).astype("float32"))
print("Searching...")
distances, indices = index.search(query, 2)
print("Done:", indices)
