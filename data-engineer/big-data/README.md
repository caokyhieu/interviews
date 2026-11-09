# Big Data Stack Study Track

**Hadoop · Hive · Kafka · Spark · Flink · Iceberg · Arrow/DataFusion · Kubernetes · Celeborn** — prepared September 2026, version-current as of Hadoop 3.5, Hive 4.1, Kafka 4.3, Spark 4.1/4.2, Flink 2.2, Iceberg v3, Celeborn 0.7.

Diagrams are Mermaid. They render in GitHub, in VS Code's built-in Markdown preview (`⇧⌘V`), and in most Markdown viewers. If a diagram doesn't render, install the *Markdown Preview Mermaid Support* extension.

## Files

| File | Contents |
|---|---|
| **[00-the-big-picture.md](00-the-big-picture.md)** | **Start and finish here.** How all ten chapters connect: the master architecture, the six layers and their contracts, five physical facts that generate the whole design, the life of one event end-to-end, the life of one query, the causality map (change one thing, six things move), a day in the life of the platform, one failure traced through every layer |
| [01-hadoop.md](01-hadoop.md) | HDFS internals (write/read paths, NameNode memory math, rack awareness, HA, erasure coding), YARN, MapReduce and its shuffle, file formats and Parquet internals |
| [02-hive.md](02-hive.md) | Metastore, Tez/LLAP/vectorization, partitioning vs bucketing, join strategies, ACID deltas + compaction, and why Iceberg superseded Hive tables |
| [03-kafka.md](03-kafka.md) | Log storage and why it's fast, ISR/high-watermark/durability dial, KRaft, producer & consumer internals, rebalancing old vs new, EOS, share groups, tiered storage, ops |
| [04-spark.md](04-spark.md) | Driver/executor/stage model, shuffle mechanism, Catalyst + Tungsten + AQE, five join strategies, skew and salting, memory model, Structured Streaming, Spark 4.x |
| [05-flink.md](05-flink.md) | Slots and chaining, event time and watermarks, state types/key groups/ForSt, checkpoint barriers and 2PC, windows, Flink SQL changelogs, backpressure |
| [06-comparison-and-qa.md](06-comparison-and-qa.md) | How the stack evolved and why, the reference architecture, Spark vs Flink, delivery semantics, Lambda/Kappa/lakehouse, a fully worked design answer, ~45 rapid-fire Q&As |
| [07-iceberg.md](07-iceberg.md) | The metadata tree, the atomic commit protocol, hidden partitioning and evolution, CoW vs MoR and delete files, v3 (deletion vectors, row lineage, VARIANT), catalogs, **maintenance**, vs Delta/Hudi/Paimon |
| [08-datafusion.md](08-datafusion.md) | Arrow's columnar memory format and zero-copy, DataFusion's planner and streaming partitioned execution, extension APIs, Comet as a Spark accelerator, single-node vs distributed, the composable data stack |
| [09-kubernetes.md](09-kubernetes.md) | Declarative reconciliation, pods/StatefulSets/operators, requests vs limits and OOMKilled, gang scheduling with YuniKorn/Volcano, Karpenter, Spark/Flink/Kafka on K8s, **why dynamic allocation stalls without an external shuffle service** |
| [10-celeborn.md](10-celeborn.md) | The shuffle problem on elastic/spot clusters, Master/Worker/LifecycleManager, push-based shuffle and partition aggregation, replication and partition split, tiered storage, deployment on K8s, vs Magnet and Uniffle |

## Suggested order

