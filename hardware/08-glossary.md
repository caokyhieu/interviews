# Glossary

Terms in the order you'll likely meet them. The chapter number shows where each is explained in full.

## Basics (ch. 1)
| Term | Meaning |
|---|---|
| **Bit** | a single 1 or 0 |
| **Transistor / MOSFET** | an electrically-controlled switch; the building block of every chip |
| **Semiconductor** | a material (usually silicon) whose conductivity can be controlled — what makes transistors possible |
| **Logic gate** | a few transistors implementing a rule like AND, OR, NOT |
| **MAC** | multiply-accumulate, `a × b + c` — the core operation of AI |
| **Clock / GHz** | the chip's heartbeat; 1 GHz = 1 billion ticks per second |
| **Die** | one piece of silicon cut from a wafer |
| **Moore's law** | transistor count roughly doubles every two years |
| **Dennard scaling** | shrinking transistors used to keep power density constant; ended ~2006 |

## Manufacturing (ch. 2)
| Term | Meaning |
|---|---|
| **Wafer** | 300 mm silicon disc on which hundreds of chips are made at once |
| **Fabless / foundry / IDM** | designs only / manufactures for others / does both |
| **Photolithography** | printing circuit patterns with light through a mask |
| **DUV / EUV** | 193 nm / 13.5 nm lithography light; EUV only from ASML |
| **Multipatterning (SAQP)** | printing a dense layer in several exposures to beat DUV's limits |
| **Process node (7nm, 5nm, N+2, N+3)** | a marketing label for a manufacturing generation; compare density instead |
| **Yield** | fraction of chips on a wafer that work; ≈ e^(−defect density × area) |
| **Reticle limit** | largest area one exposure can print, ~858 mm² |
| **SMIC** | China's leading foundry; makes Huawei's advanced chips with DUV |
| **Entity List / export controls** | US restrictions cutting Huawei off from TSMC, EUV tools and HBM |

## CPUs (ch. 3)
| Term | Meaning |
|---|---|
| **ISA** | the instruction vocabulary a CPU understands (x86, Arm, RISC-V) |
| **Architecture licence** | right to design your own cores for Arm's ISA (Huawei has one for Armv8) |
| **Pipelining / superscalar / out-of-order** | techniques to keep a core busy |
| **Branch prediction** | guessing the outcome of "if" statements to avoid waiting |
| **SIMD** | one instruction applied to many numbers at once |
| **Cache (L1/L2/L3)** | small fast on-chip memory holding recently-used data |
| **Memory wall** | processors outpacing memory speed |
| **Latency vs bandwidth** | time for one request vs bytes per second |
| **SMT / threads** | one core running 2 instruction streams; "192 cores / 384 threads" |
| **NUMA** | memory attached to a different socket or chiplet is slower to reach |
| **Confidential computing** | hardware-encrypted enclaves protecting data while it's processed (Kunpeng 950) |
| **Kunpeng / TaiShan** | Huawei's Arm server CPUs / the servers and cores built around them |

## AI chips (ch. 4)
| Term | Meaning |
|---|---|
| **FLOP / FLOPS** | one floating-point operation / operations per second |
| **TFLOPS, PFLOPS, EFLOPS, ZFLOPS** | 10¹², 10¹⁵, 10¹⁸, 10²¹ FLOPS |
| **FP32, BF16, FP8, FP4** | number formats by bit width; fewer bits = more speed, less precision |
| **MX formats (MXFP8, MXFP4)** | block-scaled formats: a group of values shares one scale factor |
| **HiF8 / HiF4** | Huawei's own tapered-precision 8- and 4-bit formats |
| **GPU / SIMT** | many flexible threads executing in groups (warps) |
| **NPU / TPU** | chip built around a large matrix engine |
| **Systolic array** | grid of MACs through which data pulses, reusing each value many times |
| **Tensor core** | Nvidia's matrix-multiply unit inside a GPU |
| **Da Vinci core** | Huawei's AI core: Cube + Vector + Scalar units |
| **Cube unit** | Da Vinci's matrix engine (16×16×16 per cycle at FP16) |
| **Arithmetic intensity** | FLOPs per byte of memory traffic |
| **Roofline / ridge point** | peak FLOPS ÷ bandwidth; below it you're memory-bound |
| **Compute-bound / memory-bound** | limited by math units / by memory bandwidth |
| **Prefill / decode** | reading the prompt (compute-bound) / generating tokens one by one (memory-bound) |
| **KV cache** | stored attention state for previous tokens; grows with context length |
| **950PR / 950DT** | Ascend variant for Prefill & Recommendation / Decode & Training |
| **Dense vs sparse FLOPS** | sparse numbers assume zeros are skipped — usually 2× inflated |

## Memory & packaging (ch. 5)
| Term | Meaning |
|---|---|
| **SRAM / DRAM** | fast on-chip memory / dense cheap main memory |
| **DDR5, LPDDR5X, GDDR7** | conventional memory types |
| **HBM (HBM3E, HBM4)** | stacked DRAM beside the compute die, 1,024–2,048-bit wide |
| **TSV** | through-silicon via — vertical wire through a stacked die |
| **HiBL 1.0 / HiZQ 2.0** | Huawei's low-cost high-capacity HBM / high-bandwidth HBM (144 GB, 4 TB/s) |
| **Interposer** | silicon slab carrying dense wiring between dies in a package |
| **2.5D / 3D packaging** | dies side-by-side on an interposer / dies stacked on each other |
| **CoWoS** | TSMC's 2.5D packaging technology |
| **Chiplet** | one of several smaller dies combined in a package |
| **UCIe** | industry standard for chiplet-to-chiplet links |

