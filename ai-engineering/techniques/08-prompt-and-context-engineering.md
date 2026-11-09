# Prompt and context engineering techniques: a deep dive

> **Where this fits.** Overview: [../03-context-engineering-and-memory.md](../03-context-engineering-and-memory.md). Working-memory techniques (compaction, clearing, notes, sub-agents) are in [03-memory.md](03-memory.md) Part A. This doc covers **what goes into one request** and **how to optimise prompts systematically**.
>
> **Format:** idea → diagram → worked example → pros/cons.

---

## 0. Running example

Build the prompt for ACME's support bot, which answers from retrieved documents.

**Version 0 (typical first draft):**
```text
You are a SUPER helpful and friendly support assistant!!! ALWAYS be accurate. NEVER make things up.
Answer the question. Here are some docs: <paste of 8 chunks> Question: How long do Team customers have for refunds?
Today is 2026-09-19 14:03:22. User id: u_8812.
```
Problems: shouting, no structure, no output format, no abstention path, the question buried before nothing, and the timestamp and user ID at the top, which break prompt caching on every request.

---

# Part A: Prompt structure

## A.1 The anatomy of a good request

```mermaid
flowchart TB
    subgraph PREFIX["stable prefix: cacheable"]
        TOOLS["tool definitions, sorted"]
        SYS["system: role in one line, task,<br/>rules WITH reasons, output format"]
        EX["2-3 fixed examples"]
    end
    subgraph DYN["per-request: after the cache point"]
        MEMS["memories, dated"]
        DOCS["documents in tags"]
        Q["the question, LAST"]
        VOL["volatile data: time, IDs"]
    end
    TOOLS --> SYS --> EX --> MEMS --> DOCS --> Q --> VOL
```

**Version 1 (restructured):**
```text
[system]
You answer ACME billing questions for support agents, using only the provided documents.
- Cite the id of every document you use, e.g. [c1]; agents click through to verify.
- If the documents don't contain the answer, say so and name what's missing. Agents escalate those cases, so a guess costs more than "I don't know".
- Answer in 1-3 sentences; agents read answers aloud to customers.

[user]
<documents>
<doc id="c1">The Team plan has a 30-day refund window.</doc>
<doc id="c2">Refunds are issued within 14 days of purchase.</doc>
</documents>
<question>How long do Team customers have for refunds?</question>
(current date: 2026-09-19)
```

| Technique | Why it helps |
|---|---|
| clear task + criteria | current models follow instructions literally |
| rules with **reasons** | models generalise from the reason ("read aloud" → no Markdown tables) |
| XML tags | unambiguous boundaries between data and instructions |
| **documents first, question last** | long-context guidance reports up to ~30% better answers on complex multi-document inputs |
| explicit abstention | fewer confident hallucinations |
| volatile data at the end | the prefix stays byte-identical, so it stays cached |

## A.2 Structured outputs instead of "please return JSON"
```mermaid
flowchart LR
    SCHEMA["JSON schema:<br/>answerable, answer, citations"] --> API["output_config.format<br/>constrained decoding"]
    API --> VALID["always-valid JSON"]
    VALID --> CODE["code validates citation ids<br/>against the retrieved set"]
```
Replaces fragile parsing and retries. Assistant **prefill** (starting the reply with `{`) returns an error on current Claude models; use structured outputs. Code: [`LLM.parse`](../code/aieng/llm.py), [`answer()`](../code/aieng/rag/llm_steps.py).

## A.3 Grounding with quotes (long documents)
```mermaid
flowchart LR
    DOCS["long contract"] --> STEP1["step 1: extract the exact quotes<br/>relevant to the question"]
    STEP1 --> STEP2["step 2: answer using only those quotes"]
    STEP2 --> OUT["answer + quotes: easy to verify"]
```

## A.4 Reasoning control
```mermaid
flowchart LR
    TASK["task"] --> EFF{"effort level"}
    EFF -->|low| FAST["classification, extraction,<br/>sub-agents"]
    EFF -->|high / xhigh| DEEP["planning, debugging,<br/>multi-step agents"]
```
With adaptive thinking, don't also demand "think step by step" in the visible output. It duplicates the work and bloats answers.

---

# Part B: Examples (few-shot)

