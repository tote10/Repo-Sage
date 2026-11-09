from pathlib import Path
from typing import Optional, Union

def load_repo(repo_path: Optional[Union[str, Path]] = None) -> str:
    path_obj = Path(repo_path) if repo_path else Path("sample_repo")
    parts = []
    if path_obj.exists():
        for file_path in sorted(path_obj.rglob("*.py")):
            try:
                code = file_path.read_text(encoding="utf-8")
                header = f"# FILE: {file_path}\n"
                parts.append(header + code)
            except (UnicodeDecodeError, OSError):
                continue
    return "\n\n".join(parts)

if __name__ == "__main__":
    content = load_repo()
    print(f"Loaded {len(content)} characters from repo.")
