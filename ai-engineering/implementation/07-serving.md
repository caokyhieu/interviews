# Implementing inference serving: vLLM / SGLang, quantization, speculative decoding, benchmarking

> Concepts: [../08-inference-and-serving.md](../08-inference-and-serving.md). Code: [../code/serving/bench.py](../code/serving/bench.py). Needs a GPU (or use llama.cpp/Ollama locally for the method, without the speedups).

---

## 1. Serve a model

```bash
pip install vllm
vllm serve Qwen/Qwen2.5-7B-Instruct \
  --max-model-len 16384 \          # only what you need: KV memory scales with it
  --gpu-memory-utilization 0.90 \  # fraction of VRAM for weights + KV cache
  --enable-prefix-caching          # reuse KV of shared prefixes (on by default in recent vLLM)
```
It's OpenAI-compatible at `http://localhost:8000/v1`. SGLang: `python -m sglang.launch_server --model-path <model>` (RadixAttention prefix caching is on by default).

**Structured output:** both support JSON-schema constrained decoding (`response_format` / `guided_json`). Use it rather than retrying on invalid JSON.

---

## 2. Benchmark properly ([bench.py](../code/serving/bench.py))

```bash
python -m serving.bench --url http://localhost:8000/v1 --model Qwen/Qwen2.5-7B-Instruct --concurrency 1 8 32
```
It reports TTFT p50/p95, TPOT p50 and total throughput per concurrency level, after a warm-up request (the first request pays for CUDA graph capture and compilation).

Rules for valid comparisons:
1. **Change one variable per run** (quantization *or* speculation *or* batch settings).
2. **Same prompts, same `max_tokens`, `temperature=0`.**
3. Report **several concurrency levels**. Most optimisations help at one end and not the other.
4. Measure **quality** too (your eval set) after quantization or any change to decoding.

---

## 3. The optimisation menu

| Technique | How | Helps | Costs / caveats |
|---|---|---|---|
| Prefix caching | `--enable-prefix-caching`; stable prompt prefixes | TTFT for repeated system prompts / agent loops | only exact prefix matches |
| FP8 quantization | `--quantization fp8` (or a pre-quantized FP8 checkpoint) | memory → more KV → more concurrency; faster decode | needs Hopper/Blackwell-class GPUs for full speed; eval quality |
| INT4 weight-only (AWQ/GPTQ) | load an AWQ/GPTQ checkpoint | fits bigger models on smaller GPUs | larger quality risk on reasoning/long context |
| KV-cache FP8 | `--kv-cache-dtype fp8` | longer contexts / more users | small quality risk |
| Speculative decoding | `--speculative-config '{"method": "eagle3", "model": "<eagle3 head>", "num_speculative_tokens": 4}'` (vLLM also lists draft-model, n-gram, suffix, MTP, DFlash and other methods) | TPOT at **low** concurrency | gains shrink at high concurrency; needs a drafter matched to the target |
| Chunked prefill | default in recent vLLM | long prompts no longer stall other users' decoding | — |
| Multi-LoRA | `--enable-lora --lora-modules name=path` | many fine-tunes on one base | adapter swapping overhead |
| Tensor parallel | `--tensor-parallel-size 2` | models that don't fit one GPU | interconnect-bound; prefer 1 GPU if it fits |

**Speculative decoding checklist:** use a drafter trained for your exact target model (EAGLE-3 heads, DFlash drafters, or the model's own MTP heads); start with 3–5 speculative tokens; measure the **acceptance rate** (vLLM logs spec-decode metrics): below ~50% it's usually not worth it; benchmark at your real concurrency.

---

## 4. Capacity planning in one formula

KV bytes per token = `2 × layers × kv_heads × head_dim × bytes_per_value`.
Example: 32 layers, 8 KV heads, head_dim 128, FP16 (2 bytes) → 2·32·8·128·2 = **131 KB per token**.
80 GB GPU with a 16 GB model at 0.9 utilisation → ~56 GB for KV → ~430k tokens in flight → e.g. 50 concurrent requests at 8k context.
This explains the benefit of FP8 KV (2× the tokens) and of GQA/MLA models (fewer KV heads).

---

## 5. Common errors

| Symptom | Cause | Fix |
|---|---|---|
| OOM at startup | `max-model-len` too large for the KV reservation; utilisation too high alongside other processes | lower `--max-model-len`; `--gpu-memory-utilization 0.85`; quantize |
| Throughput far below expectations | benchmarking at concurrency 1; no continuous batching (e.g. HF `generate` loop) | test at realistic concurrency; use vLLM/SGLang |
| TTFT spikes under load | long prompts prefilling; no chunked prefill; queueing | chunked prefill; prefix caching; separate long-context traffic; disaggregated prefill at scale |
| Speculation made things slower | low acceptance (mismatched drafter); high concurrency | matched drafter; fewer speculative tokens; disable at high load |
| Quality dropped after quantization | INT4 on a reasoning-heavy task; bad calibration data | FP8 instead; eval before rollout; a different quantized checkpoint |
| Outputs differ from the HF model | wrong chat template; different sampling defaults | pass the same template; set temperature/top_p explicitly |
| Prefix cache hit rate low | per-request data at the start of the prompt | move variable content to the end (same rule as API prompt caching) |
| First request very slow | graph capture / compilation | warm-up requests at startup; readiness probe after warm-up |

---

## 6. How to improve (order)
1. Right-size `max-model-len` and batch settings; enable prefix caching; restructure prompts for prefix reuse.
2. FP8 weights (+ FP8 KV if memory-bound), then eval quality.
3. Speculative decoding if latency at low/medium concurrency matters.
4. Route easy traffic to a smaller model (router + eval).
5. At cluster scale: prefill/decode disaggregation and KV-aware routing (NVIDIA Dynamo, llm-d, SGLang PD).

## 7. Exercises
1. Serve a 7B model, run `bench.py` at 1/8/32 concurrency. Then enable FP8 and compare throughput **and** your eval score.
2. Add a speculative config; record the acceptance rate and speedup at each concurrency level; explain the trend.
3. Compute the KV-cache capacity for your model and GPU with the formula in §4 and compare it with the number vLLM logs at startup.
