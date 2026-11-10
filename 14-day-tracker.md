# 14-Day Accelerated Plan for repo-sage (Revised & Detailed)

You are currently on **Day 4**. The first 3 days (Foundations, Dumb Loop, Naive RAG) are marked as complete based on your codebase. Here is the *highly detailed* breakdown for every single day moving forward.

---

### [X] Day 1: Foundations: a running FastAPI app + project skeleton
*(Completed)*

### [X] Day 2: The dumbest loop (your magic moment)
*(Completed)*

### [X] Day 3: Naive RAG: chunk -> embed -> retrieve
*(Completed)*

---

### [X] Day 4: Smart chunking (AST) + real file:line citations
**Focus Area:** Moving from blind character-slicing to intelligent, structure-aware chunking and grounding the LLM to cite its sources.
**The Struggle:** Preventing hallucinations and ensuring every response can be verified instantly by a human clicking the exact file and line number. You also have to handle API idempotency so indexing twice doesn't bloat your database.
**Details & Try It:**
*   **Structured Citations:** In `rag/ask.py`, rewrite your prompt to strictly demand `SOURCES: [file:line]` at the end of the text. Parse this string in Python to extract the clean list.
*   **A/B Testing:** Run 5 questions through your new AST chunker vs the old one. Verify that the retrieved code is complete functions, not broken syntax.
*   **Re-Index Hygiene:** Create a `POST /index` route in your FastAPI app (`app/api`). Make sure to wipe the old index data *before* running `chunk_repo()` so it is completely idempotent.

---

### [X] Day 5: Hybrid search + reranking
**Focus Area:** Combining exact keyword search (BM25) with semantic search (Vector) and then re-ordering the results.
**The Struggle:** Vector search finds concepts but fails at exact variable names (e.g., `user_id_x7`). BM25 finds exact words but misses concepts. Combining them requires normalizing scores.
**Details & Try It:**
*   Implement BM25 text search alongside your existing vector search.
*   Run both searches simultaneously for a query.
*   Combine the scores (Reciprocal Rank Fusion) so exact matches and conceptual matches bubble to the top.
*   Introduce a lightweight Cross-Encoder (reranker) to re-score the top 20 combined results for maximum precision.

---

### [X] Day 6: Tools & structured output
**Focus Area:** Giving the LLM the ability to take actions instead of just talking.
**The Struggle:** Forcing an unpredictable language model to output perfectly structured JSON that your Python code can parse and execute without crashing.
**Details & Try It:**
*   Define a tool schema (e.g., a function `search_code(query)`).
*   Prompt the LLM to return a JSON object with the function name and arguments when it needs more information.
*   Write Python code to catch that JSON, execute the actual Python function, and return the result back to the LLM.

---

### [ ] Day 7: The agent loop
**Focus Area:** The ReAct (Reason + Act) loop. Letting the LLM think, take an action, observe the result, and decide if it's finished.
**The Struggle:** The loop can run infinitely if the LLM gets confused. You have to build in hard stops (max iterations).
**Details & Try It:**
*   Wrap your LLM call in a `while` loop.
*   Give it a "scratchpad" (context history) of what tools it has called so far.
*   If it calls `search_code`, run it, append the observation to the context, and loop again.
*   If it outputs an `answer` JSON, break the loop and show the user.

---

### [ ] Day 8: Trust: evals, grounding, and "I don't know"
**Focus Area:** Automated testing for AI. Building an eval suite that scores your app's accuracy.
**The Struggle:** You can't eyeball 100 questions every time you change the code. You need a script to test if the answers are actually right and if the citations are real.
**Details & Try It:**
*   Write 20 diverse question/answer pairs about a sample repo.
*   Write an eval script that runs your app against these 20 questions.
*   Use a larger, smarter model (like GPT-4) as an "evaluator" to score if your app's answer matched the ground truth and if it hallucinated.
*   Tune the prompt so the app confidently says "I don't know" instead of guessing.

---

### [ ] Day 9: Database + auth (it becomes a real app)
**Focus Area:** Multi-tenant architecture. Moving from a single local script to a web app with users.
**The Struggle:** Isolating data. User A should never be able to search User B's repositories.
**Details & Try It:**
*   Swap any local files for SQLite or Postgres.
*   Add a `users` table and a `repositories` table.
*   Implement basic JWT authentication.
*   Ensure every vector search is filtered by `user_id` so data doesn't leak.

---

### [ ] Day 10: Background indexing, caching, streaming, logging
**Focus Area:** Performance and user experience.
**The Struggle:** Indexing a large repo takes minutes. You can't block an HTTP request for that long.
**Details & Try It:**
*   Offload the `/index` endpoint to a background worker (like Celery or background tasks in FastAPI).
*   Add Redis caching so identical questions return instantly.
*   Implement Server-Sent Events (SSE) so the LLM answer streams word-by-word to the client instead of hanging for 10 seconds.

---

### [ ] Day 11: Docker + deploy + a minimal frontend
**Focus Area:** Shipping it to the real world.
**The Struggle:** Dev vs Prod environments. The "it works on my machine" problem.
**Details & Try It:**
*   Write a `Dockerfile` and a `docker-compose.yml` to spin up the app and the database together.
*   Build a simple HTML/JS frontend with a chat box that handles the SSE stream.
*   Deploy to a service like Render, Railway, or Fly.io. Ensure environment variables hold your API keys securely.

---

### [ ] Day 12: Polish, README, demo, portfolio
**Focus Area:** Making the project legible to recruiters, peers, and strangers.
**The Struggle:** Explaining a complex technical architecture concisely.
**Details & Try It:**
*   Dogfood the app and fix the 5 most annoying bugs.
*   Write an `ARCHITECTURE.md` explaining why you chose AST chunking over naive chunking.
*   Record a 2-minute demo video showing the app citing real code lines.

---

### [ ] Day 13: Buffer / Catch-up day
**Focus Area:** Debt collection.
**Details:** Use this day to fix any bugs lingering from the Docker deployment or the background workers. Run your full eval suite (from Day 8) against the live production URL.

---

### [ ] Day 14: Final Review & Launch
**Focus Area:** Go live.
**Details:** Post your project on GitHub, write a LinkedIn or blog post detailing the hardest struggle you faced (likely the Agent Loop or Grounding), and share the demo video. Celebrate!
