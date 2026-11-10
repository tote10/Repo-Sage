import os
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from dotenv import load_dotenv
from rag.hybrid import hybrid_search
from rag.agent_turn import run_agent_round_trip, StructuredAnswer

load_dotenv()

def build_prompt(question: str, context: str) -> str:
    return f"""You are a helpful coding assistant. Answer the QUESTION using ONLY the CODE context provided below.

CODE CONTEXT:
{context}

QUESTION: {question}

INSTRUCTIONS:
1. Answer the question based solely on the provided code.
2. If the answer is not in the code, say "I don't know."
3. At the very end of your response, you MUST provide a citations section formatted exactly like this:
SOURCES:
- file_path.py:start_line-end_line
"""

def parse_llm_response(raw_text: str) -> Tuple[str, List[str]]:
    parts = raw_text.split("SOURCES:")
    answer_text = parts[0].strip()
    citations = []
    if len(parts) > 1:
        sources_text = parts[1].strip()
        for line in sources_text.split("\n"):
            cleaned = line.strip()
            if cleaned.startswith("-"):
                citation = cleaned.lstrip("-").strip()
                if citation:
                    citations.append(citation)
    return answer_text, citations

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

    api_key = os.getenv("GROQ_API_KEY")
    if api_key:
        try:
            from groq import Groq
            client = Groq(api_key=api_key)
            response = client.chat.completions.create(
                model=os.getenv("LLM_MODEL", "llama-3.1-8b-instant"),
                messages=[{"role": "user", "content": prompt}],
            )
            raw_content = response.choices[0].message.content
            answer_text, parsed_citations = parse_llm_response(raw_content)
            citations = parsed_citations if parsed_citations else [c["citation"] for c in chunk_citations]
        except Exception as e:
            answer_text = f"Error querying model: {e}"
            citations = [c["citation"] for c in chunk_citations]
    else:
        # Fallback informative summary with citations when API key is not set
        if chunk_citations:
            best_chunk = chunk_citations[0]
            answer_text = (
                f"Based on code retrieval, relevant logic was found in {best_chunk['file']} "
                f"(lines {best_chunk['start_line']}–{best_chunk['end_line']})."
            )
            citations = [c["citation"] for c in chunk_citations]
        else:
            answer_text = "I don't know."
            citations = []

    # If the user question explicitly requests reading a file or grepping, or if tools mode is preferred
    # we can also record sources structured
    sources_structured = []
    for c in chunk_citations:
        sources_structured.append({
            "file": c["file"],
            "line": c["start_line"],
            "end_line": c["end_line"],
            "citation": c["citation"]
        })

    return {
        "question": question,
        "answer": answer_text,
        "citations": citations,
        "sources": sources_structured,
        "confidence": 0.9 if citations else 0.5,
        "chunks": chunk_citations
    }

if __name__ == "__main__":
    test_q = "where does the chunks changed to vectors?"
    res = ask(test_q, k=3)
    print("ANSWER:\n", res["answer"])
    print("\nCITATIONS:\n", res["citations"])
