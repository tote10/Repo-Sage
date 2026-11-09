# Week 1 — Foundations: a running FastAPI app + project skeleton

**Phase 0 — Foundations.** Maps to backend-ai-roadmap: *01 Python + fundamentals, 02 HTTP/REST/FastAPI.*

> **The struggle (= the learning):** tooling, environments, project layout. None of it is
> "AI" yet — but if you can't run a server and hit an endpoint cleanly, everything later is
> built on sand. This week you earn the right to build the interesting stuff.

**Rule of engagement:** for each day, *try it yourself first and let it break.* When stuck,
bring what you tried and the error — get the concept explained, not the finished code handed
to you.

---

## Day 1 — Python environment that doesn't lie to you
- **Goal:** a clean, reproducible Python environment you understand.
- **Try it:** install Python 3.11+, create a virtual environment (`python -m venv .venv`),
  activate it, `pip install fastapi uvicorn`, freeze with `pip freeze > requirements.txt`.
- **Where it breaks (the concept):** "works on my machine." *Why* venvs exist — global vs
  isolated packages, why `pip freeze` matters, what `PATH` and "activate" actually do.
- **Done check:** `which python` (or `where python`) points inside `.venv`, and
  `pip list` shows fastapi.

## Day 2 — Hello, server
- **Goal:** a FastAPI app that returns JSON on `GET /health`.
- **Try it:** write `main.py` with one route, run `uvicorn main:app --reload`, hit it in the
  browser and with `curl`.
- **Where it breaks (the concept):** what is an ASGI server vs your app? What does `--reload`
  do? What's the difference between the function you wrote and the HTTP response the client
  sees? Look at the auto-generated docs at `/docs`.
- **Done check:** `curl localhost:8000/health` returns `{"status":"ok"}`.

## Day 3 — HTTP for real (not vibes)
- **Goal:** an endpoint that *takes input* and *validates it*.
- **Try it:** add `POST /ask` that accepts a JSON body `{"question": "..."}` using a Pydantic
  model. Return the question back, uppercased.
- **Where it breaks (the concept):** request body vs query params vs path params; status codes
  (200 / 422 / 404); why Pydantic rejects bad input *for* you. Send a malformed body on purpose
  and read the 422.
- **Done check:** valid body → 200; missing `question` → 422 with a clear error.

## Day 4 — Project skeleton you won't outgrow in week 5
- **Goal:** a folder layout that has room for ingester / search / agent / api later.
- **Try it:** create `app/` with `app/main.py`, `app/api/`, `app/core/` (config), and a
  `tests/` folder. Move your routes into a router. Add a `.gitignore` (ignore `.venv`,
  `__pycache__`, `.env`).
- **Where it breaks (the concept):** imports and packages (`__init__.py`, module paths),
  separating config from code, why secrets go in `.env` not in source.
- **Done check:** app still runs after the reshuffle; `.env` exists and is git-ignored.

## Day 5 — First test + first commit + Python refresh
- **Goal:** prove it works automatically, and lock in the baseline.
- **Try it:** `pip install pytest httpx`, write one test that calls `/health` and asserts 200.
  `git init`, commit everything. Spend the back half refreshing the Python you're rusty on
  (dicts, list/dict comprehensions, type hints, f-strings, `with` blocks).
- **Where it breaks (the concept):** what a test client is, why tests beat clicking around,
  what belongs in version control.
- **Done check:** `pytest` is green; `git log` shows your first commit.

---

## Deliverable
A FastAPI app you can start with one command that serves `/health` and `/ask`, with a passing
test and a clean repo skeleton.

## Definition of Done
- [ ] `uvicorn` starts the app; `/health` and `/ask` work.
- [ ] Bad input to `/ask` returns 422 (you didn't write that handler — Pydantic did).
- [ ] `pytest` passes at least one real test.
- [ ] Repo is initialized, `.env` is git-ignored, `requirements.txt` is committed.
- [ ] You can explain, out loud, what a virtualenv and an ASGI server are.

## Reflection (one line in progress.md)
- **W1 — what fought back hardest?**