## B.1 Static vs dynamic examples
```mermaid
flowchart LR
    subgraph STATIC["static"]
        S1["same 3 examples every request"] --> SC["cache-friendly"]
    end
    subgraph DYNAMIC["dynamic, kNN"]
        Q["new question"] --> EMB["embed"]
        POOL[("example pool: 500 Q/A")] --> SEL["pick the 3 most similar"]
        EMB --> SEL
        SEL --> DC["better fit, but changes per request,<br/>so place AFTER the cache point"]
    end
```
**Evidence.** Semantically similar demonstrations beat random ones (Liu et al., 2021). Example **order** also changes results (Lu et al., 2021): shuffle during evals, and put the most representative example last.

## B.2 Contrastive examples
```text
<example quality="good">Team customers have 30 days to request a refund [c1].</example>
<example quality="bad" reason="uses the general 14-day rule instead of the Team-specific one">You have 14 days [c2].</example>
```
Contrastive pairs make the boundary between acceptable and unacceptable clear. They're especially useful for judges.

## B.3 Many-shot in-context learning
```mermaid
flowchart LR
    FEW["3 examples"] --> ACC1["accuracy x"]
    MANY["300-1000 examples<br/>in a long, cached context"] --> ACC2["can approach fine-tuning<br/>on some tasks"]
```
Agarwal et al. (2024). Costs tokens (reduced by prompt caching); no training needed.

---

# Part C: Automatic prompt optimisation

## C.1 The shared loop
```mermaid
flowchart LR
    P0["current prompt"] --> RUN["run on dev set"]
    RUN --> SCORE["metric: e.g. correct + cited"]
    SCORE --> PROPOSE["propose new prompt(s)"]
    PROPOSE --> P0
    SCORE --> TEST["finally: report on a held-out test set"]
```
Every method below is a different way to do **"propose new prompts"**.

## C.2 APE
```mermaid
flowchart LR
    DEMOS["input/output examples"] --> GEN["LLM generates 50 candidate instructions"]
    GEN --> EVAL["score each on the dev set"]
    EVAL --> BEST["keep the best, optionally resample around it"]
```

## C.3 OPRO (LLM as optimiser)
```mermaid
flowchart LR
    HIST["meta-prompt: previous prompts WITH scores,<br/>sorted"] --> OPT["optimiser LLM:<br/>write a better prompt"]
    OPT --> NEW["new prompt"] --> SC["score on dev"] --> HIST
```

## C.4 DSPy (prompts as learnable parameters)
```mermaid
flowchart TB
    PROG["program: modules with signatures<br/>retrieve -> answer(question, docs -> answer, citations)"] --> OPTZ["optimiser, e.g. MIPROv2"]
    METRIC["your metric function"] --> OPTZ
    TRAIN["50-500 examples"] --> OPTZ
    OPTZ --> BOOT["bootstrap demos: run the program,<br/>keep traces that pass the metric"]
    OPTZ --> INSTR["propose instructions per module"]
    BOOT & INSTR --> BAYES["Bayesian search over<br/>instruction x demo combinations"]
    BAYES --> COMPILED["compiled program:<br/>best prompts + demos per module"]
```
Works across models (recompile when you switch) and treats prompts like weights. Needs a metric and examples; there's a learning curve.

## C.5 TextGrad ("gradients" in text)
```mermaid
flowchart RL
    OUT["output"] --> CRIT["LLM critic: the answer used the<br/>14-day rule, not the Team rule"]
    CRIT --> GRADP["textual gradient for the prompt:<br/>tell the model to prefer plan-specific rules"]
    GRADP --> UPD["update the prompt"]
```
Feedback flows backward through a multi-step system, like backpropagation.

## C.6 GEPA (reflective prompt evolution)
```mermaid
flowchart TD
    POP["pool of candidate prompts"] --> SEL["pick a candidate from the Pareto front:<br/>best on at least one example"]
    SEL --> RUNS["run on a minibatch, collect TRACES + failures"]
    RUNS --> REFL["LLM reflects on the traces:<br/>why did it fail? propose a mutation"]
    REFL --> NEWC["new candidate (or merge two candidates)"]
    NEWC --> EVALC["evaluate"]
    EVALC --> POP
```
**Evidence.** The paper reports beating GRPO-based RL by ~10% on average (up to ~20%) with up to ~35× fewer rollouts, and beating MIPROv2 (arXiv 2507.19457).

