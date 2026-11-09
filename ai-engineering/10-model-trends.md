# 10. Model trends in 2026

> **Goal of this chapter.** A short tour of what's changing inside the models (reasoning, MoE, hybrid architectures, diffusion LMs, multimodality), with the practical consequences for engineers building on top of them.

---

## 10.1 Reasoning models and test-time compute

Since OpenAI o1 (Sept 2024) and DeepSeek-R1 (Jan 2025), frontier models **think before answering**: they generate a long internal chain of thought, trained with RL (ch. 7). More thinking tokens → better answers on hard problems. This is **test-time compute** scaling.

**What it means for engineers:**
- Most APIs expose a **thinking budget / effort level**. Choose it per task: low for classification or extraction, high for planning, math and debugging.
- Reasoning tokens cost money and latency. Route easy requests to low effort (ch. 8 §8.7).
- Models now interleave thinking with tool calls, which changes agent design: fewer hand-written "plan" steps are needed.
- Prompting changes: give goals and constraints, not step-by-step instructions. Over-specifying can hurt reasoning models.
- Research direction: *when* to retrieve or call tools during reasoning (ch. 2 §2.8).

---

## 10.2 Mixture of Experts (MoE)

Each token is routed to a few "expert" feed-forward blocks out of many. Total parameters are large (capacity); **active** parameters per token are small (speed).

- Example: **Step 3.5 Flash** (Feb 2026) reports frontier-level performance with only **11B active parameters**. DeepSeek-V3/R1, Qwen3-MoE, gpt-oss, Kimi K2 and most frontier models are MoE.
- **Engineering consequences:** the whole model must fit in memory (total params) even though compute follows active params. Expert parallelism across GPUs is needed at scale, and RL on MoE is less stable (one reason GSPO exists, ch. 7).

---

## 10.3 Hybrid architectures: attention + linear / state-space layers

Full attention costs O(n²) in sequence length and its KV cache grows linearly, which is painful for agents with long contexts. **State-space models (Mamba)** and **linear attention** keep a fixed-size state, so they have O(n) compute and constant memory, but they recall exact details less well.

**2026 answer: mix them.** Most layers are linear/SSM; a few are full attention for precise recall.
- **Nemotron 3 Super** (NVIDIA, Apr 2026): hybrid Mamba-Transformer aimed at long-context agent workloads.
- **Mamba-3** (Mar 2026): improved SSM.
- **Gated DeltaNet-2** (May 2026): linear attention with separate erase/write mechanisms.
- **Arcee Trinity** and Qwen3-Next-style models: hybrid designs.

Raschka's summary of 2026 architecture research: the focus is **"hybrid architectures, state space layers, MoE capacity allocation"** rather than simply scaling Transformers.

**Consequence:** much cheaper long contexts and smaller KV caches. Serving engines needed new kernels, and prefix caching is harder for SSM state.

---

## 10.4 Diffusion language models

Instead of generating left-to-right one token at a time, **diffusion LMs** start from masked or noisy text and refine many tokens **in parallel** over a few steps. Examples: LLaDA, Mercury (Inception Labs), Gemini Diffusion.
- Pros: very fast generation, and they can edit or infill anywhere.
- Cons: quality still generally trails autoregressive frontier models on reasoning, and the ecosystem is less mature.
- Already a practical spin-off: **DFlash uses a block-diffusion model as a speculative *drafter*** (ch. 8 §8.6). It combines parallel drafting with an autoregressive verifier.

---

## 10.5 Other trends worth a line each

- **Long context is normal:** 1M-token windows on several frontier models, but with context rot (ch. 3).
- **Native multimodality:** one model for text, image, audio and video in and out. **Computer-use agents** operate GUIs from screenshots (OSWorld is the benchmark).
- **Open-weight models close the gap:** Qwen, DeepSeek, Kimi, GLM, gpt-oss, Llama and Mistral lag frontier closed models by months, not years. Good for fine-tuning and private deployment.
- **Small models get good:** distillation (ch. 7 §7.6) makes 1–10B models viable for narrow tasks and on-device use.
- **Low precision everywhere:** FP8 training and FP4 inference (ch. 8 §8.5).

---

## 10.6 Check your understanding

1. **Why can an MoE model be fast but still need lots of memory?** Compute scales with *active* parameters per token, but all experts must be stored.
2. **What's the trade-off hybrid SSM/attention models make?** Linear/SSM layers give O(n) compute and a fixed state (cheap long context) but weaker exact recall. A few attention layers restore recall.
3. **How should you set reasoning effort?** Per task: low for simple extraction/classification, high for planning/math/debugging. Measure the quality-cost trade-off with evals.
4. **How do diffusion LMs help autoregressive serving today?** As fast parallel drafters for speculative decoding (DFlash).

---

## Sources
- Sebastian Raschka, *LLM Research Papers: The 2026 List (Jan–May)*: https://magazine.sebastianraschka.com/p/llm-research-papers-2026-part1
- DeepSeek-AI, *DeepSeek-V3 Technical Report* (2024): arXiv 2412.19437
- Gu & Dao, *Mamba* (2023): arXiv 2312.00752
- Nie et al., *LLaDA: Large Language Diffusion Models* (2025): arXiv 2502.09992
- *DFlash*: arXiv 2602.06036
- Google, *AI updates August 2026*: https://blog.google/innovation-and-ai/technology/google-ai-updates-august-2026/
