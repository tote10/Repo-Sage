# Week 6 — Tools & structured output

**Phase 3 — Agent + tools.** Maps to backend-ai-roadmap: *06 Tools & structured output.*

> **The struggle (= the learning):** so far the LLM only *talks* — it answers from whatever
> chunks you happened to retrieve. This week you let it *act*: define tools like `read_file` and
> `grep` that the model can call, you run them, and you feed results back. You also force its
> output into a **structured shape** (JSON) you can trust. This is the groundwork for the agent
> loop in Week 7.

---

## Day 1 — Structured output (no more parsing prose)
- **Goal:** make the LLM return validated JSON, not free text.
- **Try it:** define a schema for an answer (`answer`, `sources: [{file, line}]`,
  `confidence`). Use tool-calling / structured output so the model must return that shape;
  validate it with Pydantic on the way out.
- **Where it breaks (the concept):** why "please return JSON" in a prompt is unreliable, and how
  schema-enforced output fixes it. Structured data is what real apps pass around — not prose.
- **Done check:** `/ask` returns a validated object every time, or a clean error if it doesn't.

## Day 2 — Define your first tool: `read_file`
- **Goal:** give the model a function it can request.
- **Try it:** declare a `read_file(path)` tool with a JSON schema for its arguments. Implement
  the actual function (read from the indexed repo, return the text, maybe with line numbers).
  Send the tool definition with your request and log when the model asks to call it.
- **Where it breaks (the concept):** the model doesn't run your code — it *requests* a call with
  arguments; **you** execute and return the result. Tool *description* quality decides whether
  the model uses it correctly.
- **Done check:** for "show me what's in auth/login.py," the model emits a `read_file` call with
  the right path.

## Day 3 — Add `grep` and harden the tools
- **Goal:** a second tool + safety.
- **Try it:** add `grep(pattern)` that searches the repo and returns matching `file:line` hits.
  **Sandbox the tools:** confine paths to the indexed repo (no `../` escapes), cap result size,
  handle missing files gracefully.
- **Where it breaks (the concept):** tools are an attack surface — never pass model output
  straight to the filesystem unchecked. Returning too much blows the context window.
- **Done check:** `grep("password")` returns bounded `file:line` matches; path-escape attempts
  are rejected.

## Day 4 — One round-trip: request → execute → feed back
- **Goal:** complete a single tool turn end-to-end (not yet a loop).
- **Try it:** send question + tools → if the model returns a tool call, execute it, append the
  result to the conversation, and send again → get the final answer. Just **one** cycle for now.
- **Where it breaks (the concept):** the message protocol — assistant tool-use turn, then a
  tool-result turn, then the final answer. This handshake *is* the atom of the agent loop.
- **Done check:** a question that needs reading one file gets answered correctly via a real tool
  round-trip.

## Day 5 — Tool design review
- **Goal:** make the model *want* to use tools correctly.
- **Try it:** iterate on tool names, descriptions, and argument schemas. Try a question where
  the model *should* grep but doesn't — fix it by improving the description, not by hardcoding.
  Log every tool call (name + args + result size).
- **Where it breaks (the concept):** prompt/tool-description engineering; observability — you
  can't debug an agent you can't see. These logs matter a lot in Week 7.
- **Done check:** the model reliably picks the right tool for 4–5 varied questions; calls are
  logged.

---

## Deliverable
An `/ask` that returns structured, validated answers and can call `read_file` and `grep`
through a real (single) tool round-trip, with every tool call logged.

## Definition of Done
- [ ] Answers are schema-validated JSON with `sources`.
- [ ] `read_file` and `grep` are defined, implemented, and sandboxed to the repo.
- [ ] A question is answered via a genuine request→execute→feed-back round-trip.
- [ ] Path-escape and oversized-result cases are handled safely.
- [ ] Every tool call is logged with name, args, and result size.

## Reflection (one line in progress.md)
- **W6 — what fought back hardest?**