| Method | Optimises | Needs | Notes |
|---|---|---|---|
| manual + evals | anything | a metric | the baseline; watch for dev-set overfitting |
| APE | instructions | examples + metric | simple search |
| OPRO | instructions | metric | the LLM sees the score history |
| DSPy MIPROv2 | instructions + demos per module | metric + 50–500 examples | the most practical framework |
| TextGrad | prompts / variables in compound systems | critic feedback | noisy, costly |
| GEPA | prompts via reflection on traces | metric + traces | sample-efficient |

---

# Part D: Context assembly per request

```mermaid
flowchart LR
    NEED["what does this step need?"] --> JIT["just-in-time: give tools<br/>search, grep, read"]
    NEED --> PD["progressive disclosure:<br/>skill/tool names first,<br/>details on demand"]
    NEED --> MEM["memories: few, dated, relevant"]
    NEED --> CMP["compress long inputs:<br/>quotes, summaries, LLMLingua"]
    JIT & PD & MEM & CMP --> ORDER["cache-aware order:<br/>stable first, volatile last"]
    ORDER --> CHECK["verify cache_read_input_tokens > 0"]
```

| Technique | Purpose |
|---|---|
| cache-aware ordering | any byte change invalidates everything after it |
| mid-conversation system messages | add instructions without editing the frozen system prompt (keeps the cache; history stays append-only) |
| just-in-time retrieval | smaller contexts; the model fetches what it needs |
| progressive disclosure | scales to many skills and tools |
| tool-definition hygiene | fewer, clearer tools in a fixed order |

---

# Part E: Prompt habits that hurt modern models

```mermaid
flowchart LR
    OLD["2023-era prompt"] --> A1["ALL CAPS, CRITICAL, NEVER"]
    OLD --> A2["micromanaged step lists"]
    OLD --> A3["think step by step in the output"]
    OLD --> A4["persona backstory"]
    OLD --> A5["prefill / forced tool_choice hacks"]
    A1 --> B1["calm, specific rules with reasons"]
    A2 --> B2["goals, constraints, definition of done"]
    A3 --> B3["adaptive thinking + effort"]
    A4 --> B4["one line of role + criteria"]
    A5 --> B5["structured outputs, strict schemas"]
```
Current models follow instructions **literally**: an emphasised rule gets over-applied, and a micromanaged procedure constrains better native reasoning.

---

# Part F: Decision guide

```mermaid
flowchart TD
    S["write a clear, structured prompt"] --> E["run the eval"]
    E --> F1{"format inconsistent?"}
    F1 -->|yes| FIX1["structured outputs or 2-3 examples"]
    F1 -->|no| F2{"quality inconsistent?"}
    F2 -->|yes| FIX2["error analysis -> targeted rules<br/>or examples per failure category"]
    F2 -->|no| DONE["ship"]
    FIX2 --> F3{"plateau, with metric + data?"}
    F3 -->|yes| OPT["DSPy MIPROv2 or GEPA"]
    OPT --> F4{"still a plateau, narrow high-volume task?"}
    F4 -->|yes| FT["fine-tune, see 06"]
```

---

## Check your understanding
1. **Name three problems with Version 0 of the running prompt.** Shouting and no reasons; no output format or abstention; volatile data at the top breaking the cache (also no structure; question placement).
2. **Where do dynamic few-shot examples go, and why?** After the cache breakpoint, because they change per request.
3. **What does DSPy's optimiser search over?** Instructions and bootstrapped demonstrations for each module, scored by your metric.
4. **What makes GEPA sample-efficient?** It reflects on full execution traces to propose targeted prompt mutations, and keeps a Pareto front of candidates.

---

## Sources
- Anthropic, *Prompt engineering* docs (incl. long-context tips): https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview
- Anthropic, *Effective context engineering for AI agents* (2025)
- Liu et al., *What Makes Good In-Context Examples for GPT-3?*: arXiv 2101.06804 · Lu et al., *Fantastically Ordered Prompts*: arXiv 2104.08786 · Agarwal et al., *Many-Shot ICL*: arXiv 2404.11018
- Zhou et al., *APE*: arXiv 2211.01910 · Yang et al., *OPRO*: arXiv 2309.03409
- Khattab et al., *DSPy*: arXiv 2310.03714 · Opsahl-Ong et al., *MIPROv2*: arXiv 2406.11695
- Yuksekgonul et al., *TextGrad*: arXiv 2406.07496 · Agrawal et al., *GEPA*: arXiv 2507.19457
- Liu et al., *Lost in the Middle*: arXiv 2307.03172 · Jiang et al., *LLMLingua*: arXiv 2310.05736
