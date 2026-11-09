from rag.chunk import extract_ast_chunks, chunk_repo
from pathlib import Path

def test_extract_ast_chunks():
    sample_code = """
def hello(name: str):
    return f"Hello, {name}!"

class Greeter:
    def greet(self):
        return "Hi"
"""
    chunks = extract_ast_chunks(sample_code, "test.py")
    assert len(chunks) == 2
    names = [c["name"] for c in chunks]
    assert "hello" in names
    assert "Greeter" in names
    assert chunks[0]["start_line"] == 2
    assert chunks[1]["type"] == "Class"

def test_chunk_repo_sample():
    chunks = chunk_repo("sample_repo")
    assert len(chunks) > 0
    for chunk in chunks:
        assert "text" in chunk
        assert "file" in chunk
        assert "start_line" in chunk
        assert "end_line" in chunk
        assert chunk["end_line"] >= chunk["start_line"]
