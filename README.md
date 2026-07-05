# repo-sage

**Point it at a codebase. Ask it anything. Get a real answer — with the exact file and line to prove it.**

---

Ever opened an unfamiliar codebase and felt completely lost? Hundreds of files, no idea where
anything happens, afraid to change one line in case the whole thing falls over. Everyone feels
this — new hires, open-source contributors, you on your own project three months later.

Plain search doesn't help. `grep` finds *text*, but it can't *reason*. Ask "where does this app
check the password?" and grep just hands you every file with the word "password" in it. You're
still doing the thinking.

**repo-sage does the thinking.** You point it at a repo, ask in plain English, and it answers —
and it always shows you where it got the answer, so you can verify in two seconds.

---

## What it feels like

```
You:  Where does this project check if a password is correct?

repo-sage:  In auth/login.py:40–55 — it hashes the input you typed and
            compares it against the stored hash.
            Sources: auth/login.py:40, utils/hashing.py:12

You:  What breaks if I delete utils/hashing.py?

repo-sage:  Three files import it: login.py, signup.py, reset_password.py.
            Deleting it breaks login, signup, and password reset.
```

It read the **real code**, found the **real answer**, and **proved it with a citation.** No
guessing. No bluffing.

---

## What makes it different

- **It cites everything.** Every answer points to a real `file:line` you can open and check. If
  it can't back a claim up, you'll see exactly why.
- **It says "I don't know."** When the answer isn't in the code, it tells you — instead of making
  something up that sounds right. That honesty is the whole point.
- **It actually navigates the repo.** It can read files, search for symbols, and trace what calls
  what — taking several steps to figure out an answer, the way a real engineer would.

---

## How it works (the one big idea)

A codebase is way too big to hand to an AI all at once. So repo-sage does two boring things, fast:

1. **Retrieve** — out of thousands of pieces of code, find the handful actually relevant to your
   question. (Like a librarian grabbing the 3 right books instead of reading the whole library.)
2. **Reason** — hand *only those few pieces* to the AI and say: "answer using just this, and cite it."

It never understands the whole repo at once. It understands the small, relevant slice it pulled
for your specific question. That's the trick that makes the impossible-sounding thing possible.

---

## Built with

Python · FastAPI · Claude (Anthropic) · embeddings + a vector store for search · an agent that
uses tools (`read_file`, `grep`, `find_callers`) · and an eval suite that scores how often the
answers are actually right.

---

## Scope (on purpose)

v1 is **great at Python repos of reasonable size** — hundreds of files, the kind of project people
actually need help with. Answers are *often* correct and *always* cite their source, so you're
never trusting it blindly. More languages and giant repos can come later on the same foundation.

---

## Status

🚧 **Actively building.** repo-sage is being built end-to-end over 12 weeks, learning each piece
of the stack by hitting the wall it solves. Curious about the plan, or want to follow along?

- **The plan:** [`ROADMAP.md`](./ROADMAP.md)
- **The plain-English deep dive:** [`UNDERSTAND-THE-PROJECT.md`](./UNDERSTAND-THE-PROJECT.md)
- **Where I am right now:** [`tracker.md`](./tracker.md)
