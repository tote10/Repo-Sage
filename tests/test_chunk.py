import tempfile
from pathlib import Path
from rag.chunk import extract_ast_chunks, chunk_repo, should_skip_path

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

def test_fallback_chunking_on_syntax_error():
    broken_code = "def syntax_err(\n    return 42"
    chunks = extract_ast_chunks(broken_code, "broken.py")
    assert len(chunks) == 1
    assert chunks[0]["type"] == "Block"

def test_should_skip_path():
    assert should_skip_path(Path(".git/config")) is True
    assert should_skip_path(Path("node_modules/pkg/index.js")) is True
    assert should_skip_path(Path("src/main.py")) is False

def test_chunk_repo_sample():
    chunks = chunk_repo("sample_repo")
    assert len(chunks) > 0
    for chunk in chunks:
        assert "text" in chunk
        assert "file" in chunk
        assert "start_line" in chunk
        assert "end_line" in chunk
        assert chunk["end_line"] >= chunk["start_line"]

def test_chunk_repo_with_max_files():
    chunks = chunk_repo("sample_repo", max_files=1)
    assert len(chunks) > 0
    files = {c["file"] for c in chunks}
    assert len(files) == 1
