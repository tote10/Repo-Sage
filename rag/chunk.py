from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Set
import ast

DEFAULT_SAMPLE = Path(__file__).resolve().parent.parent / "sample_repo"

DEFAULT_IGNORE_DIRS: Set[str] = {
    ".git", "__pycache__", ".venv", "venv", "env", "node_modules",
    "build", "dist", ".tox", ".eggs", ".mypy_cache", ".pytest_cache"
}
MAX_FILE_SIZE_BYTES = 1024 * 1024  # 1MB limit

def should_skip_path(path: Path, skip_dirs: Optional[Set[str]] = None) -> bool:
    ignored = skip_dirs or DEFAULT_IGNORE_DIRS
    return any(part in ignored or part.startswith(".") for part in path.parts)

def fallback_line_chunks(text: str, file_path: Union[str, Path], window_size: int = 50, overlap: int = 10) -> List[Dict[str, Any]]:
    """Chunks text into sliding line windows when AST parsing is unavailable."""
    lines = text.split("\n")
    total_lines = len(lines)
    chunks = []
    if total_lines == 0:
        return chunks
    step = max(1, window_size - overlap)
    for start_idx in range(0, total_lines, step):
        end_idx = min(total_lines, start_idx + window_size)
        chunk_lines = lines[start_idx:end_idx]
        chunk_text = "\n".join(chunk_lines).strip()
        if chunk_text:
            chunks.append({
                "text": chunk_text,
                "file": str(file_path),
                "start_line": start_idx + 1,
                "end_line": end_idx,
                "name": f"lines_{start_idx + 1}_{end_idx}",
                "type": "Block"
            })
        if end_idx >= total_lines:
            break
    return chunks

def extract_ast_chunks(text: str, file_path: Union[str, Path]) -> List[Dict[str, Any]]:
    try:
        tree = ast.parse(text)
    except SyntaxError:
        return fallback_line_chunks(text, file_path)

    lines = text.split("\n")
    chunks = []
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            name = node.name
            type_ = "Class" if isinstance(node, ast.ClassDef) else "Function"
            start = node.lineno 
            end = node.end_lineno if hasattr(node, "end_lineno") and node.end_lineno else start
            chunk_text = "\n".join(lines[start - 1:end])
            chunk = {
                "text": chunk_text,
                "file": str(file_path),
                "start_line": start,
                "end_line": end,
                "name": name,
                "type": type_
            }
            chunks.append(chunk)

    if not chunks and text.strip():
        # Module-level code without functions/classes
        chunks = fallback_line_chunks(text, file_path)

    return chunks

def chunk_repo(
    repo_path: Optional[Union[str, Path]] = None,
    max_files: Optional[int] = None
) -> List[Dict[str, Any]]:
    chunks = []
    target_path = Path(repo_path) if repo_path else DEFAULT_SAMPLE
    if not target_path.exists():
        return []

    files_processed = 0
    for path in sorted(target_path.rglob("*.py")):
        if should_skip_path(path):
            continue 
        try:
            if path.stat().st_size > MAX_FILE_SIZE_BYTES:
                continue
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue

        extracted = extract_ast_chunks(text, path)
        chunks.extend(extracted)
        files_processed += 1
        if max_files and files_processed >= max_files:
            break

    return chunks

if __name__ == "__main__":
    chunks = chunk_repo()
    print(f"Total chunks: {len(chunks)}")
    for c in chunks[:8]:
        print(f"File: {c['file']} (lines {c['start_line']}-{c['end_line']}):\n{c['text']}\n(type: {c['type']}, name: {c['name']})\n---")
