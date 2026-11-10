import pytest
from pathlib import Path
from rag.tools import read_file, grep, resolve_and_sandbox_path, get_tool_call_logs, clear_tool_call_logs


def test_resolve_and_sandbox_path_valid():
    repo = Path("./sample_repo").resolve()
    safe_path = resolve_and_sandbox_path("auth.py", str(repo))
    assert safe_path == repo / "auth.py"


def test_resolve_and_sandbox_path_escape_traversal():
    repo = Path("./sample_repo").resolve()
    with pytest.raises(PermissionError):
        resolve_and_sandbox_path("../../etc/passwd", str(repo))

    with pytest.raises(PermissionError):
        resolve_and_sandbox_path("../requirements.txt", str(repo))


def test_read_file_success():
    clear_tool_call_logs()
    output = read_file("auth.py", repo_path="./sample_repo")
    assert "import jwt" in output
    assert "1 |" in output

    logs = get_tool_call_logs()
    assert len(logs) == 1
    assert logs[0]["tool"] == "read_file"
    assert logs[0]["args"]["path"] == "auth.py"
    assert logs[0]["result_size_chars"] > 0


def test_read_file_security_escape():
    clear_tool_call_logs()
    output = read_file("../../etc/passwd", repo_path="./sample_repo")
    assert "Access denied" in output or "Error" in output


def test_read_file_not_found():
    clear_tool_call_logs()
    output = read_file("non_existent_file.py", repo_path="./sample_repo")
    assert "Error: File 'non_existent_file.py' does not exist." in output


def test_read_file_truncation():
    clear_tool_call_logs()
    output = read_file("auth.py", repo_path="./sample_repo", max_lines=5)
    assert "Truncated" in output
    lines = output.strip().splitlines()
    assert len([l for l in lines if "|" in l]) <= 5


def test_grep_matches():
    clear_tool_call_logs()
    result = grep("def ", repo_path="./sample_repo")
    assert "auth.py" in result
    assert "main.py" in result

    logs = get_tool_call_logs()
    assert len(logs) == 1
    assert logs[0]["tool"] == "grep"
    assert logs[0]["args"]["pattern"] == "def "


def test_grep_no_matches():
    clear_tool_call_logs()
    result = grep("xyz_non_existent_pattern_12345", repo_path="./sample_repo")
    assert "No matches found" in result


def test_grep_truncation_limits():
    clear_tool_call_logs()
    result = grep("e", repo_path="./sample_repo", max_matches=3)
    assert "Truncated" in result
