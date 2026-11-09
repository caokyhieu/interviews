# 11. Projects and interview questions

> **Goal of this chapter.** Turn reading into skill. Six build projects, ordered by difficulty, and 30 interview questions with short model answers. Cover the answers and say yours out loud first.

---

## Part A — Six projects

Each project lists **what to build**, **what to measure**, and **what you'll be able to say in an interview**. Put them on GitHub with a README showing your eval results. That's worth more than any certificate.

### Project 1 — A RAG system that measures itself (1–2 weekends)
- **Build:** Q&A over a real corpus (your company's public docs, a textbook, SEC filings). Start naive (fixed chunks + dense search), then add, one at a time: hybrid BM25+dense with RRF → reranker → contextual retrieval → query rewriting.
- **Measure:** write 50–100 questions with reference answers. Track recall@10, faithfulness and answer correctness after each change (Ragas or your own judge, calibrated on 30 hand labels).
- **Interview line:** "Hybrid search gave +X recall, the reranker +Y, contextual retrieval +Z. Here's the table."

### Project 2 — An agent from scratch, then with an SDK (1 weekend)
- **Build:** the raw loop (ch. 4 §4.1) with 3–4 tools (web search, calculator, file read/write), directly on a model API. Add a max-steps limit, error handling and cost tracking. Then rebuild with the Claude Agent SDK or LangGraph and compare.
- **Measure:** 20 tasks; success rate, steps, tokens, cost per task.
- **Interview line:** "I know what the framework does for me because I wrote the loop myself."

### Project 3 — An MCP server on the 2026-07-28 spec (1 weekend)
- **Build:** an MCP server exposing something useful (your notes, a Postgres DB, a public API). Stateless handlers, an MRTR confirmation for a write action, TTLs on `tools/list`. Connect it to Claude Code or another client.
- **Bonus:** write a SKILL.md that teaches the agent *how* to use your server well.
- **Interview line:** "I've migrated to stateless MCP and I know why the spec changed."

### Project 4 — Evals and tracing for Projects 1 and 2 (1 weekend)
- **Build:** add Langfuse or Phoenix tracing. Do error analysis: read 50 traces, write notes, group them into failure categories. Write a code-based check or a calibrated LLM judge for the top 3 categories. Run the eval suite in CI (GitHub Actions).
- **Measure:** judge–human agreement; pass^k over 5 runs for the agent.
- **Interview line:** "Here's my failure taxonomy and how I validated the judge."

### Project 5 — LoRA fine-tune vs prompting (1–2 weekends)
- **Build:** pick a narrow task (extract fields from invoices, classify support tickets, SQL generation for one schema). Generate training data with a frontier model (distillation), LoRA-tune a 1–8B open model with Unsloth/TRL on Colab or one GPU.
- **Measure:** accuracy, latency and cost vs the frontier model with a good prompt.
- **Stretch:** a small GRPO run with a verifiable reward (e.g. SQL executes and returns the right rows) using TRL's GRPOTrainer.
- **Interview line:** "The 3B model matched 94% of the frontier model's accuracy at 1/30 of the cost."

### Project 6 — Serve it and speed it up (1 weekend)
- **Build:** serve your fine-tuned model with vLLM or SGLang. Benchmark it; then turn on prefix caching, FP8 quantization and speculative decoding (EAGLE/DFlash if available for your model).
- **Measure:** TTFT, TPOT and throughput at concurrency 1, 8 and 32; quality after quantization.
- **Interview line:** "Speculation gave 2.3× at concurrency 1 but only 1.1× at 32. Here's why."

---

## Part B — 30 interview questions

### RAG and knowledge bases
1. **Design a RAG system for 10M internal documents with per-user permissions.**
   Layout-aware parsing → structure-aware chunks with context → hybrid index (dense + BM25) with **permission metadata filtering before ranking** → rerank → generate with citations. Incremental indexing plus deletion. Separate retrieval and answer evals. Poisoning defenses. Discuss cost (embedding refresh), latency budget and caching.
2. **Recall is low. How do you debug it?** Build a labelled retrieval set; inspect misses: parsing problems? chunk boundaries? vocabulary mismatch (add BM25/query rewrite)? wrong embedding model for the domain? too-small k before reranking?
3. **Bi-encoder vs cross-encoder vs late interaction?** Separate encoding (fast, shallow) vs joint encoding (accurate, slow, used for reranking) vs per-token vectors with MaxSim (in between, storage-heavy).
4. **When would you pick long context over RAG?** Small, stable corpora; holistic questions; with prompt caching. RAG for large or changing corpora, access control and citations.
5. **What's GraphRAG and when is it worth it?** An LLM-extracted entity graph + community summaries, for global and multi-hop questions. Expensive indexing, so not worth it for simple lookup.
6. **How do you evaluate a RAG system without labelled data?** Bootstrap synthetic Q&A from documents (then filter them by hand), use reference-free metrics (faithfulness, context relevance) with a calibrated judge, and mine production logs for real questions.

### Agents
7. **Workflow or agent for a customer-support bot?** Mostly a workflow: route by intent, with fixed flows for refunds etc. An agent only for open-ended troubleshooting. Human escalation. Evaluate with τ-bench-style simulated users and pass^k.
8. **How do you design tools for an agent?** Few high-level tools, doc-quality descriptions, unambiguous typed params, concise outputs with pagination, actionable errors. Iterate using failed transcripts.
9. **Your agent loops forever. Fixes?** Max steps and a budget; detect repeated identical calls; better error messages; progress notes/todo list; a stop criterion in the prompt; check whether a tool returns ambiguous results.
10. **When is multi-agent worth it?** Parallel breadth-first tasks (research). It costs many times more tokens and brings coordination and error-spreading risks. Avoid it for tightly coupled work.
11. **How would you build an agent that runs for 8 hours?** Durable session log outside the context; a stateless harness that can resume; compaction plus notes files; sandboxes as disposable resources; checkpoints; credentials outside the sandbox; human check-ins for risky steps (brain/hands/session).
12. **What is context engineering?** Choosing everything the model sees each step (instructions, tools, retrieved data, memory, history), within a budget, with cache-friendly ordering, just-in-time retrieval, compaction and sub-agent isolation.
13. **How do you reduce an agent's cost by 5×?** Prefix-cache hits (stable prefix), trimming tool outputs, routing easy steps to smaller models, lower reasoning effort where it's safe, sub-agents to keep contexts small, workflow compilation/distillation once the task is stable.
14. **How would you add memory to an assistant?** Decide the memory types (semantic facts, episodic history, procedural rules); async extraction with dedupe and conflict updates; scoped storage (user/org); hybrid retrieval with recency; allow users to view and delete; evaluate on LongMemEval-style questions.

### Protocols
15. **What is MCP and why did it matter?** A standard protocol for tools, resources and prompts. It turns N×M integrations into N+M.
16. **What changed in MCP 2026-07-28?** Stateless core (no handshake/session IDs), MRTR instead of server-initiated elicitation, header routing, cacheable lists, an extensions framework (Tasks, Apps, EMA), auth hardening with CIMD; Roots/Sampling/Logging deprecated.
17. **MCP vs A2A vs Skills?** Tools vs peer agents vs packaged know-how with progressive disclosure.

### Evaluation
18. **How do you build an eval set from scratch?** Collect traces → error analysis (open then axial coding) → prioritise failure categories → code checks where possible → calibrated binary LLM judges for the rest → regression suite in CI.
19. **How do you validate an LLM judge?** Human labels on 100–200 examples, a train/test split, measure agreement (TPR/TNR, κ), iterate the rubric, re-validate when the judge model changes; control for position and length bias.
20. **pass@k vs pass^k?** Capability (any success) vs reliability (all succeed). Production cares about pass^k.
21. **How do you evaluate a coding agent?** Hidden tests in a sandbox (SWE-bench style), final repo state, plus trace metrics (steps, cost), plus checks for reward hacking (edited tests?).

### Post-training
22. **When fine-tune vs RAG vs prompt?** Prompt first; RAG for knowledge; fine-tune for format, style, cost and latency (distillation) or verifiable-task skill (RL).
23. **Explain LoRA.** Freeze W, learn a low-rank ΔW = BA. Few trainable params, swappable adapters. QLoRA = 4-bit base.
24. **Explain GRPO and one of its fixes.** Sample a group per prompt, use group-normalised rewards as advantages, no critic. DAPO: clip-higher, dynamic sampling (drop zero-variance groups), token-level loss, overlong shaping. Dr.GRPO removes length bias. GSPO uses sequence-level ratios.
25. **DPO in one sentence?** Directly optimise the policy on chosen/rejected pairs with a closed-form objective that equals RLHF's optimum, with no reward model and no RL loop.
26. **What is reward hacking? An example?** The policy exploits flaws in the reward, e.g. a coding agent that edits tests to pass. Mitigations: robust verifiers, held-out checks, monitoring traces, KL constraints.

### Inference
27. **Why is decode memory-bound, and what helps?** Little arithmetic per byte read. Batching, quantization, speculative decoding, KV reductions (GQA/MLA).
28. **Explain speculative decoding and what's new in 2026.** The drafter proposes, the target verifies in one pass, and it's lossless. New: parallel block drafting (P-EAGLE, DFlash with a diffusion drafter + KV injection); SGLang Spec V2 overlap scheduling; gains shrink at high batch.
29. **How do you cut TTFT for a long-prompt agent?** Prefix caching (stable prefix), chunked prefill, prefill/decode disaggregation, smaller context via compaction.

### Security
30. **How do you secure an email agent against prompt injection?** Break the lethal trifecta: least-privilege tools; untrusted email content processed by a quarantined model with no tools (dual-LLM/CaMeL); a validator outside the model for outbound actions; human confirmation showing the exact recipient and payload; egress allow-lists; credentials outside the sandbox; assume-compromise testing.

---

## Part C — Staying current (after this course)

Weekly (≈1 hour):
- **Engineering blogs:** Anthropic Engineering, OpenAI, Google DeepMind/Developers, LMSYS (serving), Hugging Face blog
- **Newsletters/people:** Sebastian Raschka (*Ahead of AI*), Latent Space, Simon Willison's blog (security, tools), Hamel Husain (evals), Interconnects (Nathan Lambert, RL/post-training), Turing Post
- **Papers:** Hugging Face Daily Papers, arXiv cs.CL/cs.AI; read the abstract + figures, and only go deeper on what touches your work
- **Specs/changelogs:** MCP blog, A2A releases, vLLM/SGLang release notes

A useful habit: for each new technique, write **one paragraph** in these notes answering *what problem, how, trade-off, when I'd use it*. That's exactly what interviewers probe.
