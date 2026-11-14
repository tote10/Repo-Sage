import os
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Union

logger = logging.getLogger("rag.tools")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

import re

READ_FILE_TOOL = {
    "type": "function",
    "function": {
        "name": "read_file",
        "description": "Read the contents of a file in the codebase, optionally specifying start and end line numbers. Output is formatted with line numbers.",
        "parameters": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Relative path of the file to read within the repository, e.g. 'sample_repo/auth.py' or 'auth.py'."
                },
                "start_line": {
                    "type": "integer",
                    "description": "Optional 1-based start line number to read from."
                },
                "end_line": {
                    "type": "integer",
                    "description": "Optional 1-based end line number to read up to (inclusive)."
                }
            },
            "required": ["path"]
        }
    }
}

GREP_TOOL = {
    "type": "function",
    "function": {
        "name": "grep",
        "description": "Search the codebase for a text pattern or regular expression, returning matching file:line occurrences. Sandboxed to the repository root.",
        "parameters": {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "The regex pattern or string to search for across files."
                },
                "path": {
                    "type": "string",
                    "description": "Optional relative subdirectory or file path to limit the search scope (defaults to entire repository)."
                },
                "max_matches": {
                    "type": "integer",
                    "description": "Maximum number of matching lines to return (defaults to 50, capped at 100)."
                }
            },
            "required": ["pattern"]
        }
    }
}

AVAILABLE_TOOLS = [READ_FILE_TOOL, GREP_TOOL]


def sandbox_path(relative_path: str, repo_path: Union[str, Path]) -> Path:
    """
    Resolves relative_path against repo_path and ensures it does not escape
    the repo boundary (prevents directory traversal attacks like ../).
    """
    repo = Path(repo_path).resolve()
    # Normalize path string to remove leading slashes if any
    clean_path = str(relative_path).lstrip("/")
    target = (repo / clean_path).resolve()

    if not (target == repo or repo in target.parents):
        raise PermissionError(f"Access denied: Path '{relative_path}' traverses outside repository root '{repo}'.")
    return target


