# Week 11 — Docker + deploy + a minimal frontend

**Phase 6 — Ship it.** Maps to backend-ai-roadmap: *09 Docker & deploy, 11 Capstone build.*

> **The struggle (= the learning):** "works on my machine" is not shipped. This week you package
> the app in Docker, put a minimal chat frontend on it, and **deploy it to a public URL** a
> stranger can open. Config, secrets, ports, and CORS will all fight you — that fight *is* the
> deploy lesson.

---

## Day 1 — Dockerize the backend
- **Goal:** the app runs in a container.
- **Try it:** write a `Dockerfile` (slim Python base, install requirements, copy app, run
  uvicorn). Use a `.dockerignore`. Build and run locally; hit `/health` on the container.
- **Where it breaks (the concept):** images vs containers, layer caching, why the container is a
  reproducible environment, never baking secrets into the image.
- **Done check:** `docker run` serves the app locally on a mapped port.

## Day 2 — Compose the stack & config
- **Goal:** run app + dependencies together, configured by environment.
- **Try it:** `docker-compose.yml` for the app plus anything it needs (e.g. Postgres if you
  migrate off SQLite, Redis if you used a queue). Read all config/secrets from env vars — nothing
  hardcoded.
- **Where it breaks (the concept):** 12-factor config, service networking between containers, dev
  vs prod settings. This is where SQLite→Postgres becomes real if you make the switch.
- **Done check:** `docker compose up` brings the whole stack up; the app talks to its DB.

## Day 3 — A minimal frontend
- **Goal:** a chat box a human can actually use.
- **Try it:** a single page (plain HTML/JS, or a tiny React app) with: a repo input, a question
  box, streamed answers, and **clickable citations**. Keep it ugly but functional. Wire CORS so
  the browser can call the API.
- **Where it breaks (the concept):** CORS, talking to your own API from a browser, consuming a
  stream client-side. The citation links are the payoff of all the grounding work — make them
  visible.
- **Done check:** you ask a question in the browser and watch a cited answer stream in.

## Day 4 — Deploy to a public URL
- **Goal:** a stranger can reach it.
- **Try it:** deploy to a simple host (Railway / Render / Fly). Set production env vars/secrets in
  the host dashboard. Run DB migrations against the prod DB. Open the public URL on your phone.
- **Where it breaks (the concept):** prod vs local config, secret management, build/start
  commands, ephemeral filesystems (where does the vector store live?). The first deploy always
  surprises you.
- **Done check:** the public URL works end-to-end (index a small repo, ask, get a cited answer).

## Day 5 — Production hardening
- **Goal:** survive contact with real users.
- **Try it:** add **rate limiting** and a per-user cost cap (you're paying per token!), basic
  error pages, a health check the host monitors, and confirm logs are visible in the host. Run
  the eval set against the deployed app.
- **Where it breaks (the concept):** abuse and runaway cost are real once it's public; graceful
  failure and spend limits protect you. Prod is a different environment — re-verify there.
- **Done check:** rate limit + cost cap enforced; evals pass against the live URL.

---

## Deliverable
repo-sage live at a public URL: index a Python repo and get streamed, cited answers in a browser,
with rate limiting and cost caps in place.

## Definition of Done
- [ ] The app runs in Docker; `docker compose up` brings up the full stack.
- [ ] All config/secrets come from environment, nothing hardcoded.
- [ ] A minimal frontend streams answers and shows clickable citations.
- [ ] A public URL works end-to-end for someone who isn't you.
- [ ] Rate limiting + per-user cost cap enforced; evals pass on the live app.

## Reflection (one line in progress.md)
- **W11 — what fought back hardest?**
