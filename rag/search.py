from sentence_transformers import SentenceTransformer
from embed import embed_chunks
from chunk import chunk_repo
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')
chunks = embed_chunks(chunk_repo())
def cosine_sim(a,b):
    return(np.dot(a,b)/(np.linalg.norm(a)*np.linalg.norm(b)))
def search(query ,k=5):
    
    query_vec = model.encode(query)
    scored = []
    for chunk in chunks:
        score = cosine_sim(query_vec, chunk["embedding"])
        scored.append((score, chunk))
    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[:k]