```mermaid
flowchart LR
    BP0["00 Big picture<br/>read for ORIENTATION"] --> H["01 Hadoop<br/>the vocabulary:<br/>blocks, locality, shuffle,<br/>containers, formats"] --> HV["02 Hive<br/>tables, partitions,<br/>metastore, ACID"]
    HV --> IC["07 Iceberg<br/>the direct answer to<br/>everything Hive tables<br/>got wrong"]
    IC --> K["03 Kafka<br/>the substrate<br/>everything else<br/>reads from"]
    K --> F["05 Flink<br/>streaming concepts<br/>at their cleanest"]
    F --> S["04 Spark<br/>mostly familiar;<br/>focus on streaming,<br/>AQE, skew, 4.x"]
    S --> DF["08 Arrow / DataFusion<br/>where engines are going;<br/>the 'do you even need<br/>a cluster' argument"]
    DF --> KU["09 Kubernetes<br/>where all of this<br/>actually runs now"]
    KU --> CE["10 Celeborn<br/>fixing shuffle for<br/>elastic clusters"]
    CE --> C["06 Comparison + Q&A<br/>re-read the worked<br/>design answer until<br/>the structure is automatic"]
    C --> BP1["00 Big picture AGAIN<br/>now as SYNTHESIS —<br/>the causality map and<br/>the self-test questions"]
```

**Read [00](00-the-big-picture.md) twice**: once at the start so you know where each system sits, and once at the end, where its causality map and cross-chapter self-test turn the pieces into one system.

Read **07 right after 02** — Iceberg only makes sense as an answer to Hive's specific failures. Read **05 before 04's streaming chapter**; event time, watermarks, state and checkpoints are cleanest in Flink and transfer directly. Read **09 and 10 as a pair, after 04** — chapter 9 ends on the problem that chapter 10 solves.

## The twenty-three things to be able to say cold

**Storage & tables**
1. ~150 bytes of NameNode heap per file/block object — that's *why* the small-files problem exists, and the lesson generalizes to every system here.
2. Rack-aware placement: local, remote rack, same remote rack — one cross-rack hop buys rack tolerance, a second would waste bandwidth.
3. S3 has no atomic rename, which broke Hadoop's commit protocol, which is why Iceberg commits by swapping a metadata pointer.
4. Partition by a low-cardinality column for pruning; bucket by a high-cardinality key for shuffle-free joins. Partitioning on high cardinality is the classic disaster.
5. Parquet pruning has three levels — partition, row group (min/max, **only useful if data is sorted**), column.

**Iceberg**
6. A Hive table is a directory; an Iceberg table is a metadata tree with an atomically swapped root pointer. Everything else follows.
7. Planning reads manifests instead of listing S3 — and manifest stats prune files before any data is read.
8. Hidden partitioning means the table knows `dt = days(ts)`, so filtering on `ts` prunes automatically. No sync column, no accidental full scans.
9. CoW = slow writes, fast reads (batch). MoR = fast writes, degrading reads (streaming/CDC) — and **requires compaction**.
10. Compaction without `expire_snapshots` frees nothing; old snapshots still reference the old files.

**Kafka**
11. Ordering is per-partition, never per-topic; partition count is the parallelism ceiling.
12. `acks=all` + `min.insync.replicas=2` + `RF=3` — and why `acks=all` alone is not enough.
13. Kafka 4.x is KRaft-only; KIP-848 killed stop-the-world rebalances; share groups add queue semantics.

**Processing**
14. Exactly-once = exactly-once *effect on state*. It reaches the outside world only through an idempotent or transactional sink.
15. A watermark is a latency-vs-completeness dial, and an operator's watermark is the **minimum across its inputs** — one idle partition stalls everything.
16. Flink 2.0's disaggregated state (ForSt) makes state size unbounded and recovery time independent of state size.
17. Savepoints + stable `uid()`s are how you upgrade a stateful Flink job; `maxParallelism` can never change.
18. Spark stages are cut at shuffle boundaries; skew is diagnosed by max-vs-median task time; fixes are AQE skew join, broadcast, salting.

**Engines & direction**
19. Arrow is the in-memory standard, Parquet the on-disk one; "zero-copy" means the wire format *is* the memory format. Native vectorized execution under an existing SQL front end (Comet, Photon, Velox) is the defining engine trend of the 2020s.
20. Ask how much data the query *actually touches after pruning* — it usually fits on one machine, and a cluster buys elastic scale and fault tolerance at the cost of a shuffle and an ops burden.

