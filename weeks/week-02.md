# Week 2 — The dumbest loop (your magic moment)

**Phase 1 — Dumbest loop.** Maps to backend-ai-roadmap: *05 LLM fundamentals.*

> **The struggle (= the learning):** calling an LLM API, prompts, tokens, cost. By Friday you
> point the app at a *tiny* code folder, ask a question, and get a **real answer**. It's crude
> — it just stuffs the whole folder into the prompt — and **it breaks on big repos.** That
> break is the entire reason Weeks 3–5 exist. Feel the wall this week so retrieval *means*
> something later.

---

## Day 1 — Talk to the LLM at all
- **Goal:** a script that sends a prompt to the Groq API and prints the reply.
  *(Using Groq's free tier instead of the paid Claude API — the lessons are identical.)*
- **Try it:** get a free API key at console.groq.com/keys, put it in `.env`,
  `pip install groq python-dotenv`, send "Say hello in one sentence." Pick your dev model now: a
  **cheap, fast** model for iteration (e.g. `llama-3.1-8b-instant`) and note a **stronger** model
  (e.g. `llama-3.3-70b-versatile`) for quality later.
  *Verify exact current model IDs from the official docs before hardcoding them.*
- **Where it breaks (the concept):** API keys & secrets, what a "message" is, system vs user
  prompt, that responses are non-deterministic.
- **Done check:** you get a reply printed to your terminal.

## Day 2 — Tokens & cost (the meter is running)
- **Goal:** see tokens and estimate cost per call.
- **Try it:** read `usage` (input/output tokens) off the response. Send a short prompt and a
  long one; compare. Look up your chosen model's price per million tokens and compute the cost
  of each call.
- **Where it breaks (the concept):** tokens ≠ words, the **context window** limit, why output
  tokens often cost more than input, why "just send the whole repo" won't scale.
- **Done check:** you can state the token count and rough cost of any call you make.

## Day 3 — Read a folder of code into text
- **Goal:** walk a small directory and collect its code files.
- **Try it:** make a `sample_repo/` with ~5 small Python files. Write a function that walks it,
  reads each `.py` file, and concatenates them with a header line like `# FILE: path` before
  each. Skip binary/huge files.
- **Where it breaks (the concept):** file walking, encodings, why you must label which file
  each chunk of text came from (you'll *need* those labels for citations).
- **Done check:** one big string containing all files, each prefixed with its path.

## Day 4 — The dumb loop: folder → prompt → answer
- **Goal:** wire it together behind your `POST /ask` endpoint.
- **Try it:** build a prompt: *"Here is a codebase. Answer the question using ONLY this code.
  Cite the file you used. CODE:\n{all_code}\n\nQUESTION: {question}"*. Send it, return the
  answer. Ask "Where does this project check the password?" against your sample repo.
- **Where it breaks (the concept):** prompt structure, instruction-following, that the model
  can answer about *your* code because it's *in the prompt* (not magic). Notice it sometimes
  cites wrong — seed of grounding work in Week 8.
- **Done check:** `/ask` returns a real, mostly-correct answer with a file mentioned.

## Day 5 — Feel the wall, on purpose
- **Goal:** break it with a big repo and write down exactly how.
- **Try it:** point it at a real medium Python repo (hundreds of files). Watch it fail —
  context-limit error, or absurd cost, or a vague answer. Record the error and the token count.
  Write 3 sentences in `progress.md`: what broke, why, what you think fixes it.
- **Where it breaks (the concept):** **this is the lesson.** The whole-repo approach can't
  scale → you need to send only the *relevant slice* → that's RAG (Week 3).
- **Done check:** a documented failure with numbers, and a hypothesis.

---

## Deliverable
`POST /ask` that answers questions about a *small* code folder by sending it to the LLM (Groq), and a
written, reproduced demonstration of *why it fails* on a large one.

## Definition of Done
- [x] You can ask a question about `sample_repo/` and get a real answer.
- [x] You can report tokens + cost for a call without guessing.
- [x] You picked a dev model and a quality model and can say why each.
- [x] You have a documented failure on a big repo (error + token count + hypothesis).
- [x] You understand that the answer works only because the code is *in the prompt*.

## Reflection (one line in progress.md)
- **W2 — what fought back hardest?**

 W2 Day 5 — the wall. Pointing ask.py at the whole repo pulled in
  ▎ 1,457 .py files (~18M chars, ~4.5M tokens) and the request failed
  ▎ with a connection error — ~35× over the model's 128K-token limit.
  ▎ It broke because stuffing the entire codebase (mostly irrelevant
  ▎ .venv files) into one prompt can't fit and can't scale. The fix is
  ▎ to send only the relevant files for a given question —
  ▎ retrieval/RAG — which is Week 3