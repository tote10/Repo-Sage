# repo-sage — Build Roadmap

> Day-to-day, you live in [`START-HERE.md`](./START-HERE.md) and [`tracker.md`](./tracker.md).
> This file is the big-picture plan: the phases, the build order, and how it maps to your
> backend-ai-roadmap. Read it once to see the shape of the journey, then mostly ignore it.

A 12-week, build-to-learn project. You build **one real AI product** end-to-end and,
by hitting the wall each concept solves, you learn the entire backend + AI stack for real
(not by reading — by struggling and shipping).

---

## How this roadmap works

- One file per week: `week-01.md` … `week-12.md`. Each has a **day-by-day** plan (5 days/week).
- **Rule of engagement:** for each day, *try it yourself first and let it break.* When stuck,
  bring what you tried — get the concept explained, not the finished code handed to you.
  Struggle first, then understanding. That's the whole point.
- Track status in [`progress.md`](./progress.md) (week-level) and [`tracker.md`](./tracker.md)
  (day-by-day checklist).
- Each week ends with a **Deliverable** (something that runs) and a **Definition of Done**.

## The golden build order

We do **not** build the whole engine and then switch it on. In **Week 2 you get a working
magic moment** (crude, but real), then every later week *deepens* the same thing. You always
have something that runs. That's how real software gets built — and it keeps you going when
it's hard.

---

## Phase → Week map

| Phase | Weeks | What you build | The struggle (= the learning) |
|---|---|---|---|
| **0 — Foundations** | 1 | Running FastAPI app + project skeleton | Tooling, environments, project layout |
| **1 — Dumbest loop** | 2 | code folder → LLM → real answer (tiny repo) | Calling an LLM API, prompts, tokens, cost; *it breaks on big repos* |
| **2 — Retrieval / RAG** | 3–5 | Chunk → embed → retrieve only relevant code; citations; hybrid search | Why naive RAG gives dumb answers. The deep end. |
| **3 — Agent + tools** | 6–7 | Give the AI tools (`read_file`, `grep`, `find_callers`) + a think→act loop | Tool design, agent loops, stopping infinite loops |
| **4 — Trust / evals** | 8 | A test set + auto-scoring; force citations & "I don't know" | How do you even *measure* "correct"? (the rare senior skill) |
| **5 — Real app** | 9–10 | Auth, database, background indexing, caching, streaming, logging | Async, job queues, idempotency, cost control |
| **6 — Ship it** | 11–12 | Docker, deploy, frontend, README, demo, polish | Docker, prod config, "works on my machine" |

## Maps onto your `backend-ai-roadmap`

| repo-sage week | backend-ai-roadmap week |
|---|---|
| 1 | 01 Python + fundamentals, 02 HTTP/REST/FastAPI |
| 2 | 05 LLM fundamentals |
| 3–5 | 07 RAG |
| 6 | 06 Tools & structured output |
| 7 | 08 Agents |
| 8 | 08 Agents & evals, 10 testing/observability |
| 9 | 03 Databases/SQL/ORM, 04 Auth/structure/CRUD |
| 10 | 10 Testing, observability, scale |
| 11 | 09 Docker & deploy, 11 Capstone build |
| 12 | 12 Polish & portfolio |

> Algorithms (`algo-roadmap`) stays a **separate** LeetCode grind — a project can't teach that.
> Project = job-ready skills + portfolio + maybe money. LeetCode = passing the interview.

---

## Tech stack (decided as we go, not all up front)

- **Language:** Python
- **API framework:** FastAPI
- **LLM:** Claude (Anthropic API). Use a cheap fast model for dev iteration, a stronger one for
  quality. *Exact model picked in Week 2.*
- **Embeddings + vector store:** start simple (local), introduced in Week 3.
- **DB:** SQLite while learning → Postgres later. ORM: SQLAlchemy.
- **Deploy:** Docker + a simple cloud host (Railway / Render / Fly). Week 11.

## Scope (so you don't drown)

- **v1 target:** great at **Python** repos of **reasonable size** (hundreds of files).
- Answers are **often correct and always cite their source** so the user can verify in 2 seconds.
- More languages, huge repos = *later*, same architecture. Shipping a sharp slice beats a vague everything.
