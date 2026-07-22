from pathlib import Path
import ast

SAMPLE = Path(__file__).parent.parent / "sample_repo"



def extract_ast_chunks(text, file_path):
    chunks = []
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []
    lines = text.split("\n")
    for node in tree.body:
        if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef, ast.ClassDef)):
            name = node.name
            type_ = "Class" if isinstance(node, ast.ClassDef) else "Function"
            start = node.lineno 
            end = node.end_lineno
            chunk_text = "\n".join(lines[start -1:end])
            chunk = {"text": chunk_text, "file": str(file_path), "start_line": start, "end_line": end, "name": name, "type": type_}
            chunks.append(chunk)
    return chunks
def chunk_repo():
    chunks = []
    skip_dirs = {".git", "__pycache__", ".venv", "venv", "env", "node_modules",}
    for path in SAMPLE.rglob("*.py"): 
        if any(skip in path.parts for skip in skip_dirs):
            continue 
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        chunks.extend(extract_ast_chunks(text, path))
    return chunks



if __name__ == "__main__":
    chunks = chunk_repo()
    print(f"Total chunks: {len(chunks)}")
    for c in chunks[:8]:
        print(f"File: {c['file']} (lines {c['start_line']}-{c['end_line']}):\n{c['text']}\n(type: {c['type']}, name: {c['name']})\n---")
    
