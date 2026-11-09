from pathlib import Path
from typing import Optional, Union, Set

DEFAULT_IGNORE_DIRS: Set[str] = {
    ".git", "__pycache__", ".venv", "venv", "env", "node_modules",
    "build", "dist", ".tox", ".eggs", ".mypy_cache", ".pytest_cache"
}
MAX_FILE_SIZE_BYTES = 1024 * 1024  # 1MB limit per source file to avoid OOM

def should_skip_path(path: Path, skip_dirs: Optional[Set[str]] = None) -> bool:
    ignored = skip_dirs or DEFAULT_IGNORE_DIRS
    return any(part in ignored or part.startswith(".") for part in path.parts)

def load_repo(repo_path: Optional[Union[str, Path]] = None, max_chars: int = 5_000_000) -> str:
    path_obj = Path(repo_path) if repo_path else Path("sample_repo")
    parts = []
    total_chars = 0
    if path_obj.exists():
        for file_path in sorted(path_obj.rglob("*.py")):
            if should_skip_path(file_path):
                continue
            try:
                if file_path.stat().st_size > MAX_FILE_SIZE_BYTES:
                    continue
                code = file_path.read_text(encoding="utf-8")
                header = f"# FILE: {file_path}\n"
                chunk = header + code
                parts.append(chunk)
                total_chars += len(chunk)
                if total_chars >= max_chars:
                    break
            except (UnicodeDecodeError, OSError):
                continue
    return "\n\n".join(parts)

if __name__ == "__main__":
    content = load_repo()
    print(f"Loaded {len(content)} characters from repo.")
