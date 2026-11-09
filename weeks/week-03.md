# Week 3 — Naive RAG: chunk → embed → retrieve

**Phase 2 — Retrieval / RAG (the heart).** Maps to backend-ai-roadmap: *07 RAG.*

> **The struggle (= the learning):** why naive RAG already beats "stuff the whole repo," and
> why it's *still* dumb. This is the deep end. The goal this week is the full pipeline working
> end-to-end, even crudely: cut code into pieces, turn each into numbers, store them, and at
> question time fetch only the few relevant pieces to send to the LLM.

---

## Day 1 — Chunking, the crude way
- **Goal:** cut your code text into pieces.
- **Try it:** split each file into fixed-size chunks (e.g. ~800 characters, with a little
  overlap). Keep, for every chunk: the text, the source file path, and a rough line range.
- **Where it breaks (the concept):** chunk size trade-offs; fixed-size cuts will slice a
  function in half (you'll fix that in Week 4 — note it now). Why metadata (file + lines) must
  ride along with every chunk.
- **Done check:** a list of chunk objects, each with `text`, `file`, `start_line`, `end_line`.

## Day 2 — Embeddings: text → vectors
- **Goal:** turn each chunk into a vector.
- **Try it:** start **local and simple** — `pip install sentence-transformers`, use a small
  model (e.g. `all-MiniLM-L6-v2`). Embed one sentence, print the vector length. Then embed all
  chunks.
- **Where it breaks (the concept):** what a vector/embedding *is* (meaning as numbers), why
  similar meaning → similar vectors, dimensionality, that embedding is a separate model from
  the chat LLM.
- **Done check:** every chunk now has an embedding vector of consistent length.

## Day 3 — A vector store you can query
- **Goal:** store vectors and find nearest neighbors.
- **Try it:** start with the simplest thing that works — keep vectors in memory and compute
  cosine similarity by hand with numpy; OR use a tiny local store (e.g. `chromadb` or `faiss`).
  Write `search(query, k=5)`: embed the query, return the top-k closest chunks.
- **Where it breaks (the concept):** cosine similarity / nearest-neighbor search, why a real
  vector DB exists (speed at scale), what "top-k" means and how k affects answers.
- **Done check:** `search("password check")` returns the 5 most relevant chunks with scores.

## Day 4 — Close the RAG loop
- **Goal:** retrieve → build a small prompt → answer.
- **Try it:** at question time: `search` for the top-k chunks, paste *only those* into the
  prompt (with their file paths), ask the LLM to answer using only them. Compare token count vs
  Week 2's whole-repo prompt.
- **Where it breaks (the concept):** **this is RAG.** The model never sees the whole repo —
  only the slice you pulled. Cost drops massively. Answer quality now depends entirely on
  *retrieval quality.*
- **Done check:** the big repo that broke in Week 2 now answers — and the token count is a
  fraction of before.

## Day 5 — Watch retrieval fail
- **Goal:** find questions where the right chunk *isn't* retrieved.
- **Try it:** ask 5 questions. For each, print which chunks were retrieved. Find at least one
  case where the answer is wrong *because the relevant code wasn't in the top-k.* Write down
  why (bad chunking? exact keyword the embedding missed? k too small?).
- **Where it breaks (the concept):** "garbage retrieved → garbage answer." This seeds Week 4
  (smart chunking) and Week 5 (hybrid search). The bottleneck moved from the LLM to retrieval.
- **Done check:** a documented retrieval miss with a diagnosed cause.

---

## Deliverable
An end-to-end RAG `/ask`: index a repo once, then answer questions using only retrieved chunks
— working on a repo that was too big in Week 2.

## Definition of Done
- [ ] Indexing produces chunks with `text` + `file` + line range.
- [ ] Every chunk is embedded; `search(query, k)` returns ranked relevant chunks.
- [ ] `/ask` answers from retrieved chunks only, at a fraction of Week 2's tokens.
- [ ] You can show, for any question, which chunks were retrieved.
- [ ] You have one documented retrieval failure and its cause.

## Reflection (one line in progress.md)
- **W3 — what fought back hardest?**
