# Week 9 — Database + auth (it becomes a real app)

**Phase 5 — Real app.** Maps to backend-ai-roadmap: *03 Databases/SQL/ORM, 04 Auth/structure/CRUD.*

> **The struggle (= the learning):** until now everything lived in memory and vanished on
> restart. A real app *remembers*: users, the repos they indexed, their chat history. This week
> you add a database and authentication so different people have private, persistent data. This
> is the unglamorous backbone every product needs.

---

## Day 1 — Data model + SQLite via SQLAlchemy
- **Goal:** persist the core entities.
- **Try it:** model `User`, `Repo`, `Chat`, `Message` (and where indexed chunks/metadata live).
  Set up SQLAlchemy with SQLite. Create the tables.
- **Where it breaks (the concept):** schema design, primary/foreign keys, relationships, ORM vs
  raw SQL. Decisions here ripple through the whole app — model the relationships before coding.
- **Done check:** tables exist; you can create and read a `User` and a `Repo` from a script.

## Day 2 — CRUD wired into the API
- **Goal:** create/read/update/delete through endpoints.
- **Try it:** endpoints to register a repo, list a user's repos, save a chat message, fetch chat
  history. Use a per-request DB session (FastAPI dependency). Persist indexing results so a repo
  doesn't need re-indexing every restart.
- **Where it breaks (the concept):** session lifecycle (open/commit/close per request), N+1
  queries, keeping DB logic out of route handlers. Restart the server — data must survive.
- **Done check:** index a repo, restart the app, and still query it without re-indexing.

## Day 3 — Authentication
- **Goal:** users can sign up and log in.
- **Try it:** signup/login endpoints; **hash passwords** (bcrypt/argon2 — never store plaintext);
  issue a session token or JWT on login. (Fitting: your own app's `auth/login.py` is now the
  kind of code repo-sage explains.)
- **Where it breaks (the concept):** password hashing + salting, tokens vs sessions, why secrets
  never touch the DB in plaintext. Security has real consequences here.
- **Done check:** signup creates a user with a hashed password; login returns a valid token.

## Day 4 — Authorization & scoping
- **Goal:** users only see *their* data.
- **Try it:** a dependency that resolves the current user from the token and **rejects**
  unauthenticated requests. Scope every query by `user_id` so User A can't read User B's repos or
  chats. Try to access another user's data on purpose and confirm it's blocked.
- **Where it breaks (the concept):** authentication (who are you) vs authorization (what can you
  touch). Forgetting to scope a query is one of the most common real security bugs.
- **Done check:** protected routes 401 without a token; cross-user access attempts are denied.

## Day 5 — Migrations & don't break the evals
- **Goal:** evolve the schema safely and confirm nothing regressed.
- **Try it:** add Alembic (or a documented migration approach) so schema changes don't nuke data.
  Make one migration (add a column). Re-run your Week 8 eval harness through the now-persistent,
  authed app.
- **Where it breaks (the concept):** migrations vs "drop and recreate"; in production you can't
  lose data. Regression-testing after infra changes is a habit, not an afterthought.
- **Done check:** a migration applies cleanly with data intact; eval score holds at/above Week 8.

---

## Deliverable
A multi-user app where people sign up, log in, index repos, and chat — all persisted in a
database and private to each user — with evals still passing.

## Definition of Done
- [ ] `User`/`Repo`/`Chat`/`Message` persist; data survives restart.
- [ ] CRUD endpoints work with per-request DB sessions.
- [ ] Signup/login work; passwords are hashed; login issues a token.
- [ ] Protected routes reject anonymous requests; queries are scoped per user.
- [ ] A migration runs without data loss; eval score ≥ Week 8.

## Reflection (one line in progress.md)
- **W9 — what fought back hardest?**
