# Week 8 — Trust: evals, grounding, and "I don't know"

**Phase 4 — Trust / evals.** Maps to backend-ai-roadmap: *08 Agents & evals, 10 testing/observability.*

> **The struggle (= the learning):** how do you even *measure* "correct"? Until now "better" has
> been a vibe. This week you build a test set with known answers, score the app **automatically**,
> and force it to **ground every claim in a citation** and say **"I don't know"** when the
> sources don't support an answer. This is the rare senior skill — the number going up *is* the
> project from here on.

---

## Day 1 — Build the eval set
- **Goal:** a file of questions with known-good answers.
- **Try it:** pick a fixed repo. Write 20–30 questions across types: factual ("where is X"),
  impact ("what breaks if…"), and **unanswerable** ones (the answer isn't in the repo). For each,
  record the expected `file:line`(s) and/or a gold answer.
- **Where it breaks (the concept):** writing good test questions is hard and clarifying — vague
  questions can't be scored. Including unanswerable cases is what lets you test refusal.
- **Done check:** `evals.jsonl` (or similar) with ≥20 questions and expected answers/sources.

## Day 2 — Auto-scoring harness
- **Goal:** run all questions and produce a score.
- **Try it:** a script that asks each question, captures the answer + sources + trace, and scores
  it. Use cheap automatic checks first: did the expected `file:line` appear in the cited sources?
  Then add an **LLM-as-judge** to grade answer correctness against the gold answer.
- **Where it breaks (the concept):** exact-match scoring is brittle for prose, so you combine
  source-overlap checks with a judge. The judge itself can be wrong — spot-check it.
- **Done check:** one command prints an overall score (% correct) and per-question results.

## Day 3 — Baseline + the score log
- **Goal:** establish the number you'll try to beat.
- **Try it:** run the harness, record the baseline % in `progress.md`'s **Eval score log** with
  the date and "baseline." Read every *failure* trace and bucket the causes (retrieval miss, bad
  citation, hallucination, gave up too early).
- **Where it breaks (the concept):** the score is only useful with a baseline and error
  analysis. Failure buckets tell you *what to fix*, not just *that* you failed.
- **Done check:** a baseline score logged with a dated row and a tally of failure causes.

## Day 4 — Grounding & forced citations
- **Goal:** stop ungrounded claims.
- **Try it:** require every answer to cite sources actually present in the context; **verify**
  the model didn't cite a `file:line` it never received, and reject/retry if it did. Tighten the
  system prompt so claims map to sources. Re-run evals.
- **Where it breaks (the concept):** hallucinated citations are worse than no answer — they look
  trustworthy and aren't. Verifying citations against provided context is the guardrail.
- **Done check:** invented/unsupported citations are caught; grounding-related failures drop.

## Day 5 — Teach it to say "I don't know"
- **Goal:** refuse confidently when the answer isn't supported.
- **Try it:** for the unanswerable questions, the app must say it can't find it — not guess.
  Tune the prompt + a confidence threshold. Re-run evals; confirm refusals are right *and* you
  didn't start refusing answerable questions (track both).
- **Where it breaks (the concept):** the precision/refusal trade-off — over-refusing is its own
  failure. Calibrated "I don't know" is what makes the tool trustworthy.
- **Done check:** unanswerable questions get refused; answerable ones still get answered;
  overall eval score beats the baseline.

---

## Deliverable
An automated eval harness with a logged baseline, plus grounding and refusal behavior that
**measurably** improves the score over the baseline.

## Definition of Done
- [ ] ≥20 eval questions (incl. unanswerable) with expected answers/sources.
- [ ] One command produces an overall score + per-question breakdown.
- [ ] Baseline logged in `progress.md`; failures bucketed by cause.
- [ ] Hallucinated/unsupported citations are detected and prevented.
- [ ] Unanswerable → "I don't know"; answerable still answered; score > baseline.

## Reflection (one line in progress.md)
- **W8 — what fought back hardest?**
