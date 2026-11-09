# Week 4 Action Plan: Smart Chunking & Citations

This document contains every detail and exact step needed to finish your current position in the project (Week 4, Days 3-5). Follow these steps to implement structured citations, A/B testing, and indexing hygiene.

---

## 1. Structured Citations (Day 3)
**File to edit:** `rag/ask.py`

**The Struggle:** Grounding the LLM to prevent hallucinations.
**The Focus:** Changing the prompt and parsing out the exact sources.

**Detailed Steps:**
1. **Update the Prompt:** You need to explicitly demand a structured output format at the very end of the response. Update your `prompt` string in `ask.py` to look like this:

```python
prompt = f"""You are a helpful coding assistant. Answer the QUESTION using ONLY the CODE context provided below.

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
```

2. **Parse the Output:** After getting `response.choices[0].message.content`, don't just print it. Split the text to extract the sources.

```python
raw_response = response.choices[0].message.content
parts = raw_response.split("SOURCES:")

answer_text = parts[0].strip()
print(f"ANSWER:\n{answer_text}\n")

if len(parts) > 1:
    sources_text = parts[1].strip()
    print("CITATIONS:")
    # Parse the list of sources
    for line in sources_text.split('\n'):
        if line.strip().startswith('-'):
            print(f"Verified Source -> {line.strip('- ').strip()}")
```

---

## 2. A/B Testing: Dumb vs Smart Chunking (Day 4)
**File to edit:** New script or just mental check.

**The Struggle:** Measuring subjective quality without automated evaluations.
**The Focus:** Proving AST parsing is better than fixed character slices.

**Detailed Steps:**
1. Pick 5 questions (e.g., "Where are chunks changed to vectors?", "How does search work?", "What skips directories in chunking?").
2. Run these questions against your current AST implementation. Note if the chunks returned actually contain the whole function needed to answer it.
3. Compare it in your head to Week 3 (when a chunk was just 800 characters and might cut a function in half).
4. **Done check:** Just verify that your AST chunks are pulling in coherent, complete Python functions.

---

## 3. Re-Index Hygiene (Day 5)
**File to edit:** `app/api/routes.py` (and potentially `app/main.py`)

**The Struggle:** Idempotency (running the same action twice shouldn't break things).
**The Focus:** Making an API route to trigger the indexing process cleanly.

**Detailed Steps:**
1. Create or open your FastAPI routes file (`app/api/routes.py`).
2. Add an `/index` POST route.
3. Import your `chunk_repo` logic and vector embedding logic here.

```python
from fastapi import APIRouter
from rag.chunk import chunk_repo
# from rag.embed import your_embed_function
# from rag.search import clear_index  # You will need a function to wipe the old index

router = APIRouter()

@router.post("/index")
def reindex_codebase():
    # 1. Clear the existing index to ensure IDEMPOTENCY
    # clear_index()  <- Implement a way to wipe your old vector data/DB

    # 2. Extract new chunks
    chunks = chunk_repo()

    # 3. Embed and store the chunks
    # for chunk in chunks:
    #     save_to_vector_db(chunk)

    return {"status": "success", "chunks_indexed": len(chunks)}
```

**Why clear the index?** Because if you run `/index` twice without clearing, you will have two copies of `chunk.py` in your database. This messes up your retrieval scores.

---
### Next Actions
1. Open [`rag/ask.py`](file:///c:/Users/admin/Desktop/Repo-Sage/rag/ask.py).
2. Copy the prompt and parsing logic from Section 1 into it.
3. Run `python rag/ask.py` to see if the LLM correctly lists `SOURCES:` at the bottom.
