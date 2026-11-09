# Technique deep dives

The concept chapters give the overview; the implementation guides show one working build. **These docs catalog the alternatives**: for each area, every major technique with how it works, pros, cons, cost, when to use it, published evidence, and pitfalls, followed by a comparison table and a decision guide.

| # | Deep dive | Techniques covered |
|---|---|---|
| 01 | [Chunking](01-chunking.md) | fixed, recursive, sentence, structure-aware, page-level, AST (code), tables, conversations · semantic breakpoint, cluster/DP, late chunking · contextual retrieval, LLM boundaries (LumberChunker), propositions (Dense X), multi-representation · sentence-window, parent–child/auto-merge, RAPTOR, mixed granularity · size/overlap evidence |
| 02 | [Retrieval and RAG architectures](02-retrieval-and-rag-architectures.md) | BM25, doc2query/query2doc, SPLADE, dense (Matryoshka, quantised), ColBERT, ColPali · flat/IVF/PQ/HNSW/DiskANN/ScaNN · RRF vs convex fusion · cross-encoder/LLM rerankers · HyDE, multi-query, decomposition, step-back, self-query · IRCoT, FLARE, Self-RAG, CRAG, Adaptive-RAG, Search-R1 · GraphRAG, LazyGraphRAG, LightRAG, HippoRAG, KAG · CAG, LongRAG, compression |
| 03 | [Memory](03-memory.md) | working memory (buffers, summaries, compaction, clearing, notes, sub-agents) · conversation RAG, extract-and-reconcile (Mem0), memory stream + reflection (Generative Agents), MemGPT/Letta, MemoryOS, knowledge graphs, **temporal KG (Zep/Graphiti, bi-temporal)**, HippoRAG, A-MEM, MIRIX/MemOS, file-based memory, experiential memory (Reflexion, ExpeL, Voyager, AWM), parametric, latent/KV, RL-trained (Memory-R1) · formation, updates, forgetting, retrieval signals · benchmarks and the Zep–Mem0 dispute |
| 04 | [Agent architectures](04-agent-architectures.md) | CoT/reasoning, ReAct, plan-and-execute, ReWOO, LLMCompiler, Reflexion, self-consistency, ToT/LATS, CodeAct · multi-agent topologies and the MAST failure taxonomy · tool-use patterns · control and reliability patterns |
| 05 | [Evaluation](05-evaluation-techniques.md) | reference metrics, execution checks · judge variants (binary, rubric, pairwise, G-Eval, fine-tuned, juries, agent-as-judge) and biases · RAG metrics · agent metrics · human, online, statistics (paired tests, PPI) · test-set construction (CheckList, contamination) |
| 06 | [Post-training](06-post-training-techniques.md) | LoRA, QLoRA, DoRA, LoRA+, rsLoRA, PiSSA, (IA)³, prompt tuning · SFT data techniques · RLHF, DPO, IPO, KTO, ORPO, SimPO, online DPO, RLAIF · ORM/PRM, rubric rewards · PPO, RLOO, GRPO, DAPO, Dr.GRPO, GSPO, VAPO · distillation (sequence, logit, on-policy) · merging (TIES, DARE) |
| 07 | [Inference optimisation](07-inference-optimization.md) | MQA/GQA/MLA, sparse/linear attention, FlashAttention, PagedAttention, prefix caching, KV quant/eviction/offload · batching, chunked prefill, disaggregation · TP/PP/DP/EP · GPTQ, AWQ, SmoothQuant, FP8, MXFP4/NVFP4, GGUF, QAT · speculative decoding family (draft, n-gram, Medusa, EAGLE-1/2/3, MTP, P-EAGLE, DFlash) · pruning · routing and caching |
| 08 | [Prompt and context engineering](08-prompt-and-context-engineering.md) | prompt structure, few-shot selection, many-shot ICL · APE, OPRO, DSPy/MIPROv2, TextGrad, GEPA · context assembly · habits that hurt modern models |
| 09 | [Security defenses](09-security-defenses.md) | spotlighting, classifiers, constitutional classifiers, instruction hierarchy, StruQ/SecAlign · six secure agent design patterns (action-selector, plan-then-execute, map-reduce, dual LLM, code-then-execute/CaMeL, context-minimisation) · IFC/taint, Parallax, sandboxing, egress · supply chain · AgentDojo-style testing |

## How each doc is built

- **One running example per doc**, used by every technique in it, so you can compare what each one does to the same input: the ACME billing document (chunking), four queries (retrieval), Alice moving from Berlin to Paris (memory), booking a vegetarian dinner (agents), a support bot's answers (evals), a text-to-SQL model (post-training), an 8B model on one GPU (inference), a support prompt (prompting), and a prompt-injection email (security).
- **Every technique has its own section** with a diagram of how it works (data flow, sequence, tree, graph or timeline), the running example worked through it, then pros/cons, evidence and pitfalls.
- **Diagrams are Mermaid** (press `⇧⌘V` in VS Code to render). All of them were parse-checked with the Mermaid 12 parser.

## How to use these
- **For interviews:** each doc ends with "check your understanding". Be able to state, for any technique, *the problem it solves, how it works, its cost, and when you wouldn't use it*.
- **For building:** start from the decision guide at the end of each doc, then go to the matching implementation guide and code.
- **On the evidence:** numbers are quoted with their source. Vendor-authored results (Mem0, Zep, Letta, Anthropic, LMSYS, etc.) are marked as such. Where independent studies disagree with popular advice (semantic chunking, chunk overlap, multi-agent systems), both sides are given.
