import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")
index = faiss.read_index("vector_store/manipulation.index")

def semantic_similarity(text):
    emb = model.encode([text])
    D, _ = index.search(np.array(emb), 1)
    return float(1 / (1 + D[0][0]))
