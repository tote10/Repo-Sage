# Week 4 — Smart chunking (AST) + real file:line citations

**Phase 2 — Retrieval / RAG.** Maps to backend-ai-roadmap: *07 RAG.*

> **The struggle (= the learning):** fixed-size chunks slice functions in half and produce
> garbage. This week you chunk by **structure** — one function/class = one chunk — using
> Python's own parser (AST). And you make citations *real*: every answer points to an exact
> `file:line` the user can click and verify in 2 seconds. This is the feature that makes
> repo-sage trustworthy instead of a chatbot.

---

## Day 1 — Meet the AST
- **Goal:** parse a Python file into its structure.
- **Try it:** use the standard-library `ast` module. Parse one file, walk the tree, print every
  function and class with its name and start/end line numbers (`node.lineno`,
  `node.end_lineno`).
- **Where it breaks (the concept):** what an Abstract Syntax Tree is — code as a tree the
  computer understands, not just text. Why this is the "little parser per language" the project
  scoped to Python for.
- **Done check:** for a file, you can list every function/class and its exact line range.

## Day 2 — Chunk by function/class
- **Goal:** replace fixed-size chunking with structural chunking.
- **Try it:** make each top-level function and class its own chunk (text = that span; metadata =
  file + real start/end lines). Handle the leftovers (module-level code, imports) sensibly.
  Split chunks that are too large to embed well.
- **Where it breaks (the concept):** chunk *boundaries* matter more than chunk *size*; a whole
  function is a unit of meaning, so its embedding is far more coherent.
- **Done check:** re-index; chunks now align to function/class boundaries with accurate lines.

## Day 3 — Citations that actually point somewhere
- **Goal:** force the answer to cite `file:line` from the chunks it used.
- **Try it:** label each retrieved chunk in the prompt with its `file:start-end`. Instruct
  the LLM to end with a `Sources:` list of the exact `file:line` references it relied on. Parse
  those out and return them as structured data, not just prose.
- **Where it breaks (the concept):** grounding — tying claims to sources. The model will
  sometimes cite a chunk it didn't really use, or invent a line; you'll measure and tighten
  this in Week 8.
- **Done check:** answers come back with a clickable-style `auth/login.py:40` that genuinely
  contains the relevant code.

## Day 4 — A/B: dumb vs smart chunking
- **Goal:** prove the upgrade actually helped.
- **Try it:** keep both chunkers behind a flag. Run the same 5–10 questions through each.
  Eyeball: are retrieved chunks more on-target with AST chunking? Are citations landing on the
  right lines?
- **Where it breaks (the concept):** you're inventing a poor-man's eval. Note how subjective
  "better" feels right now — that pain is *why* Week 8 builds automated scoring.
- **Done check:** a short written comparison; AST chunking wins on most questions.

## Day 5 — Re-index hygiene & metadata
- **Goal:** make indexing repeatable and inspectable.
- **Try it:** add an `/index` action that (re)builds the store for a given repo path. Store
  enough metadata per chunk (file, lines, symbol name) to render a citation without re-reading
  files. Make re-indexing idempotent (running twice doesn't duplicate).
- **Where it breaks (the concept):** idempotency, separating "index time" from "query time,"
  why you don't want to re-embed unchanged files forever (seed for Week 10 caching).
- **Done check:** `/index` rebuilds cleanly; citations render from stored metadata alone.

---

## Deliverable
RAG with **AST-based chunking** and **verifiable `file:line` citations** — answers you can
fact-check by clicking the source.

## Definition of Done
- [ ] Chunks align to functions/classes with accurate start/end lines.
- [ ] Every answer returns a structured list of `file:line` sources.
- [ ] At least one citation, checked by hand, lands on the correct code.
- [ ] You can show AST chunking beats fixed-size chunking on your question set.
- [ ] `/index` is repeatable and idempotent.

## Reflection (one line in progress.md)
- **W4 — what fought back hardest?**
