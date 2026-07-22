from pathlib import Path

parts = []
def load_repo():
    for path in Path("sample_repo").rglob("*.py"):
        code = path.read_text(encoding="utf-8")
        header = f"# FILE: {path}\n"
        parts.append(header + code)
    return "\n\n".join(parts)
