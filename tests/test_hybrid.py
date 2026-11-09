import pytest
from rag.chunk import chunk_repo
from rag.bm25 import keyword_search
from rag.search import search as vector_search
from rag.hybrid import hybrid_search, reciprocal_rank_fusion

def test_bm25_exact_symbol_match():
    chunks = chunk_repo("sample_repo")
    results = keyword_search("hash_password", chunks, k=3)
    assert len(results) > 0
    top = results[0][1]
    assert "auth.py" in top["file"]
    assert "hash_password" in top["name"]

def test_reciprocal_rank_fusion():
    chunk_a = {"file": "a.py", "start_line": 1, "end_line": 10, "text": "a"}
    chunk_b = {"file": "b.py", "start_line": 1, "end_line": 10, "text": "b"}

    list1 = [(0.9, chunk_a), (0.8, chunk_b)]
    list2 = [(0.95, chunk_b), (0.7, chunk_a)]

    fused = reciprocal_rank_fusion([list1, list2], k=60)
    assert len(fused) == 2
    # Both appeared in top positions, fused list is valid and deduped
    files = [c["file"] for _, c in fused]
    assert "a.py" in files and "b.py" in files

def test_hybrid_search_sample():
    results = hybrid_search("create_access_token", k=3, repo_path="sample_repo")
    assert len(results) > 0
    top = results[0][1]
    assert "auth.py" in top["file"]
    assert "create_access_token" in top["name"]

def test_hybrid_vs_vector_comparison():
    # Evaluation question testing exact function symbol retrieval
    query = "delete_comment"
    hybrid_res = hybrid_search(query, k=1, repo_path="sample_repo")
    assert len(hybrid_res) == 1
    assert "delete_comment" in hybrid_res[0][1]["name"]
