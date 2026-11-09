import os
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from rag.search import search

load_dotenv()

def build_prompt(question: str, context: str) -> str:
    return f"""Here is a codebase. Answer using ONLY this code. Cite
  the file and line numbers you used.

  CODE:
  {context}

  QUESTION: {question}"""

def ask(question: str, k: int = 5, repo_path: Optional[str] = None) -> Dict[str, Any]:
    results = search(question, k=k, repo_path=repo_path)
    context_parts = []
    citations = []

    for score, chunk in results:
        file_path = chunk["file"]
        start_line = chunk["start_line"]
        end_line = chunk["end_line"]
        citation_str = f"{file_path}:{start_line}-{end_line}"
        citations.append({
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
            answer_text = response.choices[0].message.content
        except Exception as e:
            answer_text = f"Error querying model: {e}"
    else:
        # Fallback informative summary with citations when API key is not set
        if citations:
            best_chunk = citations[0]
            answer_text = (
                f"Based on code retrieval, relevant logic was found in {best_chunk['file']} "
                f"(lines {best_chunk['start_line']}–{best_chunk['end_line']})."
            )
        else:
            answer_text = "I don't know. No relevant code found in the repository."

    return {
        "question": question,
        "answer": answer_text,
        "citations": [c["citation"] for c in citations],
        "chunks": citations
    }

if __name__ == "__main__":
    test_q = "where does the chunks changed to vectors?"
    res = ask(test_q, k=3)
    print("Answer:", res["answer"])
    print("Citations:", res["citations"])
