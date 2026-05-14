import os
import pickle
import faiss
import numpy as np
from fastembed import TextEmbedding
from langchain_text_splitters import RecursiveCharacterTextSplitter
DATA_PATH = "data"
STORE_PATH = "faiss_store"

def load_documents():
    docs = []
    for file in os.listdir(DATA_PATH):
        if file.endswith(".txt"):
            
            with open(os.path.join(DATA_PATH, file), "r", encoding="utf-8") as f:
                docs.append(f.read())
    return docs

def chunk_text(text):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=150,
        separators=["\n\n", "\n", " ", ""]
    )
    return splitter.split_text(text)

if __name__ == "__main__":
    os.makedirs(STORE_PATH, exist_ok=True)

    docs = load_documents()
    chunks = []
    for doc in docs:
        chunks.extend(chunk_text(doc))

    model = TextEmbedding()
    embeddings = list(model.embed(chunks))
    embeddings = np.array(embeddings).astype("float32")

    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    faiss.write_index(index, f"{STORE_PATH}/index.faiss")

    with open(f"{STORE_PATH}/metadata.pkl", "wb") as f:
        pickle.dump(chunks, f)

    print("Index built successfully.")