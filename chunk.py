from pathlib import Path

def chunk_repo():
    chunks = []
    skip_dirs = {".git", "__pycache__", ".venv", "venv", "env", "node_modules","sample_repo"}
    for path in Path(".").rglob("*.py"): 
        if any(skip in path.parts for skip in skip_dirs):
            continue 
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        start = 0
        overlap = 100
        while start < len(text):
            end = min(start + 800, len(text))
            piece = text[start:end]
            chunk = {"text": piece, "file": str(path), "start_line": text.count('\n', 0, start) + 1, "end_line": text.count('\n', 0, end) + 1}
            chunks.append(chunk)
            if end == len(text):
                break
            start = end - overlap
    return chunks



if __name__ == "__main__":
    print(chunk_repo())
