# Week 10 — Background indexing, caching, streaming, logging

**Phase 5 — Real app.** Maps to backend-ai-roadmap: *10 Testing, observability, scale.*

> **The struggle (= the learning):** indexing a real repo takes a while — if it blocks the HTTP
> request, the app feels broken. Answers that re-embed and re-call the LLM every time are slow
> and expensive. This week: do slow work in the **background**, **cache** what you can, **stream**
> answers token-by-token, and **log** everything so you can see what's happening in production.

---

## Day 1 — Background indexing (don't block the request)
- **Goal:** kick off indexing as a job, return immediately.
- **Try it:** make `POST /index` enqueue a job and return a `job_id` with status `pending`. Run
  the work in the background (FastAPI `BackgroundTasks` to start; a real queue like Celery/RQ +
  Redis if you want the deeper lesson). Add `GET /index/{job_id}` for status.
- **Where it breaks (the concept):** sync vs async work, the request/response cycle shouldn't own
  long jobs, job state machines (`pending → running → done/failed`).
- **Done check:** indexing a big repo returns instantly with a job id; status flips to `done`.

## Day 2 — Idempotency & incremental indexing
- **Goal:** don't redo work you've already done.
- **Try it:** hash each file; only re-embed files that changed since last index. Make submitting
  the same index job twice safe (no duplicates, no double-spend).
- **Where it breaks (the concept):** idempotency keys, content hashing, cache invalidation —
  "only one of the two hard problems," and you'll feel why.
- **Done check:** re-indexing an unchanged repo does almost no work; changing one file re-embeds
  only that file.

## Day 3 — Caching answers & embeddings
- **Goal:** cut latency and cost on repeats.
- **Try it:** cache query embeddings and identical-question answers (with a TTL). Track cache
  hit rate. Measure cost per question before vs after.
- **Where it breaks (the concept):** what's safe to cache and for how long, cache keys, the
  trade-off between freshness and cost. Stale answers after a re-index are a real bug — invalidate
  on re-index.
- **Done check:** a repeated question is served from cache, faster and cheaper; cache invalidates
  when the repo re-indexes.

## Day 4 — Streaming answers
- **Goal:** show the answer as it's generated.
- **Try it:** stream tokens from the LLM to the client (SSE or chunked response). Handle a client
  that disconnects mid-stream. Still capture the full answer + sources server-side for history.
- **Where it breaks (the concept):** streaming changes the response model — you can't send a
  clean JSON object at the end the same way; you stream text then a final sources payload.
  Perceived speed matters as much as real speed.
- **Done check:** an answer visibly streams in; the complete answer + sources are still saved.

## Day 5 — Structured logging & observability
- **Goal:** see inside the running app.
- **Try it:** structured logs (JSON) for every request: question, retrieved chunks, tool calls,
  tokens, cost, latency, cache hit/miss, errors. Add a request id that ties a trace together.
  Skim the logs after running your eval set.
- **Where it breaks (the concept):** you cannot operate what you cannot see; logs/metrics are how
  you debug prod and control cost. This is the grown-up version of Week 7's traces.
- **Done check:** one request id lets you reconstruct the full story of any answer from logs.

---

## Deliverable
An app that indexes in the background, caches embeddings/answers, streams responses, and emits
structured logs — faster, cheaper, and observable.

## Definition of Done
- [ ] `/index` runs as a background job with a queryable status.
- [ ] Re-indexing is idempotent and incremental (only changed files).
- [ ] Repeated questions hit a cache; cache invalidates on re-index.
- [ ] Answers stream to the client; full answer + sources still persisted.
- [ ] Structured logs reconstruct any request by id (tokens, cost, latency included).

## Reflection (one line in progress.md)
- **W10 — what fought back hardest?**
