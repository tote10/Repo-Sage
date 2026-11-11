import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from rag.tools import (
    READ_FILE_TOOL,
    sandbox_path,
    read_file,
    execute_tool_call,
    request_tool_call
)

REPO_ROOT = Path(__file__).parent.parent
SAMPLE_REPO = REPO_ROOT / "sample_repo"

def test_read_file_tool_schema():
    assert READ_FILE_TOOL["type"] == "function"
    assert READ_FILE_TOOL["function"]["name"] == "read_file"
    params = READ_FILE_TOOL["function"]["parameters"]
    assert "path" in params["properties"]
    assert "path" in params["required"]
    assert "start_line" in params["properties"]
    assert "end_line" in params["properties"]

def test_read_file_valid():
    output = read_file("auth.py", repo_path=SAMPLE_REPO)
    assert "1: import jwt" in output
    assert "def create_access_token" in output

def test_read_file_with_line_range():
    output = read_file("auth.py", repo_path=SAMPLE_REPO, start_line=1, end_line=3)
    lines = output.split("\n")
    assert len(lines) == 3
    assert lines[0].startswith("1: ")
    assert lines[1].startswith("2: ")
    assert lines[2].startswith("3: ")

def test_read_file_invalid_line_range():
    output = read_file("auth.py", repo_path=SAMPLE_REPO, start_line=99999, end_line=100000)
    assert "out of range" in output

def test_read_file_not_found():
    output = read_file("non_existent_file.py", repo_path=SAMPLE_REPO)
    assert "Error: File not found:" in output

def test_sandbox_path_allows_inside_repo():
    target = sandbox_path("auth.py", repo_path=SAMPLE_REPO)
    assert target.exists()
    assert target.samefile(SAMPLE_REPO / "auth.py")

def test_sandbox_path_blocks_escape():
    with pytest.raises(PermissionError):
        sandbox_path("../../etc/passwd", repo_path=SAMPLE_REPO)

    output = read_file("../../etc/passwd", repo_path=SAMPLE_REPO)
    assert "Error: Access denied" in output

def test_execute_tool_call():
    result = execute_tool_call("read_file", {"path": "auth.py", "start_line": 1, "end_line": 2}, repo_path=SAMPLE_REPO)
    assert "1: import jwt" in result
    assert "2: from datetime import datetime, timedelta" in result

def test_execute_tool_call_unknown():
    result = execute_tool_call("unknown_tool", {}, repo_path=SAMPLE_REPO)
    assert "Error: Unknown tool" in result

def test_request_tool_call_heuristic():
    call = request_tool_call("show me what's in auth.py", repo_path=SAMPLE_REPO)
    assert call is not None
    assert call["name"] == "read_file"
    assert call["arguments"]["path"] == "auth.py"

def test_request_tool_call_mock_groq():
    import sys
    mock_groq_mod = MagicMock()
    mock_choice = MagicMock()
    mock_tool_call = MagicMock()
    mock_tool_call.id = "call_123"
    mock_tool_call.function.name = "read_file"
    mock_tool_call.function.arguments = '{"path": "auth.py", "start_line": 1, "end_line": 10}'
    mock_choice.message.tool_calls = [mock_tool_call]
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_response
    mock_groq_mod.Groq.return_value = mock_client

    with patch.dict(sys.modules, {"groq": mock_groq_mod}):
        with patch.dict("os.environ", {"GROQ_API_KEY": "fake_key"}):
            call = request_tool_call("What is in auth.py?", repo_path=SAMPLE_REPO)
            assert call is not None
            assert call["name"] == "read_file"
            assert call["arguments"]["path"] == "auth.py"
            assert call["arguments"]["start_line"] == 1
