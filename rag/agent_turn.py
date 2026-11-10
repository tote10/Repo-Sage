import os
import json
import logging
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ValidationError
from rag.tools import read_file, grep, TOOLS_SCHEMA, get_tool_call_logs

logger = logging.getLogger("rag.agent")
if not logger.handlers:
    logging.basicConfig(level=logging.INFO)


class SourceRef(BaseModel):
    file: str = Field(description="Relative path of the source file")
    line: Optional[int] = Field(default=None, description="Relevant line number if known")
    end_line: Optional[int] = Field(default=None, description="Relevant ending line number if known")
    citation: Optional[str] = Field(default=None, description="Formatted citation string e.g. 'file.py:10-20'")


class ToolCallRecord(BaseModel):
    tool: str
    args: Dict[str, Any]
    result_size_chars: int
    result_size_lines: int


class StructuredAnswer(BaseModel):
    answer: str = Field(description="Answer text to the user's question")
    sources: List[SourceRef] = Field(default_factory=list, description="List of source references cited in the answer")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")
    tool_calls: List[ToolCallRecord] = Field(default_factory=list, description="Tools invoked during answering")


STRUCTURED_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "answer": {"type": "string", "description": "The concise, accurate answer to the question."},
        "sources": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "file": {"type": "string"},
                    "line": {"type": "integer"},
                    "end_line": {"type": "integer"},
                    "citation": {"type": "string"}
                },
                "required": ["file"]
            },
            "description": "List of exact source files and line numbers cited."
        },
        "confidence": {
            "type": "number",
            "minimum": 0.0,
            "maximum": 1.0,
            "description": "Confidence score from 0.0 to 1.0"
        }
    },
    "required": ["answer", "sources", "confidence"]
}


SYSTEM_PROMPT = """You are repo-sage, an expert software repository agent.
You have access to tools:
1. `read_file(path)` - inspect file content by path.
2. `grep(pattern)` - find matches across the repository.

You can request a tool call if you need to read code or search files.
When you are ready to answer the user's question, you MUST return a valid JSON object matching this schema:
{
  "answer": "string",
  "sources": [{"file": "path/to/file.py", "line": 10, "end_line": 20, "citation": "path/to/file.py:10-20"}],
  "confidence": 0.95
}
Do not wrap your final JSON in markdown backticks or commentary. Only return the raw JSON object.
"""


def execute_tool(tool_name: str, args: Dict[str, Any], repo_path: str) -> str:
    """Executes sandboxed tools by name."""
    if tool_name == "read_file":
        path = args.get("path", "")
        return read_file(path, repo_path=repo_path)
    elif tool_name == "grep":
        pattern = args.get("pattern", "")
        case_sensitive = args.get("case_sensitive", False)
        return grep(pattern, repo_path=repo_path, case_sensitive=case_sensitive)
    else:
        return f"Error: Unknown tool '{tool_name}'."


def fallback_structured_answer(question: str, repo_path: str, tool_records: List[ToolCallRecord]) -> StructuredAnswer:
    """
    Fallback deterministic solver for offline/test environments without Groq API key.
    Inspects question for file or search intent, performs single tool call if appropriate,
    and returns a validated StructuredAnswer.
    """
    q_lower = question.lower()
    sources: List[SourceRef] = []

    # Heuristic: check if user asks to read/inspect a specific file
    file_candidates = ["auth.py", "database.py", "main.py", "models.py", "utils.py"]
    target_file = None
    for cand in file_candidates:
        if cand in q_lower or cand.replace(".py", "") in q_lower:
            target_file = cand
            break

    if target_file:
        res = read_file(target_file, repo_path=repo_path)
        tool_records.append(ToolCallRecord(
            tool="read_file",
            args={"path": target_file},
            result_size_chars=len(res),
            result_size_lines=res.count("\n") + 1
        ))
        answer = f"Inspected {target_file}. Found implementation details in {target_file}."
        sources.append(SourceRef(file=target_file, line=1, citation=f"{target_file}:1"))
        return StructuredAnswer(answer=answer, sources=sources, confidence=0.9, tool_calls=tool_records)

    # Heuristic: check if grep pattern makes sense
    words = [w for w in question.split() if len(w) > 3 and w.lower() not in ("what", "where", "how", "show", "find", "code")]
    pattern = words[0] if words else "def "
    grep_res = grep(pattern, repo_path=repo_path)
    tool_records.append(ToolCallRecord(
        tool="grep",
        args={"pattern": pattern},
        result_size_chars=len(grep_res),
        result_size_lines=grep_res.count("\n") + 1
    ))

    first_line = grep_res.splitlines()[0] if grep_res.strip() else ""
    if ":" in first_line:
        f_part, l_part, *_ = first_line.split(":")
        try:
            line_num = int(l_part)
        except ValueError:
            line_num = 1
        sources.append(SourceRef(file=f_part, line=line_num, citation=f"{f_part}:{line_num}"))
        answer = f"Found matches for '{pattern}' in {f_part}."
        confidence = 0.85
    else:
        answer = f"No direct definitions found for '{pattern}'."
        confidence = 0.5

    return StructuredAnswer(answer=answer, sources=sources, confidence=confidence, tool_calls=tool_records)


