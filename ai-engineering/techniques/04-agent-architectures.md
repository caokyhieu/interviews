# Agent architectures and patterns: a deep dive

> **Where this fits.** Overview: [../04-agents.md](../04-agents.md) · Implementation: [../implementation/02-agents.md](../implementation/02-agents.md) · Code: [agent/](../code/aieng/agent/).
>
> **Format:** idea → diagram of the control flow → the running task executed with that pattern → pros/cons → evidence.
>
> **2026 note:** many of these patterns were invented when models couldn't plan or reflect by themselves. Modern reasoning models do much of it internally, between tool calls. The patterns are still worth knowing: each is a lever for a specific failure you'll see in evals.

---

## 0. Running task

> **"Book Alice a vegetarian dinner in Paris for 2 people, Friday 8 pm, at the best-rated place that has a table."**

Tools available:
| Tool | Does | Side effect? |
|---|---|---|
| `search_restaurants(city, diet)` | returns ~10 candidates | no |
| `get_rating(id)` | rating 1–5 | no |
| `check_availability(id, time, people)` | true/false | no |
| `book(id, time, people)` | makes the booking | **yes: needs approval** |

---

# Part A: Single-agent patterns

## A.1 Chain-of-thought and reasoning models

**Idea.** Think step by step before answering. Now built into reasoning models and controlled with an effort level.
```mermaid
flowchart LR
    IN["task"] --> TH["internal reasoning:<br/>need diet filter, rating,<br/>availability, then book"]
    TH --> OUT["answer or first tool call"]
```
Nearly free to use today (it's a parameter); it costs output tokens and latency. It's the foundation all other patterns build on.

---

## A.2 ReAct (reason + act)

**Idea.** A loop: think → call a tool → read the result → think again, until done.

```mermaid
sequenceDiagram
    participant M as Model
    participant T as Tools
    M->>T: search_restaurants(Paris, vegetarian)
    T-->>M: 10 candidates
    M->>T: get_rating(r1)
    T-->>M: 4.7
    M->>T: get_rating(r2)
    T-->>M: 4.2
    Note over M: ... one call per step, 10 ratings ...
    M->>T: check_availability(r1, Fri 20:00, 2)
    T-->>M: false
    M->>T: check_availability(r3, Fri 20:00, 2)
    T-->>M: true
    M->>T: book(r3, Fri 20:00, 2)
    T-->>M: confirmed
```

**Worked example.** About 23 sequential model calls. Each call re-sends the growing history. It adapts well ("r1 is full → try the next best"), but it's slow.

| Pros | Cons |
|---|---|
| adapts after every observation | sequential: one round trip per step |
| simple; handles open-ended tasks | history re-sent each step: cost grows fast |
| | can loop or wander without a global plan |

**Evidence.** Beat act-only and reason-only baselines on HotpotQA, FEVER, ALFWorld and WebShop (2022). **This is the default loop** ([loop.py](../code/aieng/agent/loop.py)).

---

## A.3 Plan-and-execute

**Idea.** A planner writes the steps; an executor runs each step; a re-planner revises the plan when reality differs.

```mermaid
flowchart TD
    T["task"] --> PL["PLANNER, strong model:<br/>1 search vegetarian in Paris<br/>2 rate candidates<br/>3 check availability best-first<br/>4 book first available"]
    PL --> EX["EXECUTOR, cheaper model or ReAct sub-loop:<br/>run step i"]
    EX --> CHK{"step result as expected?"}
    CHK -->|yes, more steps| EX
    CHK -->|no: all top 3 full| RP["RE-PLANNER:<br/>widen search to 9 pm or nearby areas"]
    RP --> EX
    CHK -->|all done| DONE["report"]
```

| Pros | Cons |
|---|---|
| a global view; the plan can be shown to and approved by a human | plans go stale when reality differs |
| cheaper executor models; progress tracking | rigid for exploratory tasks |

**Modern form.** The agent keeps its own **todo list** (Claude Code's todos, "plan mode").

---

## A.4 ReWOO (reasoning without observation)

**Idea.** Plan **everything up front with variables**, run all tools without calling the model in between, then write the answer once.

```mermaid
flowchart LR
    P["PLANNER, 1 model call:<br/>E1 = search_restaurants Paris, veg<br/>E2 = get_rating for each in E1<br/>E3 = check_availability top 3 of E2"] --> W["WORKER: execute E1, E2, E3<br/>no model calls"]
    W --> S["SOLVER, 1 model call:<br/>pick the best available<br/>from the evidence"]
```

**Worked example.** 2 model calls instead of ~23. But if all top 3 are full, E3 can't adapt, so the solver just reports "none available".

| Pros | Cons |
|---|---|
| far fewer tokens (history not re-sent after each tool) | can't adapt mid-plan |
| predictable | bad when results are surprising |

**Evidence.** The paper reports ~5× token efficiency on HotpotQA with a small accuracy gain (arXiv 2305.18323).

---

## A.5 LLMCompiler (parallel tool DAG)

**Idea.** Plan a **dependency graph** of tool calls and run everything whose inputs are ready **in parallel**.

```mermaid
flowchart LR
    S["search_restaurants"] --> R1["get_rating r1"]
    S --> R2["get_rating r2"]
    S --> R3["get_rating r3"]
    S --> A1["check_availability r1"]
    S --> A2["check_availability r2"]
    S --> A3["check_availability r3"]
    R1 & R2 & R3 & A1 & A2 & A3 --> J["JOINER: best-rated among available"]
    J --> B["book, after approval"]
```

**Worked example.** 6 lookups run at once. Wall time ≈ search + one lookup + book, instead of 8 sequential steps.

| Pros | Cons |
|---|---|
| latency: the paper reports up to 3.7× faster, 6.7× cheaper, ~9% more accurate than ReAct | gains depend on how parallelisable the task is |

**Modern form.** Native **parallel tool calls**: the model emits several `tool_use` blocks in one turn; our loop runs them in a thread pool.

---

## A.6 Reflexion (learn from failure by writing lessons)

**Idea.** After a failed attempt, write a **verbal lesson**, store it, and retry with the lessons in context.

```mermaid
flowchart TD
    TRY["attempt 1: booked r2 at 8 pm"] --> EVAL{"evaluator / checker"}
    EVAL -->|fail: r2 is a steakhouse,<br/>not vegetarian| REF["reflection: I trusted the search<br/>diet filter; verify the diet<br/>in get_details before booking"]
    REF --> MEMB[("reflection memory")]
    MEMB --> TRY2["attempt 2, with the lesson in context"]
    TRY2 --> EVAL
    EVAL -->|pass| DONE["done"]
```

| Pros | Cons |
|---|---|
| improves on retries without training | needs a reliable success signal |
| readable lessons | self-critique without external feedback often confirms its own mistakes |

**Evidence.** 91% pass@1 on HumanEval with GPT-4 (vs 80% baseline at the time) in the paper.

---

## A.7 Self-consistency and best-of-N

**Idea.** Sample several answers and vote, or pick the best with a verifier.
```mermaid
flowchart LR
    Q["task"] --> S1["sample 1: r3"] & S2["sample 2: r3"] & S3["sample 3: r5"] & S4["sample 4: r3"] & S5["sample 5: r1"]
    S1 & S2 & S3 & S4 & S5 --> V{"majority vote<br/>or verifier score"}
    V --> OUT["r3"]
```
N× cost; parallel; needs comparable answers or a verifier. Great for discrete answers (labels, numbers, choices).

---

## A.8 Tree of Thoughts / LATS (search over branches)

**Idea.** Explore several branches, evaluate them, and expand the promising ones (BFS/DFS in ToT; Monte Carlo tree search in LATS).
```mermaid
flowchart TD
    ROOT["task"] --> A["branch A: Marais area first"]
    ROOT --> B["branch B: highest rating citywide"]
    ROOT --> C["branch C: closest to Alice"]
    A -->|value 0.6| A1["expand A"]
    B -->|value 0.9| B1["expand B: check top 3"]
    C -->|value 0.3| PR["prune"]
    B1 --> B2["r3 available: book"]
```
**Evidence.** ToT: Game of 24 success 74% vs 4% for CoT (GPT-4). LATS: 92.7% HumanEval pass@1 (at the time).
**Trade-off.** Very expensive and needs a good state evaluator. Rare in production: reasoning models absorbed much of it.

---

## A.9 CodeAct (code as the action)

**Idea.** The agent writes a **program** that calls the tools, loops and filters, and only the final result comes back into the context.

```mermaid
flowchart LR
    M["model writes code"] --> SB["sandbox executes it"]
    SB -->|calls tools inside the code| TOOLS["search, rating, availability"]
    SB --> RES["only the final small result<br/>returns to the model"]
    RES --> M
```

**Worked example.** One model turn:
```python
cands = search_restaurants("Paris", "vegetarian")
ranked = sorted(cands, key=lambda r: get_rating(r.id), reverse=True)
best = next((r for r in ranked if check_availability(r.id, "Fri 20:00", 2)), None)
print(best.id if best else "none available")
```
10 ratings and several availability checks never enter the context. Only `r3` does.

| Pros | Cons |
|---|---|
| far fewer tokens and turns | needs a secure sandbox |
| loops, filtering, composition in one step | per-action approval is harder (keep `book` as a separate approved tool) |

**Evidence.** CodeAct reported up to ~20% higher success than JSON/text actions (arXiv 2402.01030). Now built into platforms (code execution, programmatic tool calling, MCP "code mode").

---

## A.10 Pattern comparison on the running task

| Pattern | Model calls | Adapts when r1 is full? | Latency | Tokens |
|---|---|---|---|---|
| ReAct | ~23 | ✓ | high | high |
| Plan-and-execute | ~6 + re-plans | ✓ via re-plan | medium | medium |
| ReWOO | 2 | ✗ | low | **lowest** |
| LLMCompiler / parallel calls | ~3 | ✓ via the joiner | **lowest** | medium |
| CodeAct | ~2 | ✓ (logic in code) | low | **low** |
| Reflexion | ReAct × attempts | ✓ across attempts | high | high |

---

# Part B: Workflow patterns (code decides the flow)

```mermaid
flowchart TB
    subgraph CHAIN["prompt chaining"]
        C1["extract preferences"] --> C2["search"] --> C3["write booking summary"]
    end
    subgraph ROUTE["routing"]
        RI["request"] --> RC{"classify"}
        RC -->|booking| RB["booking flow"]
        RC -->|cancel| RX["cancellation flow"]
    end
    subgraph PAR["parallelisation"]
        PI["task"] --> PA["check rating"] & PB["check availability"] & PCC["check reviews"]
        PA & PB & PCC --> PAG["aggregate"]
    end
    subgraph ORCH["orchestrator-workers"]
        OO["orchestrator splits dynamically"] --> OW1["worker"] & OW2["worker"]
        OW1 & OW2 --> OS["synthesise"]
    end
    subgraph EVO["evaluator-optimizer"]
        EG["generate"] --> EE{"evaluate"}
        EE -->|revise| EG
        EE -->|good| EOUT["output"]
    end
```
**Rule.** If you can draw the flowchart in advance, build a workflow, not an agent: it's cheaper, faster and testable.

---

# Part C: Multi-agent topologies

## C.1 Orchestrator–worker (supervisor)
```mermaid
flowchart TD
    LEAD["LEAD AGENT: plan, delegate, verify, synthesise"] -->|brief: Marais area| W1["worker 1, own context"]
    LEAD -->|brief: Latin Quarter| W2["worker 2, own context"]
    LEAD -->|brief: Montmartre| W3["worker 3, own context"]
    W1 -->|short summary| LEAD
    W2 -->|short summary| LEAD
    W3 -->|short summary| LEAD
    LEAD --> OUT["best option across areas"]
```
Parallel breadth and clean contexts, but it multiplies tokens and workers lack shared context. It's what our [`delegate_tool`](../code/aieng/agent/subagent.py) does.

## C.2 Hierarchical
```mermaid
flowchart TD
    TOP["top supervisor"] --> S1["supervisor: dining"]
    TOP --> S2["supervisor: transport"]
    S1 --> A1["search agent"] & A2["booking agent"]
    S2 --> A3["route agent"]
```
Scales to big tasks, but errors and latency grow with depth.

## C.3 Handoffs (swarm)
```mermaid
sequenceDiagram
    participant U as User
    participant T as Triage agent
    participant D as Dining agent
    participant B as Billing agent
    U->>T: book dinner and fix my card error
    T->>D: handoff with conversation
    D-->>U: booked r3 for Friday
    D->>B: handoff: card question
    B-->>U: ERR_4012 means the card was declined...
```
Each specialist has a small prompt and tool set. Risks: context lost at handover, and agents passing the conversation back and forth.

## C.4 Pipeline (fixed roles)
```mermaid
flowchart LR
    R["researcher: candidates"] --> AN["analyst: ranking"] --> BK["booker: availability + booking"] --> QA["QA: verify constraints"]
```
Mirrors a human process with structured handoffs. Rigid, and errors flow downstream (MetaGPT, ChatDev).

## C.5 Group chat
```mermaid
flowchart LR
    MGR["chat manager<br/>picks next speaker"] --> A["agent A"] & B["agent B"] & C["agent C"]
    A & B & C --> TH[("shared thread")]
    TH --> MGR
```
Flexible, but chatty, costly, and hard to terminate (AutoGen).

## C.6 Debate
```mermaid
flowchart LR
    Q["question"] --> D1["agent 1 answer"] & D2["agent 2 answer"]
    D1 -->|critique| D2
    D2 -->|critique| D1
    D1 & D2 --> R{"after N rounds:<br/>judge or consensus"}
```
Can improve factuality; costs N×; can converge on a confident wrong answer.

## C.7 Blackboard
```mermaid
flowchart LR
    BB[("shared blackboard:<br/>candidates, ratings, availability")] <--> A1["search agent"]
    BB <--> A2["rating agent"]
    BB <--> A3["booking agent"]
    CTRL["controller: who acts next"] --> A1 & A2 & A3
```
Loose coupling via shared state; needs coordination and conflict rules.

### What the evidence says about multi-agent systems
```mermaid
flowchart LR
    MA["multi-agent system"] --> WIN["WINS when work is parallel and<br/>loosely coupled; Anthropic research system:<br/>large gain but ~15x tokens of chat;<br/>token usage explained most of the gain"]
    MA --> FAIL["FAILS via MAST taxonomy, 14 modes:<br/>1 specification / system design<br/>2 inter-agent misalignment<br/>3 task verification"]
    MA --> CON["Cognition, Don't Build Multi-Agents:<br/>coupled work split across agents<br/>loses context, causes conflicting decisions"]
```
**Design rules:** complete briefs · disjoint scopes · the lead **verifies** worker outputs · budgets on spawning.

---

# Part D: Tool-use patterns

```mermaid
flowchart TB
    subgraph NATIVE["native function calling"]
        N1["tool schemas in context"] --> N2["model emits a structured call"] --> N3["your code runs it"]
    end
    subgraph SEARCHT["tool search / deferred loading"]
        S1["only a search tool loaded"] --> S2["model searches: booking"] --> S3["book tool definition loaded"]
    end
    subgraph PTC["programmatic tool calling"]
        P1["model writes code"] --> P2["code calls your tools in a sandbox"] --> P3["only the final result returns"]
    end
    subgraph MCPB["MCP"]
        M1["agent"] <-->|protocol| M2["external tool servers"]
    end
```

| Pattern | Pros | Cons |
|---|---|---|
| native function calling (+ `strict` schemas) | reliable, typed | every definition costs context |
| parallel calls | latency | all results must return in one message |
| tool search / deferred loading | scales to hundreds of tools | a search step |
| programmatic tool calling / CodeAct | big token savings | sandbox; less per-call control |
| MCP | reuse across agents | supply-chain risk; context bloat |
| skills | near-zero idle context | quality control |
| computer use / browser | any UI | slow, brittle, security-sensitive |

---

# Part E: Control and reliability patterns

```mermaid
flowchart LR
    TODO["todo list / plan file"] --> LOOP["agent loop"]
    LOOP --> VER["verification step:<br/>re-check diet, time, party size"]
    VER --> HITL{"irreversible action?"}
    HITL -->|yes| APP["human approval showing<br/>exact args: r3, Fri 20:00, 2 people"]
    HITL -->|no| RUN["run"]
    APP --> RUN
    LOOP --> LOG[("durable event log:<br/>resume after crash")]
    LOOP --> BUD["budgets: steps, tokens,<br/>dollars, time"]
    LOOP --> ADV["advisor: ask a stronger model<br/>when stuck"]
```

| Pattern | Purpose |
|---|---|
| todo list / plan file | coherence on long tasks; survives compaction |
| verification step | catch errors before "done" |
| durable execution (event log, resumable harness) | crash recovery; runs lasting hours or days (brain/hands/session) |
| human-in-the-loop | approve risky actions with the exact arguments |
| budgets | bound runaway behaviour; graceful wrap-up |
| advisor / escalation | a cheaper model asks a stronger one when stuck |
| idle-time speculation (IdleSpec, 2026) | plan ahead while waiting on slow tools |
| workflow compilation (2026) | distil a stable multi-call workflow into one fine-tuned call |

---

# Part F: Decision guide

```mermaid
flowchart TD
    A["Can you draw the steps in advance?"] -->|yes| W["workflow: chaining, routing,<br/>parallel, evaluator-optimizer"]
    A -->|no| B["single agent: ReAct loop<br/>+ good tools + todo list"]
    B --> C{"evals show..."}
    C -->|slow: many independent lookups| P["parallel calls / LLMCompiler DAG"]
    C -->|token cost from big data| CA["CodeAct / programmatic tool calling"]
    C -->|wrong but checkable answers| RF["verification + Reflexion;<br/>best-of-N with a verifier"]
    C -->|loses track on long tasks| PL["plan-and-execute / todo file,<br/>compaction + notes"]
    C -->|breadth: many sources to read| MA["orchestrator-worker sub-agents,<br/>budgeted, disjoint scopes"]
    C -->|many tools confuse it| TS["tool search, skills,<br/>fewer and better tools"]
```

---

## Check your understanding
1. **How many model calls does ReWOO need for the running task, and what's the catch?** Two (plan + solve). It can't adapt if the top choices are full.
2. **Why is LLMCompiler faster than ReAct?** Independent calls (ratings, availability) run in parallel following the dependency graph.
3. **In CodeAct, why do the 10 ratings never enter the context?** They're processed inside the code; only the final choice is printed back.
4. **What does Reflexion need to work?** A reliable success signal (a checker, tests, a user confirmation).
5. **Name the three MAST failure categories.** Specification/system design, inter-agent misalignment, task verification.
6. **Where must the human approval sit in this task, and what must it show?** Before `book`, showing the exact restaurant, time and party size.

---

## Sources
- Wei et al., *Chain-of-Thought* (2022): arXiv 2201.11903 · Wang et al., *Self-Consistency* (2022): arXiv 2203.11171
- Yao et al., *ReAct* (2022): arXiv 2210.03629 · Xu et al., *ReWOO* (2023): arXiv 2305.18323 · Kim et al., *LLMCompiler* (2023): arXiv 2312.04511 · Wang et al., *Plan-and-Solve* (2023): arXiv 2305.04091
- Shinn et al., *Reflexion* (2023): arXiv 2303.11366 · Madaan et al., *Self-Refine* (2023): arXiv 2303.17651
- Yao et al., *Tree of Thoughts* (2023): arXiv 2305.10601 · Zhou et al., *LATS* (2023): arXiv 2310.04406
- Wang et al., *CodeAct* (2024): arXiv 2402.01030
- Anthropic, *Building effective agents* (2024), *How we built our multi-agent research system* (2025): https://www.anthropic.com/engineering
- Cemri et al., *Why Do Multi-Agent LLM Systems Fail? (MAST)* (2025): arXiv 2503.13657 · Cognition, *Don't Build Multi-Agents* (2025)
- Du et al., *Multiagent Debate* (2023): arXiv 2305.14325 · Hong et al., *MetaGPT*: arXiv 2308.00352 · Wu et al., *AutoGen*: arXiv 2308.08155
- Requesty roundup (IdleSpec, workflow compilation, May 2026): https://www.requesty.ai/blog/ai-agent-techniques-may-2026-self-evolving-managed-compiled
