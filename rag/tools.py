import os
import re
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

logger = logging.getLogger("rag.tools")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)

DEFAULT_MAX_FILE_CHARS = 10000
DEFAULT_MAX_FILE_LINES = 500
DEFAULT_MAX_GREP_MATCHES = 30
DEFAULT_MAX_GREP_OUTPUT_CHARS = 8000

# Registry of logged tool calls for observability
TOOL_CALL_LOGS: List[Dict[str, Any]] = []


def log_tool_call(tool_name: str, args: Dict[str, Any], result: str) -> Dict[str, Any]:
    entry = {
        "tool": tool_name,
        "args": args,
        "result_size_chars": len(result),
        "result_size_lines": result.count("\n") + (1 if result else 0),
    }
    TOOL_CALL_LOGS.append(entry)
    logger.info("Executed tool %s with args %s -> result size %d chars", tool_name, args, len(result))
    return entry


def get_tool_call_logs() -> List[Dict[str, Any]]:
    return list(TOOL_CALL_LOGS)


def clear_tool_call_logs() -> None:
    TOOL_CALL_LOGS.clear()


def resolve_and_sandbox_path(relative_or_absolute_path: str, repo_path: str) -> Path:
    """
    Safely resolves a file path against repo_path, ensuring it cannot escape
    the repository root (e.g. through '..' traversal or absolute symlinks).
    """
    base_dir = Path(repo_path).resolve()
    target_path = Path(relative_or_absolute_path)

    if not target_path.is_absolute():
        resolved_path = (base_dir / target_path).resolve()
    else:
        resolved_path = target_path.resolve()

    # Sandboxing check: resolved_path must be strictly relative to base_dir
    try:
        resolved_path.relative_to(base_dir)
    except ValueError:
        raise PermissionError(f"Access denied: path '{relative_or_absolute_path}' escapes repository root.")

    return resolved_path


def read_file(
    path: str,
    repo_path: Optional[str] = None,
    max_chars: int = DEFAULT_MAX_FILE_CHARS,
    max_lines: int = DEFAULT_MAX_FILE_LINES,
) -> str:
    """
    Reads a file inside the repository with line numbers, capped to max_chars and max_lines.
    Prevents path traversal attacks.
    """
    target_repo = repo_path or os.getenv("REPO_PATH", "./sample_repo")
    args = {"path": path, "repo_path": target_repo}

    try:
        safe_path = resolve_and_sandbox_path(path, target_repo)
    except PermissionError as pe:
        res = f"Error: {pe}"
        log_tool_call("read_file", args, res)
        return res

    if not safe_path.exists():
        res = f"Error: File '{path}' does not exist."
        log_tool_call("read_file", args, res)
        return res

    if not safe_path.is_file():
        res = f"Error: '{path}' is not a regular file."
        log_tool_call("read_file", args, res)
        return res

    try:
        content = safe_path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        res = f"Error reading file '{path}': {e}"
        log_tool_call("read_file", args, res)
        return res

    lines = content.splitlines()
    capped_lines = lines[:max_lines]

    formatted_lines = [f"{i + 1:4d} | {line}" for i, line in enumerate(capped_lines)]
    output = "\n".join(formatted_lines)

    if len(lines) > max_lines:
        output += f"\n... [Truncated: {len(lines) - max_lines} more lines omitted]"

    if len(output) > max_chars:
        output = output[:max_chars] + "\n... [Truncated: output size limit reached]"

    log_tool_call("read_file", args, output)
    return output


def grep(
    pattern: str,
    repo_path: Optional[str] = None,
    max_matches: int = DEFAULT_MAX_GREP_MATCHES,
    max_chars: int = DEFAULT_MAX_GREP_OUTPUT_CHARS,
    case_sensitive: bool = False,
) -> str:
    """
    Searches for a pattern across files in the repository.
    Returns bounded 'file:line: match_text' matches.
    """
    target_repo = repo_path or os.getenv("REPO_PATH", "./sample_repo")
    args = {"pattern": pattern, "repo_path": target_repo, "case_sensitive": case_sensitive}

    try:
        base_dir = Path(target_repo).resolve()
        if not base_dir.exists() or not base_dir.is_dir():
            res = f"Error: Repository directory '{target_repo}' does not exist or is not a directory."
            log_tool_call("grep", args, res)
            return res
    except Exception as e:
        res = f"Error resolving repository path: {e}"
        log_tool_call("grep", args, res)
        return res

    flags = 0 if case_sensitive else re.IGNORECASE
    try:
        compiled_regex = re.compile(pattern, flags)
    except re.error as re_err:
        res = f"Error: Invalid regular expression '{pattern}': {re_err}"
        log_tool_call("grep", args, res)
        return res

    matches: List[str] = []
    total_matches_found = 0

    # Walk through directory ignoring hidden dirs (.git, etc.)
    for root, dirs, files in os.walk(base_dir):
        # Exclude hidden directories, cache directories, virtual environments
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("venv", "node_modules", "__pycache__", "dist", "build")]

        for file_name in files:
            if file_name.startswith("."):
                continue

            file_path = Path(root) / file_name
            # Security double-check: ensure file resolves within base_dir
            try:
                resolve_and_sandbox_path(str(file_path), str(base_dir))
            except PermissionError:
                continue

            try:
                # Read line by line to keep memory bounded
                with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                    for line_idx, line in enumerate(f, start=1):
                        if compiled_regex.search(line):
                            total_matches_found += 1
                            if len(matches) < max_matches:
                                rel_path = file_path.relative_to(base_dir)
                                clean_line = line.strip()
                                # Cap single line preview length
                                if len(clean_line) > 200:
                                    clean_line = clean_line[:197] + "..."
                                matches.append(f"{rel_path}:{line_idx}: {clean_line}")
            except Exception:
                continue

    if not matches:
        res = f"No matches found for pattern '{pattern}'."
        log_tool_call("grep", args, res)
        return res

    output = "\n".join(matches)
    if total_matches_found > len(matches):
        output += f"\n... [Truncated: {total_matches_found - len(matches)} more matches omitted]"

    if len(output) > max_chars:
        output = output[:max_chars] + "\n... [Truncated: output size limit reached]"

    log_tool_call("grep", args, output)
    return output


TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file inside the repository with line numbers. Use this tool when you know the file path and need to inspect its exact implementation or specific lines.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The relative path of the file to read (e.g., 'auth/login.py'). Cannot escape the repository root.",
                    }
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "grep",
            "description": "Search the repository codebase for a regular expression or substring pattern. Returns matching files and line numbers (file:line).",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "The text pattern or regular expression to search for across the repository.",
                    },
                    "case_sensitive": {
                        "type": "boolean",
                        "description": "Whether the search should be case sensitive. Defaults to false.",
                    },
                },
                "required": ["pattern"],
            },
        },
    },
]
