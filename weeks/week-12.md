# Week 12 — Polish, README, demo, portfolio (+ monetize stretch)

**Phase 6 — Ship it.** Maps to backend-ai-roadmap: *12 Polish & portfolio.*

> **The struggle (= the learning):** a working app nobody understands isn't a portfolio piece.
> This final week you make it *legible* — to a recruiter, to a stranger, to future-you. Polish
> the rough edges, write the README and an architecture doc, record a demo, and (stretch)
> experiment with a paid tier. The win is a finished, deployed project you can explain top to
> bottom.

---

## Day 1 — Dogfood and fix the top 5 rough edges
- **Goal:** use your own app hard and fix what hurts.
- **Try it:** point repo-sage at a repo you're actually studying. Note every annoyance (confusing
  error, slow path, ugly citation, dead end). Fix the top 5.
- **Where it breaks (the concept):** dogfooding surfaces real UX problems no test catches. The
  test of a real solution: you'd use it even if nobody else did.
- **Done check:** five concrete improvements shipped from real usage.

## Day 2 — The README that sells it
- **Goal:** a project README a stranger gets in 60 seconds.
- **Try it:** what it does, a screenshot/GIF, the live URL, quickstart (run locally in <5 min),
  the architecture (your 5 pieces), and your **eval score with the story** of how it improved.
- **Where it breaks (the concept):** communicating a system concisely is its own skill; the eval
  number is your credibility. (This is the *project* README, distinct from the roadmap README.)
- **Done check:** someone unfamiliar can understand and run it from the README alone.

## Day 3 — Architecture write-up & decision log
- **Goal:** show your engineering judgment, not just the result.
- **Try it:** a short `ARCHITECTURE.md`: the retrieve→reason flow, why AST chunking, why hybrid
  search, how the agent loop is bounded, how grounding/refusal work. Add a few "decisions &
  trade-offs" (e.g. Python-first, small-repo scope) and known limitations.
- **Where it breaks (the concept):** interviews probe *why*, not *what*. Writing trade-offs down
  is how you prove you understand them — and it's the senior skill from `UNDERSTAND-THE-PROJECT`.
- **Done check:** a doc that explains every major choice and what you'd do next.

## Day 4 — Demo video & final eval run
- **Goal:** a 2–3 minute demo and a final, honest score.
- **Try it:** record a walkthrough — index a repo, ask a "where," ask a "what breaks if," show a
  citation, show an "I don't know." Do a final eval run; log the final score in `progress.md`
  with the date and the before→after delta.
- **Where it breaks (the concept):** a demo makes the work *real* to people who won't read code.
  The eval delta is the headline number of the whole project.
- **Done check:** a published demo link and a final eval score logged with its delta.

## Day 5 — Portfolio packaging (+ monetize stretch)
- **Goal:** make it findable and tell the story; optionally test willingness to pay.
- **Try it:** clean the repo, pin the live URL + demo in the README, write a short LinkedIn/blog
  post on what you learned (the *struggles*, not just the features). **Stretch:** add usage limits
  + a simple paid-tier stub (e.g. free quota, then a "upgrade" placeholder) — just enough to learn
  the shape of monetization, not to actually charge.
- **Where it breaks (the concept):** the learning narrative is what lands the job; money is a
  bonus and must not derail a finished project. Done > perfect.
- **Done check:** repo + post + live demo are public and link to each other; (stretch) a usage
  limit and upgrade stub exist.

---

## Deliverable
A finished, deployed, documented portfolio project: live URL, demo video, project README +
architecture doc, a tracked eval-score story — and optionally a monetization stub.

## Definition of Done
- [ ] Top dogfooding rough edges fixed.
- [ ] Project README lets a stranger understand and run it; includes the live URL + eval story.
- [ ] `ARCHITECTURE.md` explains the design, trade-offs, and limitations.
- [ ] A 2–3 min demo is published; final eval score + delta logged in `progress.md`.
- [ ] Repo, demo, and write-up are public and cross-linked. (Stretch) paid-tier stub exists.

## The finish line (from UNDERSTAND-THE-PROJECT §8)
- [ ] A stranger can index a Python repo and ask questions at a public URL.
- [ ] Answers cite real `file:line` and refuse when unsure.
- [ ] You tracked an eval score over time and can talk about it.
- [ ] You hit every layer — API, LLM, RAG, agents, evals, DB, auth, async, Docker, deploy — by
      *needing* it.

## Reflection (one line in progress.md)
- **W12 — what fought back hardest?**
