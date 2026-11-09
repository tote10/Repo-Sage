from typing import List, Dict, Any, Optional
import math
import re

_transformer_model = None

def get_transformer_model(model_name: str = "all-MiniLM-L6-v2"):
    global _transformer_model
    if _transformer_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _transformer_model = SentenceTransformer(model_name)
        except Exception:
            _transformer_model = False
    return _transformer_model if _transformer_model is not False else None

def _simple_text_vector(text: str, dim: int = 64) -> List[float]:
    """Fallback hash-based term vector when sentence_transformers is unavailable."""
    vec = [0.0] * dim
    words = re.findall(r"\w+", text.lower())
    if not words:
        return vec
    for w in words:
        idx = hash(w) % dim
        vec[idx] += 1.0
    norm = math.sqrt(sum(x * x for x in vec))
    if norm > 0:
        vec = [x / norm for x in vec]
    return vec

def embed_chunks(chunks: List[Dict[str, Any]], model_name: str = "all-MiniLM-L6-v2") -> List[Dict[str, Any]]:
    model = get_transformer_model(model_name)
    if model is not None:
        vectors = model.encode([chunk["text"] for chunk in chunks])
        for c, v in zip(chunks, vectors):
            c["embedding"] = v
    else:
        for c in chunks:
            c["embedding"] = _simple_text_vector(c["text"])
    return chunks

def embed_text(text: str, model_name: str = "all-MiniLM-L6-v2") -> Any:
    model = get_transformer_model(model_name)
    if model is not None:
        return model.encode(text)
    return _simple_text_vector(text)

if __name__ == "__main__":
    from rag.chunk import chunk_repo
    chunks = embed_chunks(chunk_repo())
    print(f"{len(chunks)} chunks, vector length: {len(chunks[0]['embedding']) if chunks else 0}")