## Interconnect & systems (ch. 6)
| Term | Meaning |
|---|---|
| **Data / tensor / pipeline / expert parallelism** | ways to split AI work across chips |
| **MoE** | Mixture-of-Experts: model where each token uses only some "expert" sub-networks |
| **All-reduce / all-to-all** | collective communication patterns |
| **MFU** | Model FLOPs Utilization — fraction of peak compute doing useful work |
| **Scale-up / scale-out** | fast memory-semantic network making chips act as one / slower network linking those groups |
| **Memory semantics** | directly reading/writing another chip's memory |
| **RDMA / RoCE / InfiniBand** | fast network data transfer technologies for scale-out |
| **NVLink** | Nvidia's scale-up interconnect |
| **UnifiedBus (UB) / UBoE** | Huawei's single peer-to-peer scale-up protocol / UB over Ethernet |
| **SerDes** | circuits that send high-speed serial signals between chips |
| **Pluggable / LPO / NPO / CPO** | optical options from farthest to closest to the chip |
| **Hi-ONE** | Huawei's near-packaged optical engine (7.2 Tb/s, built-in light source) |
| **SuperPoD / supernode** | a very large scale-up domain acting as one computer |
| **SuperCluster** | many SuperPoDs joined by a scale-out network |
| **CloudMatrix 384 / Atlas 900 A3** | Huawei's 384-NPU SuperPoD (2025) |
| **NVL72 / NVL144** | Nvidia rack with 72 GPU packages / named by 144 dies |
| **Clos / fat tree** | multi-layer switch network where every node reaches every other in equal hops |
| **Plane / rail** | independent parallel copies of a network for bandwidth and resilience |
| **UB-Mesh** | Huawei's hierarchical full-mesh topology design |

## Software (ch. 7)
| Term | Meaning |
|---|---|
| **CUDA** | Nvidia's GPU programming platform — its deepest moat |
| **CANN** | Huawei's equivalent: compiler, operators, runtime for Ascend |
| **Ascend C** | CANN's kernel programming language |
| **HCCL / NCCL** | Huawei's / Nvidia's collective-communication libraries |
| **MindSpore** | Huawei's AI framework |
| **torch_npu** | adapter to run PyTorch on Ascend |
| **openEuler** | Huawei-originated Linux distribution |

## Competitors (ch. 9)
| Term | Meaning |
|---|---|
| **Vera Rubin / NVL72** | Nvidia's 2026 GPU / its 72-GPU copper-linked rack |
| **Groq 3 LPX** | Nvidia rack of 256 SRAM-based Groq LPUs for fast decode |
| **Vera CPU rack** | Nvidia rack of 256 Arm CPUs for RL environments and agent sandboxes |
| **BlueField-4 STX** | Nvidia storage rack for KV / context memory |
| **Ironwood (TPU v7)** | Google's 2025 TPU; 9,216-chip pods |
| **OCS** | optical circuit switch — steers light with tiny mirrors; used in Google TPU pods |
| **ICI** | Google's inter-chip interconnect |
| **Trainium3 / UltraServer** | AWS's 2025 AI chip / its 144-chip system |
| **MI455X / Helios** | AMD's 2026 GPU / its 72-GPU rack |
| **UALink** | open industry scale-up interconnect standard (AMD and others) |
| **Merchant vs in-house silicon** | sold to anyone (Nvidia, AMD, Huawei) vs built for one cloud (TPU, Trainium) |

## Inference and RL (ch. 10)
| Term | Meaning |
|---|---|
| **TTFT** | time to first token — set by prefill |
| **TPOT** | time per output token — set by decode; 1000 ÷ TPOT(ms) = tokens/s per user |
| **Interactivity vs throughput** | per-user speed vs tokens per second per chip; batching trades one for the other |
| **Disaggregated serving** | running prefill and decode on separate pools of hardware |
| **Expert parallelism (EP320)** | spreading MoE experts over chips; EP320 = 320 chips |
| **Speculative decoding** | a small model drafts tokens, the big model checks several at once |
| **Dynamo** | Nvidia's open-source distributed inference framework |
| **vLLM / SGLang / TensorRT-LLM** | LLM serving engines |
| **CloudMatrix-Infer** | Huawei's serving system for CloudMatrix 384 |
| **UCM** | Huawei's open-source Unified Cache Manager for KV cache |
| **Post-training** | everything after pre-training: SFT, then RL |
| **SFT** | supervised fine-tuning on example answers |
| **PPO / GRPO** | RL algorithms; GRPO was used for DeepSeek-R1 |
| **Rollout** | the policy generating answers during RL — inference |
| **Reward model / verifier** | scores rollouts, by a model or by checks such as unit tests |
| **Environment / sandbox** | isolated place where an agent's code and tool calls run during RL |
| **Long tail (stragglers)** | a few very long generations holding up a synchronous RL step |
| **Async RL** | training on finished rollouts while others are still generating |
| **Weight sync / resharding** | copying new weights to rollout engines / converting between training and inference layouts |
| **Co-located vs disaggregated RL** | same chips switch roles vs separate training and rollout clusters |
| **Training–inference mismatch** | rollout and training engines computing slightly different probabilities, making RL off-policy |
| **MindSpeed-RL** | Huawei's official RL training framework for Ascend |
| **verl / NeMo RL / OpenRLHF** | widely-used RL post-training frameworks |
