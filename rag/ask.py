import os
import json
import re
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError
from rag.hybrid import hybrid_search

load_dotenv()

class SourceCitation(BaseModel):
    file: str
    line: Optional[int] = None
    lines: Optional[str] = None

class StructuredAnswer(BaseModel):
    answer: str
    sources: List[SourceCitation] = Field(default_factory=list)
    confidence: Optional[float] = Field(default=1.0, ge=0.0, le=1.0)

def build_prompt(question: str, context: str) -> str:
    return f"""You are a helpful coding assistant. Answer the QUESTION using ONLY the CODE context provided below.

CODE CONTEXT:
{context}

QUESTION: {question}

INSTRUCTIONS:
1. Answer the question based solely on the provided code.
2. If the answer is not in the code, say "I don't know."
3. You MUST return your response as a valid JSON object strictly matching this schema:
{{
  "answer": "Clear explanation answering the question",
  "sources": [
    {{"file": "path/to/file.py", "lines": "10-25"}}
  ],
  "confidence": 0.95
}}
Do NOT include markdown formatting or extra text outside the JSON object.
"""

def _parse_source_citation_str(citation_str: str) -> SourceCitation:
    """Helper to convert 'file.py:start-end' or 'file.py:line' into SourceCitation."""
    if ":" in citation_str:
        file_part, lines_part = citation_str.rsplit(":", 1)
        line_num: Optional[int] = None
        if "-" in lines_part:
            start_num = lines_part.split("-")[0]
            if start_num.isdigit():
                line_num = int(start_num)
        elif lines_part.isdigit():
            line_num = int(lines_part)
        return SourceCitation(file=file_part, line=line_num, lines=lines_part)
    return SourceCitation(file=citation_str)

def parse_structured_response(raw_text: str, fallback_citations: Optional[List[str]] = None) -> StructuredAnswer:
    """Parses raw LLM text into a validated StructuredAnswer model."""
    fallback_sources = [_parse_source_citation_str(c) for c in (fallback_citations or [])]
    text = raw_text.strip()

    # Strip code block wrapping if present (e.g. ```json ... ```)
    if "```" in text:
        match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        if match:
            text = match.group(1).strip()

    try:
        data = json.loads(text)
        if isinstance(data, dict):
            # Normalize sources if needed
            normalized_sources: List[Dict[str, Any]] = []
            for s in data.get("sources", []):
                if isinstance(s, dict):
                    normalized_sources.append(s)
                elif isinstance(s, str):
                    c = _parse_source_citation_str(s)
                    normalized_sources.append(c.model_dump())
            data["sources"] = normalized_sources
            return StructuredAnswer.model_validate(data)
    except Exception:
        pass

    # If JSON parsing failed, check if it used the legacy SOURCES: format or free text
    parts = raw_text.split("SOURCES:")
    answer_text = parts[0].strip()
    sources: List[SourceCitation] = []
    if len(parts) > 1:
        sources_text = parts[1].strip()
        for line in sources_text.split("\n"):
            cleaned = line.strip()
            if cleaned.startswith("-"):
                citation = cleaned.lstrip("-").strip()
                if citation:
                    sources.append(_parse_source_citation_str(citation))

    if not sources and fallback_sources:
        sources = fallback_sources

    return StructuredAnswer(
        answer=answer_text if answer_text else raw_text.strip(),
        sources=sources,
        confidence=0.8 if sources else 0.2
    )

def ask(question: str, k: int = 5, repo_path: Optional[str] = None) -> Dict[str, Any]:
    # Default to hybrid search (Vector + BM25 + Rerank)
    results = hybrid_search(question, k=k, repo_path=repo_path)
    context_parts = []
    chunk_citations = []

    for score, chunk in results:
        file_path = chunk["file"]
        start_line = chunk["start_line"]
        end_line = chunk["end_line"]
        citation_str = f"{file_path}:{start_line}-{end_line}"
        chunk_citations.append({
            "file": file_path,
            "start_line": start_line,
            "end_line": end_line,
            "score": round(float(score), 4),
            "citation": citation_str,
            "name": chunk.get("name"),
            "type": chunk.get("type")
        })
        context_parts.append(f"File: {file_path} (lines {start_line}-{end_line}):\n{chunk['text']}\n")

    context = "\n".join(context_parts)
    prompt = build_prompt(question, context)
    default_citations = [c["citation"] for c in chunk_citations]

    api_key = os.getenv("GROQ_API_KEY")
    if api_key:
        try:
            from groq import Groq
            client = Groq(api_key=api_key)
            response = client.chat.completions.create(
                model=os.getenv("LLM_MODEL", "llama-3.1-8b-instant"),
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            raw_content = response.choices[0].message.content
            structured_res = parse_structured_response(raw_content, fallback_citations=default_citations)
        except Exception as e:
            fallback_sources = [_parse_source_citation_str(c) for c in default_citations]
            structured_res = StructuredAnswer(
                answer=f"Error querying model: {e}",
                sources=fallback_sources,
                confidence=0.0
            )
    else:
        # Fallback informative summary with citations when API key is not set
        if chunk_citations:
            best_chunk = chunk_citations[0]
            answer_text = (
                f"Based on code retrieval, relevant logic was found in {best_chunk['file']} "
                f"(lines {best_chunk['start_line']}–{best_chunk['end_line']})."
            )
            fallback_sources = [
                SourceCitation(
                    file=c["file"],
                    line=c["start_line"],
                    lines=f"{c['start_line']}-{c['end_line']}"
                )
                for c in chunk_citations
            ]
            structured_res = StructuredAnswer(
                answer=answer_text,
                sources=fallback_sources,
                confidence=1.0
            )
        else:
            structured_res = StructuredAnswer(
                answer="I don't know.",
                sources=[],
                confidence=0.0
            )

    # Legacy formatted citations string list for backwards compatibility
    legacy_citations = []
    for s in structured_res.sources:
        if s.lines:
            legacy_citations.append(f"{s.file}:{s.lines}")
        elif s.line:
            legacy_citations.append(f"{s.file}:{s.line}")
        else:
            legacy_citations.append(s.file)
    if not legacy_citations and default_citations:
        legacy_citations = default_citations

    return {
        "question": question,
        "answer": structured_res.answer,
        "sources": [s.model_dump() for s in structured_res.sources],
        "confidence": structured_res.confidence,
        "citations": legacy_citations,
        "chunks": chunk_citations
    }

if __name__ == "__main__":
    test_q = "where does the chunks changed to vectors?"
    res = ask(test_q, k=3)
    print("ANSWER:\n", res["answer"])
    print("\nCITATIONS:\n", res["citations"])
