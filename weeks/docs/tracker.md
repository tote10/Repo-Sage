# Progress Checklist — repo-sage

**How to use:** when you finish a day, change `[ ]` to `[x]`. That's it.
Each line is one day's job. Details for each day are in the matching `week-XX.md` file.

---

## Week 1 — Foundations (FastAPI skeleton)
- [x] Day 1 — Set up a clean Python environment
- [x] Day 2 — Run a FastAPI server with a `/health` page
- [x] Day 3 — Add `/ask` that takes and checks input
- [x] Day 4 — Organize the project folders + add `.env`
- [x] Day 5 — Write your first test + first git commit

## Week 2 — The dumbest loop (first magic moment)
- [x] Day 1 — Get groq to reply to you at all
- [x] Day 2 — See how many tokens / how much money each call costs
- [x] Day 3 — Read a folder of code into text
- [x] Day 4 — Folder → Claude → real answer
- [x] Day 5 — Break it on a big repo (and write down why)

## Week 3 — Naive RAG (find only the relevant code)
- [x] Day 1 — Cut code into chunks
- [x] Day 2 — Turn chunks into numbers (embeddings)
- [x] Day 3 — Store them + search for the closest chunks
- [x] Day 4 — Retrieve a few chunks → answer from only those
- [x] Day 5 — Find a question where the wrong chunk got picked

## Week 4 — Smart chunking + real citations
- [x] Day 1 — Read Python structure with `ast`
- [x] Day 2 — Make each function/class its own chunk
- [x] Day 3 — Answers point to a real `file:line`
- [x] Day 4 — Compare dumb vs smart chunking
- [x] Day 5 — Make re-indexing clean and repeatable

## Week 5 — Hybrid search + reranking
- [x] Day 1 — Add keyword search (exact names)
- [x] Day 2 — Combine keyword + meaning search
- [x] Day 3 — Rerank so the best chunk is #1
- [x] Day 4 — Test which setup answers best
- [x] Day 5 — Lock in your default search setup

## Week 6 — Tools & structured output
- [x] Day 1 — Make Claude return clean JSON
- [x] Day 2 — Give it a `read_file` tool
- [x] Day 3 — Add a `grep` tool (safely)
- [ ] Day 4 — One full tool round-trip
- [ ] Day 5 — Improve the tools + log every call

## Week 7 — The agent loop
- [ ] Day 1 — Let it take several tool steps in a row
- [ ] Day 2 — Stop it from looping forever / overspending
- [ ] Day 3 — Add `find_callers` ("what breaks if I delete X?")
- [ ] Day 4 — Let it choose: search vs grep vs read
- [ ] Day 5 — Save a full trace of every question

## Week 8 — Trust: evals + grounding
- [ ] Day 1 — Write a test set of questions + known answers
- [ ] Day 2 — Auto-score the answers
- [ ] Day 3 — Record your baseline score
- [ ] Day 4 — Force every claim to cite a real source
- [ ] Day 5 — Teach it to say "I don't know" + beat the baseline

## Week 9 — Database + login
- [ ] Day 1 — Design the database tables
- [ ] Day 2 — Save/load data through the API
- [ ] Day 3 — Sign up / log in (hash passwords)
- [ ] Day 4 — Make each user only see their own data
- [ ] Day 5 — Safe schema changes (migrations) + re-run evals

## Week 10 — Speed: background jobs, caching, streaming
- [ ] Day 1 — Index in the background (don't freeze the app)
- [ ] Day 2 — Only re-index files that changed
- [ ] Day 3 — Cache answers + embeddings to save money
- [ ] Day 4 — Stream answers as they're written
- [ ] Day 5 — Add proper logs you can read later

## Week 11 — Ship it (Docker + deploy + frontend)
- [ ] Day 1 — Put the app in Docker
- [ ] Day 2 — Run the whole stack with config from env vars
- [ ] Day 3 — Build a simple chat web page
- [ ] Day 4 — Deploy to a public URL
- [ ] Day 5 — Add rate limits + spending caps

## Week 12 — Polish + portfolio
- [ ] Day 1 — Use it on a real repo, fix the worst 5 things
- [ ] Day 2 — Write the README
- [ ] Day 3 — Write how it works (architecture)
- [ ] Day 4 — Record a demo + final score
- [ ] Day 5 — Package it as a portfolio piece
