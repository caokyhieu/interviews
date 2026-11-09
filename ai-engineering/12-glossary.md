# Glossary

One line each. The chapter number is where the term is explained.

| Term | Meaning | Ch. |
|---|---|---|
| **A2A (Agent2Agent)** | open protocol for agents to discover (Agent Cards) and delegate tasks to other agents; v1.0 Jan 2026, Linux Foundation | 5 |
| **AAIF** | Agentic AI Foundation, the Linux Foundation home (Dec 2025) for MCP, A2A and related projects | 5 |
| **Agent** | an LLM using tools in a loop, deciding its own next step | 4 |
| **Agent Card** | A2A JSON document describing an agent's skills, endpoint and auth; signed in v1.0 | 5 |
| **Agent-as-a-judge** | an evaluator that can use tools to inspect the environment, not just read transcripts | 6 |
| **Agentic RAG** | retrieval exposed as a tool the model calls when and how it chooses | 2 |
| **Agentic RL** | multi-turn RL training of tool-using agents with (usually) end-of-task rewards | 7 |
| **AGENTS.md / CLAUDE.md** | project instruction files loaded into a coding agent's context | 4, 5 |
| **BM25** | classic keyword ranking function; the sparse half of hybrid search | 2 |
| **Brain / hands / session** | Managed-agents architecture: stateless model+loop / disposable sandboxes and tools / durable event log | 4 |
| **CaMeL** | DeepMind's prompt-injection defense: privileged planner writes code, untrusted data carries capability tags | 9 |
| **Chunked prefill** | splitting long prompt processing into chunks mixed with decode steps | 8 |
| **CIMD** | Client ID Metadata Documents: MCP's replacement for Dynamic Client Registration | 5 |
| **ColBERT / late interaction** | one vector per token, scored with MaxSim; between bi- and cross-encoders | 2 |
| **ColPali** | retrieval over page *images* with a vision-language model and late interaction | 2 |
| **Compaction** | summarising the conversation history to free context space | 3 |
| **Context engineering** | deciding everything the model sees at each step, within a budget | 3 |
| **Context rot** | accuracy degrading as context length grows, even inside the window | 2, 3 |
| **Contextual retrieval** | prepending an LLM-written context sentence to each chunk before embedding and BM25 | 2 |
| **Continuous batching** | requests join/leave the running batch at every decode step | 8 |
| **Cross-encoder / reranker** | model that reads query + document together to score relevance | 2 |
| **DAPO** | GRPO successor: clip-higher, dynamic sampling, token-level loss, overlong shaping | 7 |
| **DFlash** | speculative decoding with a block-diffusion drafter and KV injection from the target | 8 |
| **Diffusion LM** | language model that refines many tokens in parallel instead of left-to-right | 10 |
| **Disaggregated serving** | prefill and decode on separate GPU pools, with KV transfer between them | 8 |
| **Distillation** | training a small model on a larger model's outputs | 7 |
| **DPO** | Direct Preference Optimization: preference tuning on chosen/rejected pairs, no reward model | 7 |
| **Dr. GRPO** | GRPO without length/std normalisation, removing length bias | 7 |
| **Dual-LLM pattern** | privileged LLM with tools never sees untrusted text; quarantined LLM reads it without tools | 9 |
| **EAGLE / P-EAGLE** | speculative drafters reading target hidden states; P-EAGLE drafts all tokens in one pass | 8 |
| **Elicitation** | MCP server asking the user for input mid-call (MRTR in 2026 spec) | 5 |
| **Episodic / semantic / procedural memory** | what happened / what is known / how to do things | 3 |
| **Error analysis** | reading traces, labelling failures, grouping into categories, before writing evals | 6 |
| **FP8 / MXFP4 / NVFP4** | low-precision number formats for faster, smaller models | 8 |
| **GraphRAG** | entity/relation graph + community summaries for global and multi-hop questions | 2 |
| **GRPO** | Group Relative Policy Optimization: critic-free RL using group-mean reward as the baseline | 7 |
| **GSPO** | GRPO variant with sequence-level importance ratios; more stable for MoE | 7 |
| **Hybrid architecture** | model mixing full-attention layers with linear-attention/SSM layers | 10 |
| **Hybrid search** | dense + sparse retrieval fused (usually with RRF) | 2 |
| **HyDE** | embed a hypothetical answer instead of the question for retrieval | 2 |
| **Indirect prompt injection** | malicious instructions hidden in content an agent reads | 9 |
| **KV cache** | stored attention keys/values of previous tokens, reused in decode | 8 |
| **Late chunking** | embed the whole document first, then pool token vectors per chunk | 2 |
| **Lethal trifecta** | private data + untrusted content + external communication = exfiltration risk | 9 |
| **LLM-as-judge** | using an LLM to grade outputs; must be calibrated against human labels | 6 |
| **LoRA / QLoRA** | low-rank adapter fine-tuning / the same on a 4-bit quantized base | 7 |
| **Managed Agents** | hosted agent infrastructure running the loop server-side (Anthropic Apr 2026, Google May 2026) | 4 |
| **MCP** | Model Context Protocol: standard for connecting models to tools, resources and prompts | 5 |
| **MCP Apps** | MCP extension letting servers ship interactive UI | 5 |
| **MoE** | Mixture of Experts: tokens routed to a few expert blocks; few active params per token | 10 |
| **MRTR** | Multi Round-Trip Requests: MCP server returns `input_required`, client retries with inputs | 5 |
| **MTP** | multi-token prediction heads, used for speculative decoding | 8 |
| **PagedAttention** | block-based KV-cache memory management (vLLM) | 8 |
| **Parallax** | 2026 architecture separating agent reasoning from execution with an external validator | 9 |
| **pass@k / pass^k** | at least one of k attempts succeeds / all k succeed (reliability) | 6 |
| **Prefill / decode** | prompt processing (compute-bound) / token generation (memory-bound) | 8 |
| **Prefix caching / prompt caching** | reusing KV cache for identical prompt prefixes | 3, 8 |
| **Progressive disclosure** | show only short descriptions; load full content when selected | 3, 5 |
| **RadixAttention** | SGLang's radix-tree prefix cache shared across requests | 8 |
| **ReAct** | reason → act → observe loop pattern for tool-using LLMs | 4 |
| **Reward hacking** | a policy exploiting flaws in its reward signal | 7 |
| **RLVR** | RL with verifiable (programmatic) rewards | 7 |
| **RRF** | Reciprocal Rank Fusion: merge ranked lists with Σ 1/(k + rank) | 2 |
| **Skill (SKILL.md)** | folder with a Markdown file (name + description frontmatter) teaching an agent a procedure; open standard Dec 2025 | 5 |
| **Speculative decoding** | drafter proposes tokens, target verifies them in one pass; lossless speedup | 8 |
| **SPLADE** | learned sparse retrieval: neural weighted keyword vectors | 2 |
| **SSM (Mamba)** | state-space sequence model with fixed-size state and linear-time compute | 10 |
| **Stateless MCP** | 2026-07-28 spec: no handshake or session IDs; each request is self-describing | 5 |
| **Sub-agent** | agent spawned by another agent with its own context; returns a summary | 3, 4 |
| **Test-time compute** | spending more inference tokens (thinking) for better answers | 10 |
| **Tool poisoning** | malicious instructions in MCP tool descriptions or outputs | 5, 9 |
| **TTFT / TPOT** | time to first token / time per output token | 8 |
| **Workflow** | LLM application where code, not the model, decides the control flow | 4 |
| **Workflow compilation** | distilling a multi-step agent pipeline into one fine-tuned model pass | 4 |
