# Implementing fine-tuning: LoRA SFT, DPO, GRPO with verifiable rewards

> Concepts: [../07-post-training-and-rl.md](../07-post-training-and-rl.md). Code: [../code/training/train.py](../code/training/train.py) (needs a GPU), [../code/training/rewards.py](../code/training/rewards.py) (tested locally). Library: Hugging Face TRL (`SFTTrainer`, `DPOTrainer`, `GRPOTrainer`) + PEFT.

---

## 1. Decide first: should you fine-tune?

Fine-tune only when evals show that prompting plus RAG plateaued, **and** one of these holds:
- a narrow, high-volume task where a small model would cut cost/latency 10×+ (distillation)
- a strict output format or style the prompt can't hold reliably
- a verifiable skill (SQL, code, math, tool use) you can reward automatically (GRPO)

You need: an eval set (evals guide), a baseline (the frontier model with a good prompt), and data.

---

## 2. SFT with LoRA

### Data
```json
{"messages": [{"role": "system", "content": "You convert questions to SQLite SQL. Answer as <sql>...</sql>."},
              {"role": "user", "content": "Schema: users(id, name, age)\nQuestion: names of users over 35"},
              {"role": "assistant", "content": "<sql>SELECT name FROM users WHERE age > 35</sql>"}]}
```
- 500–5,000 high-quality examples usually beat 50,000 noisy ones.
- **Distillation:** generate outputs with a frontier model, **filter by a verifier** (execute the SQL, run the tests), and train on the survivors (rejection sampling).
- Use exactly the system prompt / format you'll use at inference.
- Dedupe, and remove any overlap with the eval set (**contamination** makes every result meaningless).

### Run
```bash
python -m training.train sft --model Qwen/Qwen2.5-1.5B-Instruct --data sft.jsonl
```
Key settings in `train.py` and why:
| Setting | Value | Why |
|---|---|---|
| `r`, `lora_alpha` | 16, 32 | enough capacity for most tasks; raise r if underfitting |
| `target_modules` | `all-linear` | attention-only LoRA often underfits |
| `learning_rate` | 2e-4 | LoRA needs ~10× the full fine-tune LR |
| `num_train_epochs` | 1–3 | more = memorisation; watch eval loss |
| `assistant_only_loss` | True | don't train the model to write prompts |
| `max_length` | ≥ your longest example | silent truncation cuts off exactly the answers |

---

## 3. DPO

Data: `{"prompt": [...], "chosen": [...], "rejected": [...]}`. Good pairs differ in **the property you care about** (correctness, tone, refusing properly), not in random ways.

Sources of pairs: human preferences; two model samples ranked by a verifier or a calibrated judge; the model's own failures (rejected) vs corrected versions (chosen).

```bash
python -m training.train dpo --model ./out/sft-merged --data prefs.jsonl
```
Watch in the logs: `rewards/accuracies` (should rise toward 0.7–0.9), `rewards/margins` (rising), `rewards/chosen` (should **not** fall steadily; if both chosen and rejected fall, the model is just lowering the likelihood of everything). `beta` 0.1 is the default; lower = more drift from the SFT model.

---

## 4. GRPO with verifiable rewards

### The reward is the product. Write it like production code ([rewards.py](../code/training/rewards.py))
```python
def execution_reward(prompts, completions, gold_sql, db_path, **kwargs) -> list[float]:
    # extract the LAST <sql> block; execute read-only with a timeout;
    # compare result sets (order-insensitive unless gold has ORDER BY) -> 1.0 / 0.0
```
Tested behaviours (see `test_execution_reward`):
- **different SQL with the same result gets credit** (compare results, not strings)
- wrong format → 0; right answer inside the wrong format → 0 (the format reward handles shaping)
- **writes are blocked** (regex plus a read-only connection), so the policy can't "win" by changing the grader's database
- runaway queries **time out** (a progress handler), so one bad sample can't stall the batch
- conversational completions (lists of message dicts) are handled; missing this gives all-zero rewards

