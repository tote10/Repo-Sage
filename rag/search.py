from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional, Union
import numpy as np
from rag.chunk import chunk_repo
from rag.embed import embed_chunks, embed_text

class RepoIndex:
    """Vector index holding chunks and a precomputed normalized matrix for fast search."""
    def __init__(self, repo_path: Union[str, Path]):
        self.repo_path = str(Path(repo_path).resolve())
        self.chunks: List[Dict[str, Any]] = []
        self.matrix: Optional[np.ndarray] = None
        self.build()

    def clear(self) -> None:
        self.chunks.clear()
        self.matrix = None

    def build(self) -> None:
        self.clear()
        raw_chunks = chunk_repo(self.repo_path)
        self.chunks = embed_chunks(raw_chunks)
        if self.chunks:
            embeddings = [c["embedding"] for c in self.chunks]
            mat = np.array(embeddings, dtype=float)
            norms = np.linalg.norm(mat, axis=1, keepdims=True)
            norms[norms == 0] = 1.0
            self.matrix = mat / norms
        else:
            self.matrix = None

    def search(self, query: str, k: int = 5) -> List[Tuple[float, Dict[str, Any]]]:
        if not self.chunks or self.matrix is None:
            return []
        query_vec = np.array(embed_text(query), dtype=float)
        q_norm = np.linalg.norm(query_vec)
        if q_norm == 0:
            return []
        query_normed = query_vec / q_norm

        scores = np.dot(self.matrix, query_normed)
        top_indices = np.argsort(scores)[::-1][:k]

        return [(float(scores[idx]), self.chunks[idx]) for idx in top_indices]

# Global cache of repository indices
_index_cache: Dict[str, RepoIndex] = {}

def clear_index(repo_path: Optional[Union[str, Path]] = None) -> None:
    """Wipes the cached vector index to ensure idempotent re-indexing."""
    global _index_cache
    if repo_path is not None:
        resolved = str(Path(repo_path).resolve())
        if resolved in _index_cache:
            _index_cache[resolved].clear()
            del _index_cache[resolved]
    else:
        for idx in _index_cache.values():
            idx.clear()
        _index_cache.clear()

def get_repo_index(repo_path: Optional[Union[str, Path]] = None, force_refresh: bool = False) -> RepoIndex:
    resolved_path = str(Path(repo_path).resolve() if repo_path else Path("sample_repo").resolve())
    if force_refresh or resolved_path not in _index_cache:
        if resolved_path in _index_cache:
            _index_cache[resolved_path].clear()
        _index_cache[resolved_path] = RepoIndex(resolved_path)
    return _index_cache[resolved_path]

def search(query: str, k: int = 5, repo_path: Optional[Union[str, Path]] = None) -> List[Tuple[float, Dict[str, Any]]]:
    index = get_repo_index(repo_path)
    return index.search(query, k=k)

if __name__ == "__main__":
    results = search("where does the chunks changed to vectors?", k=3)
    for score, chunk in results:
        print(f"{round(score, 3)}: {chunk['file']}:{chunk['start_line']}")
