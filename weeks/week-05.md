# Week 5 — Hybrid search + reranking

**Phase 2 — Retrieval / RAG.** Maps to backend-ai-roadmap: *07 RAG.*

> **The struggle (= the learning):** semantic search misses *exact names.* Ask about a variable
> called `user_token` and embeddings may shrug, while a plain keyword search nails it — and vice
> versa for "where do we check the password." This week you combine both (hybrid search) and add
> a **reranker** so the best chunk lands at the top. This is the difference between "RAG demo"
> and "RAG that's actually good."

---

## Day 1 — Keyword search (the half you've been missing)
- **Goal:** add lexical search over chunks.
- **Try it:** implement keyword/BM25-style search (e.g. `rank_bm25`, or SQLite FTS5). Index the
  chunk text; query it for exact terms. Test it on an identifier-heavy question your semantic
  search flubbed in Week 3.
- **Where it breaks (the concept):** lexical vs semantic — keyword search has no idea what words
  *mean* but is unbeatable on exact symbols. Now you have two retrievers with opposite blind
  spots.
- **Done check:** a `keyword_search(query, k)` that finds chunks containing exact identifiers.

## Day 2 — Fuse the two result lists
- **Goal:** merge semantic + keyword results into one ranking.
- **Try it:** run both retrievers, then combine. Start with **Reciprocal Rank Fusion** (simple,
  no tuning): each chunk's score = sum of `1/(k + rank)` across both lists. Dedup chunks that
  appear in both.
- **Where it breaks (the concept):** score scales differ between retrievers, so you fuse by
  *rank*, not raw score. Why fusion beats either alone — each covers the other's misses.
- **Done check:** `hybrid_search(query, k)` returns a single fused, deduped ranking.

## Day 3 — Reranking: put the best chunk first
- **Goal:** reorder the fused candidates by true relevance to the question.
- **Try it:** take the top ~20 fused candidates and rerank them with a cross-encoder
  (e.g. a `sentence-transformers` cross-encoder) **or** an LLM-as-reranker prompt that scores
  each chunk 0–10 for relevance. Keep the top-k after reranking.
- **Where it breaks (the concept):** retrieval (fast, approximate) vs reranking (slow, precise)
  — the two-stage pattern. Why you rerank a shortlist, not the whole index (cost/latency).
- **Done check:** for a question where the right chunk was rank #6, it's now in the top 3.

## Day 4 — Tune k and measure
- **Goal:** find a good retrieval size and prove the gains.
- **Try it:** sweep retrieve-k and final-k on your question set. Track: did the right chunk make
  the final context? Compare semantic-only vs hybrid vs hybrid+rerank on the same questions.
- **Where it breaks (the concept):** more context isn't better — it adds cost, noise, and can
  *lower* answer quality. You're balancing recall vs precision vs cost. (Still eyeballing —
  Week 8 automates this.)
- **Done check:** a table: retrieval variant → how many questions got the right chunk in context.

## Day 5 — Lock the retrieval baseline
- **Goal:** freeze a configuration you trust before adding agents.
- **Try it:** pick your default (likely hybrid + rerank), make it the path `/ask` uses, and
  write down the config (k values, models, fusion method). Save your question set as a file —
  it becomes the seed of the Week 8 eval set.
- **Where it breaks (the concept):** reproducibility — you can't improve what you can't pin
  down. Retrieval is now "good enough"; the next ceiling is *navigation* (agents, Week 6–7).
- **Done check:** a documented, default retrieval config and a saved question set.

---

## Deliverable
A hybrid (semantic + keyword) retriever with reranking, set as the default, measurably better
than Week 3's semantic-only search on your question set.

## Definition of Done
- [ ] Keyword search finds exact identifiers semantic search missed.
- [ ] `hybrid_search` fuses and dedups both retrievers into one ranking.
- [ ] A reranker reorders the shortlist; right chunks move up.
- [ ] You have a comparison table showing hybrid+rerank wins.
- [ ] Default retrieval config and a reusable question set are saved.

## Reflection (one line in progress.md)
- **W5 — what fought back hardest?**