Keep shaping rewards **small** (format = 0.1 vs correctness = 1.0), or the policy optimises the format.

### Config highlights (`train.py`)
| Setting | Value | Why |
|---|---|---|
| `num_generations` | 8 | group size G: the baseline is the group mean |
| `loss_type` | `"dapo"` | token-level normalisation; `"dr_grpo"` removes length bias; `"grpo"` is the original |
| `epsilon`, `epsilon_high` | 0.2, 0.28 | DAPO clip-higher: keeps exploration, prevents entropy collapse |
| `beta` | 0.0 | no KL term (DAPO/Dr.GRPO practice); add 0.01–0.04 if outputs degrade |
| `importance_sampling_level` | `"sequence"` for GSPO | steadier, especially for MoE models |
| `temperature` | 1.0 | samples in a group must differ, or every advantage is 0 |
| `use_vllm` | True | generation dominates GRPO time; vLLM makes rollouts several times faster |

### Data difficulty matters
If the model already solves a prompt 8/8 times, or 0/8, that group has **zero variance → zero gradient**. Before training, sample 8 completions per prompt with the SFT model and keep prompts with a pass rate between roughly 10% and 90%. This is dynamic sampling done offline, and it's often the biggest win.

---

## 5. Common errors

| Symptom | Cause | Fix |
|---|---|---|
| Eval score great, real use poor | train/eval contamination; eval too similar to train | dedupe across splits; held-out eval from a different source |
| SFT model repeats the prompt or rambles | loss on prompt tokens; missing EOS; chat template mismatch | assistant-only loss; the same chat template at train and inference |
| Model forgets general abilities | too many epochs, LR too high, narrow data | fewer epochs; lower LR; mix in some general data; LoRA instead of full FT |
| GRPO reward flat at 0 | model never produces the expected format; reward function bug (e.g. wrong completion type) | SFT first; unit-test rewards; log 5 samples + rewards every N steps |
| GRPO reward flat at 1 | prompts too easy | filter to prompts with 10–90% pass rate |
| Reward rises, eval falls | **reward hacking** (exploiting the verifier) | read samples; harden the verifier (the write-blocking and timeouts above); held-out eval with a different checker |
| Completions get longer and longer | length bias; no overlong penalty | `loss_type="dr_grpo"` or `"dapo"`; `max_completion_length`; overlong shaping |
| Entropy collapses, all samples identical | clipping too tight; temperature too low | `epsilon_high`; temperature 1.0; watch the entropy metric |
| OOM | long completions × group size | smaller `num_generations`/batch; gradient checkpointing; LoRA; vLLM colocate memory fraction |
| DPO "chosen" reward falls | known DPO failure (likelihood of both responses drops) | lower LR; higher beta; add an SFT loss term; check pair quality |

---

## 6. How to improve
1. **Data quality > quantity > hyperparameters.** Filter with verifiers; read 50 random training examples.
2. Distil from the strongest model you can use, filtered by correctness.
3. Curriculum: filter prompts by difficulty for GRPO.
4. Harden the reward: add checks for every hack you find in samples.
5. Compare against the baseline on **cost per correct answer**, not just accuracy.
6. Merge LoRA into the base for serving (`model.merge_and_unload()`), or serve adapters with vLLM multi-LoRA.

## 7. Exercises
1. `pytest tests/test_other.py -k reward -v`; then add a reward-hacking case (e.g. `SELECT * FROM users` when gold returns all rows) and decide whether it deserves credit.
2. Build a 300-example text-to-SQL SFT set by distillation + execution filtering on a small SQLite DB; LoRA-tune a 1.5B model on Colab; compare it with the frontier model on 50 held-out questions.
3. Run 200 GRPO steps on top; plot mean reward, completion length and entropy; read 10 samples at steps 0, 100 and 200.