def read_file(
    path: str,
    repo_path: Optional[Union[str, Path]] = None,
    start_line: Optional[int] = None,
    end_line: Optional[int] = None,
    max_lines: int = 500
) -> str:
    """
    Reads contents of a file inside repo_path with line numbers.
    Safely sandboxes path within the repository root.
    """
    if repo_path is None:
        repo_path = Path.cwd()
    else:
        repo_path = Path(repo_path)

    try:
        resolved = sandbox_path(path, repo_path)
    except PermissionError as e:
        logger.warning("Tool call error: %s", e)
        return f"Error: {e}"

    if not resolved.exists():
        logger.warning("read_file failed: File not found: %s", path)
        return f"Error: File not found: '{path}'."

    if not resolved.is_file():
        logger.warning("read_file failed: Not a regular file: %s", path)
        return f"Error: Path is not a file: '{path}'."

    try:
        with open(resolved, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except Exception as e:
        logger.error("read_file failed reading %s: %s", path, e)
        return f"Error reading file '{path}': {e}"

    total_lines = len(lines)
    s_line = max(1, start_line) if start_line is not None else 1
    e_line = min(total_lines, end_line) if end_line is not None else total_lines

    if s_line > total_lines:
        return f"File '{path}' has {total_lines} lines. Requested start_line {s_line} is out of range."

    if e_line < s_line:
        e_line = s_line

    if (e_line - s_line + 1) > max_lines:
        e_line = s_line + max_lines - 1
        truncated_note = f"\n[Output truncated at {max_lines} lines]"
    else:
        truncated_note = ""

    formatted_lines = [
        f"{idx}: {lines[idx - 1].rstrip()}"
        for idx in range(s_line, e_line + 1)
    ]
    content = "\n".join(formatted_lines) + truncated_note
    return content


def grep(
    pattern: str,
    path: Optional[str] = None,
    repo_path: Optional[Union[str, Path]] = None,
    max_matches: int = 50,
    case_sensitive: bool = False
) -> str:
    """
    Searches the repository for occurrences of `pattern`.
    Safely sandboxes file traversal within `repo_path`.
    Limits results to avoid context overflow.
    """
    if repo_path is None:
        repo_path = Path.cwd()
    else:
        repo_path = Path(repo_path)

    base_dir = repo_path
    if path:
        try:
            base_dir = sandbox_path(path, repo_path)
        except PermissionError as e:
            logger.warning("grep sandbox error: %s", e)
            return f"Error: {e}"

    if not base_dir.exists():
        logger.warning("grep path not found: %s", path or str(repo_path))
        return f"Error: Path not found: '{path}'."

    # Validate pattern
    flags = 0 if case_sensitive else re.IGNORECASE
    try:
        regex = re.compile(pattern, flags)
    except re.error as e:
        logger.warning("grep invalid regex pattern '%s': %s", pattern, e)
        return f"Error: Invalid regex pattern '{pattern}': {e}"

    max_limit = min(max(1, max_matches), 100)
    matches: List[str] = []

    ignored_dirs = {".git", "__pycache__", ".venv", "venv", ".pytest_cache", "node_modules", ".tox"}

    # Determine files to search
    if base_dir.is_file():
        files_to_search = [base_dir]
    else:
        files_to_search = []
        for root, dirs, files in os.walk(base_dir):
            dirs[:] = [d for d in dirs if d not in ignored_dirs and not d.startswith(".")]
            for file in files:
                if file.startswith("."):
                    continue
                files_to_search.append(Path(root) / file)

    truncated = False
    for file_path in sorted(files_to_search):
        if len(matches) >= max_limit:
            truncated = True
            break

        try:
            try:
                rel_path = file_path.relative_to(repo_path)
            except ValueError:
                rel_path = file_path

            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                for line_num, line in enumerate(f, start=1):
                    if regex.search(line):
                        clean_line = line.strip()
                        # Cap line length to prevent huge minified files from bloating context
                        if len(clean_line) > 200:
                            clean_line = clean_line[:197] + "..."
                        matches.append(f"{rel_path}:{line_num}: {clean_line}")
                        if len(matches) >= max_limit:
                            truncated = True
                            break
        except Exception as e:
            logger.debug("grep skipping file %s due to error: %s", file_path, e)
            continue

    if not matches:
        return f"No matches found for pattern: '{pattern}'"

    output = "\n".join(matches)
    if truncated:
        output += f"\n[Output capped at {max_limit} matches]"
    return output


def execute_tool_call(tool_name: str, arguments: Dict[str, Any], repo_path: Optional[Union[str, Path]] = None) -> str:
    """
    Executes a recognized tool and logs the invocation details.
    """
    logger.info("Executing tool: %s with args: %s", tool_name, arguments)
    if tool_name == "read_file":
        path = arguments.get("path", "")
        start_line = arguments.get("start_line")
        end_line = arguments.get("end_line")
        result = read_file(path=path, repo_path=repo_path, start_line=start_line, end_line=end_line)
        logger.info("Executed tool %s for '%s' -> %d characters returned", tool_name, path, len(result))
        return result
    elif tool_name == "grep":
        pattern = arguments.get("pattern", "")
        path = arguments.get("path")
        max_matches = arguments.get("max_matches", 50)
        result = grep(pattern=pattern, path=path, repo_path=repo_path, max_matches=max_matches)
        logger.info("Executed tool %s for pattern '%s' -> %d characters returned", tool_name, pattern, len(result))
        return result
    else:
        err = f"Error: Unknown tool '{tool_name}'."
        logger.warning(err)
        return err


def request_tool_call(question: str, repo_path: Optional[Union[str, Path]] = None) -> Optional[Dict[str, Any]]:
    """
    Asks the LLM with tool definitions to see if it requests calling a tool.
    Returns the parsed tool call dict (name, arguments) if requested, or None.
    If no API key is available or LLM is unreachable, falls back to detecting
    read_file and grep intent for standard queries.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if api_key:
        try:
            from groq import Groq
            client = Groq(api_key=api_key)
            messages = [
                {"role": "system", "content": "You are a code assistant with access to tools. When asked to inspect, find, search or read files, call the appropriate tool."},
                {"role": "user", "content": question}
            ]
            response = client.chat.completions.create(
                model=os.getenv("LLM_MODEL", "llama-3.1-8b-instant"),
                messages=messages,
                tools=AVAILABLE_TOOLS,
                tool_choice="auto"
            )
            message = response.choices[0].message
            if message.tool_calls:
                call = message.tool_calls[0]
                args = json.loads(call.function.arguments) if isinstance(call.function.arguments, str) else call.function.arguments
                logger.info("Model requested tool call: %s with args: %s", call.function.name, args)
                return {
                    "id": getattr(call, "id", None),
                    "name": call.function.name,
                    "arguments": args
                }
        except Exception as e:
            logger.warning("Error querying model for tool calls: %s", e)

    # Heuristic fallback for testing and offline operation
    q_lower = question.lower()
    if any(k in q_lower for k in ["grep", "search for", "find all occurrences", "where is", "find references"]):
        # Extract pattern heuristically if enclosed in quotes or trailing word
        import re
        quotes = re.findall(r"['\"`]([^'\"`]+)['\"`]", question)
        if quotes:
            pattern = quotes[0]
        else:
            words = question.strip("?!.").split()
            pattern = words[-1] if words else ""
        if pattern:
            logger.info("Heuristic detected grep intent for '%s'", pattern)
            return {
                "name": "grep",
                "arguments": {"pattern": pattern}
            }

    if "read" in q_lower or "show" in q_lower or "what's in" in q_lower or "whats in" in q_lower:
        # Check if a filename ends with common code extensions
        words = question.replace("'", " ").replace('"', " ").replace("`", " ").split()
        for w in words:
            clean_word = w.strip(".,;:?!")
            if any(clean_word.endswith(ext) for ext in [".py", ".md", ".json", ".txt", ".toml", ".yml", ".yaml"]):
                logger.info("Heuristic detected read_file intent for %s", clean_word)
                return {
                    "name": "read_file",
                    "arguments": {"path": clean_word}
                }
    return None
