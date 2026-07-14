from pathlib import Path


chunks = []

for path in Path("sample_repo").rglob("*.py"):
    text = path.read_text(encoding="utf-8")
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

print(len(chunks))
