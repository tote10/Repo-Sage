from typing import List, Tuple, Dict, Any, Optional
import math
import numpy as np
from rag.chunk import chunk_repo
from rag.embed import embed_chunks, embed_text

_cached_chunks = None

def get_indexed_chunks(repo_path: Optional[str] = None) -> List[Dict[str, Any]]:
    global _cached_chunks
    if _cached_chunks is None or repo_path is not None:
        raw_chunks = chunk_repo(repo_path)
        indexed = embed_chunks(raw_chunks)
        if repo_path is None:
            _cached_chunks = indexed
        return indexed
    return _cached_chunks

def cosine_sim(a: Any, b: Any) -> float:
    a_arr = np.array(a, dtype=float)
    b_arr = np.array(b, dtype=float)
    norm_a = np.linalg.norm(a_arr)
    norm_b = np.linalg.norm(b_arr)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a_arr, b_arr) / (norm_a * norm_b))

def search(query: str, k: int = 5, repo_path: Optional[str] = None) -> List[Tuple[float, Dict[str, Any]]]:
    chunks = get_indexed_chunks(repo_path)
    if not chunks:
        return []
    query_vec = embed_text(query)
    scored = []
    for chunk in chunks:
        score = cosine_sim(query_vec, chunk["embedding"])
        scored.append((score, chunk))
    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[:k]

if __name__ == "__main__":
    results = search("where does the chunks changed to vectors?", k=3)
    for score, chunk in results:
        print(f"{round(score, 3)}: {chunk['file']}:{chunk['start_line']}")
