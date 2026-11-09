# Understand the Project (read this first)

Plain English. No jargon without explanation. If you understand this file, you understand the
whole project before writing a line of code.

---

## 1. What are we building?

**Your own app** that you can point at a codebase (a folder of code) and then *ask questions
about it in plain English* — and get answers that are **correct and point to the exact file
and line**.

You are **not** contributing to someone else's GitHub. You are **not** editing the code you
point it at. That code is just **the input** — the fuel. The app is the thing you build.

Analogy: Spotify doesn't make the songs; it reads songs and lets you do things with them.
repo-sage doesn't write the code; it reads code and lets you ask things about it.

### What using it feels like (when it's done)

```
You:  [pick a code folder / paste a GitHub link]
App:  Indexing… done. 412 files read. Ask me anything.

You:  Where does this project check if a password is correct?
App:  In auth/login.py:40–55 — it hashes the input and compares to the stored hash.
      Sources: auth/login.py:40, utils/hashing.py:12

You:  What breaks if I delete utils/hashing.py?
App:  3 files import it: login.py, signup.py, reset_password.py.
      Deleting it breaks login, signup, and password reset.
```

The key: it **read the real code**, found the real answer, and **proved it with a citation.**
"Not guessing — prove it" is the hard, valuable engineering you're here to learn.

---

## 2. Why this problem is real

Dropping into an unfamiliar codebase is brutal — for you right now, for every new hire, for
every open-source contributor. "Where does X happen? Why is it written this way? What breaks if
I change this?" Plain search (grep, GitHub search) finds *text* but can't *reason*. This is a
genuine pain you personally have today — which means you can **dogfood** your own tool (point it
at any repo you're studying). That's the test of a real solution: you'd use it even if nobody
else did.

---

## 3. How it works — the one big idea

The app does **two boring things**, fast:

1. **Retrieve** — out of thousands of code pieces, find the handful *relevant* to your question.
   (Like a librarian fetching the 3 right books, not reading the whole library.)
2. **Reason** — hand only those few pieces to the AI: *"answer using only this."*

So it **never understands the whole repo at once.** It understands the **small slice it pulled
for your specific question.** That's the trick that makes the impossible-sounding thing possible.
And when it pulls the *wrong* slice → bad answer → that's the problem you'll spend weeks improving.

---

## 4. The parts you build (5 pieces)

```
            ┌──────────────────────────────────────────────────────┐
            │                     repo-sage                         │
            │                                                       │
  code  →   │  1. INGESTER   chop code into smart pieces (by func)  │
  folder    │       │                                               │
            │       ▼                                               │
            │  2. SEARCH BRAIN   embed + store pieces; find the     │
            │       │            relevant few per question (RAG)    │
            │       ▼                                               │
  your   →  │  3. AGENT    decides: "read file X, grep for Y",      │
  question  │       │       uses tools, then answers WITH citations │
            │       ▼                                               │
            │  4. WEB INTERFACE   the chat box the user sees        │
            │                                                       │
            │  5. PLUMBING   login, database, background jobs,      │
            │                deploy — so strangers can use it       │
            └──────────────────────────────────────────────────────┘
```

You build all five. The codebase it reads is just fuel.

---

## 5. The concepts, in plain words

- **LLM (Large Language Model):** the AI you call over the internet (Claude). You send text,
  it sends text back. You pay per *token* (chunk of text). It has a **context limit** — only so
  much text fits in one request. (This limit is *why* we need retrieval.)

- **Embedding:** turning a piece of text into a list of numbers (a "vector") that captures its
  *meaning*. Two pieces with similar meaning have similar numbers. This is how the computer finds
  "relevant" code without exact word matches.

- **Vector store / vector database:** where we keep all those number-lists so we can quickly ask
  "which pieces are most similar to this question?"

- **Chunking:** how we cut the code into pieces before embedding. Cut badly (random 500-char
  blocks) → you split a function in half → garbage answers. Cut smartly (one function = one
  chunk, using a code **parser/AST**) → good answers.

- **RAG (Retrieval-Augmented Generation):** the fancy name for "retrieve relevant pieces, then
  let the LLM generate an answer from them." That's pieces 1–2 above.

- **Hybrid search:** combine *semantic* search (meaning, via embeddings) with *keyword* search
  (exact names, like a variable called `user_token`). Each catches what the other misses.

- **Tool / function calling:** letting the LLM ask your code to *do* something — "call
  `read_file('auth/login.py')`" — instead of only talking. You run the function and feed the
  result back.

- **Agent:** an LLM in a **loop** — think → call a tool → look at the result → think again →
  … → answer. This lets it *navigate* the repo across several steps instead of one-shot guessing.

- **Grounding:** forcing every claim to be backed by a real source (citation), and making it
  say *"I don't know"* when the sources don't support an answer. This is what makes it
  *trustworthy*.

- **Evals (evaluations):** your own test set of questions with known answers, scored
  automatically, so you can tell whether a change made the app **better or worse**. Almost no
  beginner can do this. You will. It's the project's safety net.

---

## 6. Can it really understand ANY repo, ANY language? (No — and that's correct)

| The fantasy (impossible) | The real v1 (buildable, still impressive) |
|---|---|
| Understands any repo, any language | **Great at Python**, reasonable-size repos |
| Always correct | Often correct, **always shows its source so you can check** |
| Comprehends everything at once | **Retrieves the relevant slice** per question |
| Magic | **Measurable** — you can prove it's getting better |

Three walls and the real-engineer move for each:

1. **Any language?** The AI can *reason* about most languages, but *smart chunking* needs a
   little parser **per language**. → Pick **Python first**, do it well; other languages are an
   afternoon later, not a rewrite.
2. **Any size?** A 2-million-line repo is too big/tangled. → Target **small-to-medium** repos —
   95% of what people actually need help with.
3. **Always right?** No. → **Citations** (verify in 2s) + **evals** (track accuracy). The number
   going up *is* the project.

**Scoping down is not cheating — it IS the job.** Juniors try to build the fantasy and drown.
Seniors carve off the sharp, useful slice. Learning to make exactly these cuts is half of what
this project teaches you.

---

## 7. Could it earn money?

Maybe — later, and only as a bonus. You're building it **to learn**. But the shape is right:
real pain + a trustworthy AI answer + deployable. If you ever monetize, it'd be usage limits +
a paid tier (Week 12 has a stub experiment). Don't let money pressure derail the learning — a
finished, deployed, understood project is the win.

---

## 8. Definition of success (end of 12 weeks)

- A **deployed** app at a public URL where a stranger can index a Python repo and ask questions.
- Answers **cite real file:line** and **refuse when unsure**.
- An **eval score** you tracked over time and can talk about.
- A README + demo so it stands as a **portfolio piece** you genuinely understand top to bottom.
- You hit every layer — API, LLM, RAG, agents, evals, DB, auth, async, Docker, deploy — by
  *needing* it, not reading about it.
