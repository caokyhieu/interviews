# Implementation guides

The concept chapters explain **what** and **why**. These guides explain **how**: the code step by step, the parameters to tune, the common errors (symptom → cause → fix), and a ranked list of improvements. Every guide is backed by runnable, tested code in [../code/](../code/).

| Guide | Builds | Code | Concept chapter |
|---|---|---|---|
| [01 RAG](01-rag.md) | chunking, BM25 + dense hybrid, RRF, reranking, contextual retrieval, citations, retrieval metrics | [aieng/rag/](../code/aieng/rag/) | [ch. 2](../02-rag-and-knowledge-bases.md) |
| [02 Agents](02-agents.md) | a guarded agent loop, tool registry, sub-agents, append-only context management | [aieng/agent/](../code/aieng/agent/) | [ch. 4](../04-agents.md) |
| [03 Context and memory](03-context-and-memory.md) | cache-friendly layout, trimming/compaction, long-term memory with reconcile | [agent/context.py](../code/aieng/agent/context.py), [memory.py](../code/aieng/memory.py) | [ch. 3](../03-context-engineering-and-memory.md) |
| [04 MCP and Skills](04-mcp-and-skills.md) | an MCP server on the 2026-07-28 spec (stateless, MRTR confirmation, cache hints), a SKILL.md | [mcp_server/](../code/mcp_server/) | [ch. 5](../05-protocols-mcp-a2a-skills.md) |
| [05 Evals](05-evals.md) | error analysis workflow, calibrated binary judges, pass@k / pass^k, bias correction, bootstrap CIs | [evals.py](../code/aieng/evals.py) | [ch. 6](../06-evaluation.md) |
| [06 Fine-tuning and RL](06-fine-tuning-and-rl.md) | LoRA SFT, DPO, GRPO (DAPO/Dr.GRPO/GSPO settings) with hardened verifiable rewards | [training/](../code/training/) | [ch. 7](../07-post-training-and-rl.md) |
| [07 Serving](07-serving.md) | vLLM/SGLang setup, quantization, speculative decoding, a TTFT/TPOT benchmark, KV capacity math | [serving/](../code/serving/) | [ch. 8](../08-inference-and-serving.md) |
| [08 Security](08-security.md) | capability declarations, taint tracking (lethal trifecta), egress allow-list, output sanitising | [security.py](../code/aieng/security.py) | [ch. 9](../09-security.md) |

## How to work through them

1. Set up the code (below) and run the tests. **Each test encodes one common error**, so reading the tests is a fast way to learn the pitfalls.
2. For each guide: read the walkthrough next to the code, run the exercises, then apply it to your own data.
3. Build order for a portfolio project: **Evals (05) → RAG (01) → Agents (02) → Context/Memory (03) → MCP (04) → Security (08)**. Add 06/07 if you're targeting ML/infra roles.

## Setup

```bash
cd ai-engineering/code
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -m pytest -q          # 46 tests, no API key or GPU needed
```
To call Claude for real, set `ANTHROPIC_API_KEY` (or run `ant auth login`) and use `aieng.llm.LLM()` in place of `FakeLLM`.

## What was verified, and what wasn't

- **Verified locally:** all pure-Python logic (chunking incl. sentence-window/semantic/cluster/late-chunk pooling, bi-temporal memory, BM25, RRF, MMR, filtering, metrics, agent-loop guards, context handoff, memory reconcile/scoping, eval statistics, security gate, SQL rewards) and the MCP server end to end over the SDK's in-memory client, negotiating protocol 2026-07-28. Structured-output schemas were checked to be strict (`additionalProperties: false`).
- **Written against current docs but not executed here:** real Claude API calls (no API key was used, to avoid spending money), `training/train.py` (needs a GPU and TRL), and the `serving/` commands (need a GPU and vLLM/SGLang). Library APIs move fast. If a flag errors, check the library's docs for your installed version.