**Deployment & shuffle**
21. Kubernetes is declarative reconciliation: you state desired state, controllers converge to it. An operator is that loop plus a CRD, encoding one system's operational knowledge.
22. Kubernetes lacks YARN's gang scheduling and hierarchical queues — add YuniKorn or Volcano, or two big Spark jobs can deadlock holding half their executors each.
23. Kubernetes has no external shuffle service, so Spark keeps idle executors alive via shuffle tracking, and a lost spot node forces a whole stage to recompute. Celeborn moves shuffle to a replicated external service, which lets you set `shuffleTracking.enabled=false` and makes compute disposable.

## Sources

- [HDFS Architecture](https://hadoop.apache.org/docs/stable/hadoop-project-dist/hadoop-hdfs/HdfsDesign.html) · [HDFS Erasure Coding (3.5.0)](https://hadoop.apache.org/docs/current3/hadoop-project-dist/hadoop-hdfs/HDFSErasureCoding.html)
- [Hive 4.0 major changes](https://hive.apache.org/docs/latest/overview-of-major-changes/) · [ASF Hive 4.0 announcement](https://news.apache.org/foundation/entry/apache-software-foundation-announces-apache-hive-4-0) · [Iceberg–Hive integration](https://iceberg.apache.org/docs/latest/hive/)
- [Kafka 4.0 release](https://www.confluent.io/blog/latest-apache-kafka-release/) · [Kafka 4.2.0](https://kafka.apache.org/blog/2026/02/17/apache-kafka-4.2.0-release-announcement/) · [Share consumer GA](https://www.confluent.io/blog/kafka-queue-semantics-share-consumer-ga/) · [Kafka 4.3.0](https://factorhouse.io/articles/apache-kafka-4-3-0/)
- [Introducing Apache Spark 4.0](https://www.databricks.com/blog/introducing-apache-spark-40) · [Spark 4.1.0 release](https://spark.apache.org/releases/spark-release-4.1.0.html)
- [Flink 2.0.0](https://flink.apache.org/2025/03/24/apache-flink-2.0.0-a-new-era-of-real-time-data-processing/) · [Disaggregated State (VLDB)](https://www.vldb.org/pvldb/vol18/p4846-mei.pdf) · [Flink 2.1.0](https://flink.apache.org/2025/07/31/apache-flink-2.1.0-ushers-in-a-new-era-of-unified-real-time-data--ai-with-comprehensive-upgrades/) · [Flink 2.2.0](https://flink.apache.org/2025/12/04/apache-flink-2.2.0-advancing-real-time-data--ai-and-empowering-stream-processing-for-the-ai-era/)
- [Iceberg spec](https://iceberg.apache.org/spec/) · [What's new in Iceberg v3](https://opensource.googleblog.com/2025/08/whats-new-in-iceberg-v3.html) · [Iceberg v3 (Databricks)](https://www.databricks.com/blog/apache-icebergtm-v3-moving-ecosystem-towards-unification) · [Iceberg maintenance in production](https://iomete.com/resources/blog/iceberg-maintenance-production-guide)
- [Apache DataFusion docs](https://datafusion.apache.org/) · [DataFusion SIGMOD 2024 paper](https://dl.acm.org/doi/10.1145/3626246.3653368) · [DataFusion Comet](https://datafusion.apache.org/comet/user-guide/overview.html)
- [Spark on Kubernetes docs](https://spark.apache.org/docs/latest/running-on-kubernetes.html) · [Apache Spark K8s Operator](https://apache.github.io/spark-kubernetes-operator/) · [Flink Kubernetes Operator 1.16](https://flink.apache.org/2026/09/15/apache-flink-kubernetes-operator-1.16.0-release-announcement/) · [Strimzi](https://strimzi.io/) · [YuniKorn gang scheduling](https://yunikorn.apache.org/docs/user_guide/gang_scheduling/)
- [Celeborn architecture](https://celeborn.apache.org/docs/latest/developers/overview/) · [Celeborn on Kubernetes](https://celeborn.apache.org/docs/latest/deploy_on_k8s/) · [Celeborn on Amazon EMR (AWS)](https://aws.amazon.com/blogs/big-data/high-performance-remote-shuffle-service-on-amazon-emr-with-apache-celeborn/)
