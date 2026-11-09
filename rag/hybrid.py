from typing import List, Tuple, Dict, Any, Optional, Union
from pathlib import Path
from rag.search import get_repo_index
from rag.bm25 import BM25Index

def reciprocal_rank_fusion(
    ranked_lists: List[List[Tuple[float, Dict[str, Any]]]],
    k: int = 60
) -> List[Tuple[float, Dict[str, Any]]]:
    """Combines rankings from multiple retrievers using Reciprocal Rank Fusion (RRF)."""
    scores: Dict[str, float] = {}
    chunk_map: Dict[str, Dict[str, Any]] = {}

    for ranked_list in ranked_lists:
        for rank, (_score, chunk) in enumerate(ranked_list):
            chunk_id = f"{chunk['file']}:{chunk['start_line']}-{chunk['end_line']}"
            chunk_map[chunk_id] = chunk
            rrf_score = 1.0 / (k + rank + 1)
            scores[chunk_id] = scores.get(chunk_id, 0.0) + rrf_score

    fused = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [(score, chunk_map[cid]) for cid, score in fused]

def rerank_candidates(
    query: str,
    candidates: List[Tuple[float, Dict[str, Any]]],
    top_k: int = 5
) -> List[Tuple[float, Dict[str, Any]]]:
    """Lightweight cross-encoder or term-density reranking to score shortlist."""
    if not candidates:
        return []

    # Score by exact query term density + symbol prominence in chunk
    query_terms = set(query.lower().split())
    reranked = []
    for rrf_score, chunk in candidates:
        text_lower = chunk["text"].lower()
        name_lower = chunk.get("name", "").lower()

        # Bonus if symbol matches name
        name_bonus = 2.0 if any(term in name_lower for term in query_terms) else 0.0
        # Term presence ratio
        matched_terms = sum(1 for t in query_terms if t in text_lower)
        coverage = matched_terms / len(query_terms) if query_terms else 0.0

        boosted_score = rrf_score * (1.0 + coverage + name_bonus)
        reranked.append((boosted_score, chunk))

    reranked.sort(key=lambda x: x[0], reverse=True)
    return reranked[:top_k]

def hybrid_search(
    query: str,
    k: int = 5,
    repo_path: Optional[Union[str, Path]] = None,
    candidate_pool_size: int = 20
) -> List[Tuple[float, Dict[str, Any]]]:
    """Runs semantic vector search + BM25 keyword search, fuses them with RRF, and reranks."""
    index = get_repo_index(repo_path)
    if not index.chunks:
        return []

    # 1. Semantic vector search
    semantic_results = index.search(query, k=candidate_pool_size)

    # 2. BM25 keyword search
    bm25 = BM25Index(index.chunks)
    bm25_results = bm25.score(query)[:candidate_pool_size]

    # 3. Reciprocal Rank Fusion
    fused = reciprocal_rank_fusion([semantic_results, bm25_results], k=60)

    # 4. Rerank top candidates
    shortlist = fused[:candidate_pool_size]
    final_results = rerank_candidates(query, shortlist, top_k=k)
    return final_results

if __name__ == "__main__":
    results = hybrid_search("verify_password", k=3)
    for score, chunk in results:
        print(f"Hybrid score {score:.4f}: {chunk['file']}:{chunk['start_line']} ({chunk.get('name')})")