def run_agent_round_trip(question: str, repo_path: Optional[str] = None) -> StructuredAnswer:
    """
    Executes a single tool round-trip turn:
    1. Send user question + tool declarations to LLM.
    2. If LLM requests a tool call:
       - Execute tool safely in repo sandbox
       - Feed tool result back to LLM in message history
       - Request final answer from LLM
    3. Validate and parse response as StructuredAnswer with Pydantic.
    """
    target_repo = repo_path or os.getenv("REPO_PATH", "./sample_repo")
    api_key = os.getenv("GROQ_API_KEY")
    tool_records: List[ToolCallRecord] = []

    if not api_key:
        return fallback_structured_answer(question, target_repo, tool_records)

    try:
        from groq import Groq
        client = Groq(api_key=api_key)
        model = os.getenv("LLM_MODEL", "llama-3.1-8b-instant")

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question}
        ]

        # First turn: model may call a tool or answer directly
        first_resp = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=TOOLS_SCHEMA,
            tool_choice="auto"
        )

        choice = first_resp.choices[0]
        message = choice.message

        if message.tool_calls:
            # Execute the first tool call (single round-trip turn as per Day 4)
            t_call = message.tool_calls[0]
            func_name = t_call.function.name
            try:
                func_args = json.loads(t_call.function.arguments)
            except Exception:
                func_args = {}

            tool_result = execute_tool(func_name, func_args, target_repo)
            record = ToolCallRecord(
                tool=func_name,
                args=func_args,
                result_size_chars=len(tool_result),
                result_size_lines=tool_result.count("\n") + 1
            )
            tool_records.append(record)

            # Feed back the tool turn into messages
            messages.append(message)
            messages.append({
                "role": "tool",
                "tool_call_id": t_call.id,
                "name": func_name,
                "content": tool_result
            })

            # Second turn: get the final structured JSON answer
            second_resp = client.chat.completions.create(
                model=model,
                messages=messages,
                response_format={"type": "json_object"}
            )
            final_raw = second_resp.choices[0].message.content
        else:
            final_raw = message.content

        # Parse and validate structured JSON
        clean_json = final_raw.strip()
        if clean_json.startswith("```json"):
            clean_json = clean_json[7:]
        if clean_json.startswith("```"):
            clean_json = clean_json[3:]
        if clean_json.endswith("```"):
            clean_json = clean_json[:-3]
        clean_json = clean_json.strip()

        parsed_data = json.loads(clean_json)
        parsed_data["tool_calls"] = [r.model_dump() for r in tool_records]
        return StructuredAnswer.model_validate(parsed_data)

    except (json.JSONDecodeError, ValidationError) as parse_err:
        logger.warning("Failed structured output validation, falling back: %s", parse_err)
        return StructuredAnswer(
            answer=f"Could not parse valid structured answer: {parse_err}",
            sources=[],
            confidence=0.0,
            tool_calls=tool_records
        )
    except Exception as e:
        logger.error("LLM agent turn failed: %s", e)
        return fallback_structured_answer(question, target_repo, tool_records)
