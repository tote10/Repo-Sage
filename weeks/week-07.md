# Week 7 — The agent loop

**Phase 3 — Agent + tools.** Maps to backend-ai-roadmap: *08 Agents.*

> **The struggle (= the learning):** one tool call isn't enough for "what breaks if I delete
> `hashing.py`?" — that needs *several* steps: grep for importers, read each, then reason. This
> week you build the loop: **think → call a tool → observe → think again → … → answer**, plus a
> `find_callers` tool. The new danger: loops that never stop. Taming that is the lesson.

---

## Day 1 — Turn the single round-trip into a loop
- **Goal:** let the model take multiple tool steps before answering.
- **Try it:** wrap Week 6's round-trip in a `while`: keep executing tool calls and feeding
  results back until the model returns a final answer instead of a tool call. Print each step.
- **Where it breaks (the concept):** the agent *plans across steps* — it reads one file, learns
  it needs another, fetches that. State accumulates in the message history.
- **Done check:** a 2–3 step question (read file A → grep → answer) completes by itself.

## Day 2 — Stop the runaway (this is the real lesson)
- **Goal:** guarantee the loop terminates.
- **Try it:** add a **max-steps** cap, detect repeated/identical tool calls, and add a token/cost
  budget per question. When a limit hits, force a final answer ("answer with what you have, or
  say you don't know").
- **Where it breaks (the concept):** agents loop forever, repeat themselves, or burn money. Hard
  limits and loop-detection are non-negotiable in production. Failure must be *graceful*.
- **Done check:** an intentionally-hard question hits the cap and returns a sane answer, not an
  infinite loop or a crash.

## Day 3 — `find_callers`: the impact tool
- **Goal:** answer "what breaks if I change/delete X?"
- **Try it:** add `find_callers(symbol)` — find where a function/file is imported or called
  (reuse your AST work + grep). Wire it into the toolset. Ask: "What breaks if I delete
  `utils/hashing.py`?"
- **Where it breaks (the concept):** higher-level tools beat raw grep for reasoning tasks; the
  agent now *composes* tools (find_callers → read_file → answer) to do something genuinely
  useful.
- **Done check:** the delete-impact question lists the real importing files with citations.

## Day 4 — Retrieval as a tool + when to use which
- **Goal:** combine RAG and the agent.
- **Try it:** expose your Week 5 hybrid `search` as a tool too. Now the agent can *retrieve* for
  fuzzy "where/how" questions and *grep/read* for exact ones — and decide which. Tune the system
  prompt so it picks well.
- **Where it breaks (the concept):** RAG and agentic navigation are complementary, not rivals —
  retrieval gives a fast first guess, tools verify and dig. The model orchestrates them.
- **Done check:** a fuzzy question triggers `search`; an exact-symbol question triggers
  `grep`/`read_file`.

## Day 5 — Trace, observe, and stress-test
- **Goal:** make the agent debuggable and measure its cost.
- **Try it:** for each question, save a full **trace**: every step, tool, args, result snippet,
  tokens, total cost. Run your question set through the agent; note where it wanders or wastes
  steps.
- **Where it breaks (the concept):** observability is how you debug non-determinism. The trace is
  what you'll stare at constantly in Week 8 when scoring correctness.
- **Done check:** every answer has a saved trace; you can point to the exact step where a wrong
  answer went wrong.

---

## Deliverable
An agent that loops over `search`, `read_file`, `grep`, and `find_callers` to answer multi-step
questions — with hard stop conditions and a full trace per question.

## Definition of Done
- [ ] The agent completes multi-step questions on its own.
- [ ] Max-steps, loop-detection, and a cost budget all work; limits fail gracefully.
- [ ] `find_callers` answers a real "what breaks if I delete X?" with citations.
- [ ] The agent chooses retrieval vs grep/read appropriately.
- [ ] Each question produces a full, inspectable trace with cost.

## Reflection (one line in progress.md)
- **W7 — what fought back hardest?**
