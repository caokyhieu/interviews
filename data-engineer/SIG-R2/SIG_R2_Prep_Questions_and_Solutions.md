# SIG Data Engineer — R2 Interview Prep: Questions & Solutions

Consolidated from:
- **Official SIG doc** (`Technical Phone Interview.pdf`) — CodeSignal, 60–90 min, live with a Software Engineer. Data structures, algorithms, OOP design patterns, Big O, tree/graph traversal, recursion, searching/sorting, hash tables, concurrency. **No AI/code-gen tools allowed.** Pencil and paper for tree/graph problems.
- **Third-party guide** (`...interview questions & guide 2026 (1).pdf`) — Python internals, Pandas internals, data engineering architecture, SQL, plus a "most likely to come up" table (SQL + pipelines + behavioral).
- Your existing prep files (`R2_CONCEPT.md`, `r2_exercises.py`, `r2_exercises_part2.py`) — kept as-is for self-testing; this doc is the answer key + the extra categories those files don't cover (Pandas, architecture, SQL, behavioral).

**How to use this:** try the coding exercises in the `.py` files cold first (that's what they're for), *then* check yourself here. For everything else, read the answers, then say them out loud once — this round rewards spoken fluency, not just correctness.

---

## Table of Contents
1. [Live Coding — Predict-the-Output Gotchas](#1-live-coding--predict-the-output-gotchas)
2. [Live Coding — Core Algorithms](#2-live-coding--core-algorithms)
3. [Live Coding — Classes & the Data Model](#3-live-coding--classes--the-data-model)
4. [Live Coding — Trees & Graphs](#4-live-coding--trees--graphs)
5. [Live Coding — Sorting](#5-live-coding--sorting)
6. [Python & Core Programming (conceptual)](#6-python--core-programming-conceptual)
7. [Pandas Internals](#7-pandas-internals)
8. [Data Engineering Architecture](#8-data-engineering-architecture)
9. [SQL Question Bank](#9-sql-question-bank)
10. [Pipeline Troubleshooting Scenarios](#10-pipeline-troubleshooting-scenarios)
11. [Behavioral & Leadership](#11-behavioral--leadership)

---

## 1. Live Coding — Predict-the-Output Gotchas

| # | Snippet | Answer | Why |
|---|---|---|---|
| 1.1 | Mutable default arg, `append_to(1)` then `append_to(2)` | `a=[1,2] b=[1,2]` (same list) | Default evaluated once at def time, shared across calls |
| 1.2 | `[lambda: i for i in range(3)]` called | `[2, 2, 2]` | Closures capture the variable, not its value — late binding |
| 1.3 | `x=[1,2]; y=[1,2]; x==y, x is y` | `True False` | `==` compares value, `is` compares identity |
| 1.4 | `m=[[0]*3]*3; m[0][0]=9` | `[[9,0,0],[9,0,0],[9,0,0]]` | All 3 rows are the *same* list object |
| 1.5 | `t=([1,2],3); t[0].append(99)` | `([1, 2, 99], 3)` | Tuple immutability is shallow — it fixes which objects it holds, not their contents |
| 1.6 | `-7 // 2, -7 % 2` | `-4, 1` | Python floor-divides (rounds toward −∞); modulo always has the sign of the divisor |
| 1.7 | `3 > 2 > 1, (3 > 2) > 1` | `True, False` | Chained comparison is `3>2 and 2>1`; explicit form is `True > 1` → `1 > 1` → `False` |
| 1.8 | `d={"b":1,"a":2}; d["c"]=3; list(d)` | `['b', 'a', 'c']` | Dicts (3.7+) preserve insertion order |

---

## 2. Live Coding — Core Algorithms

For every solution below: **state time/space complexity out loud, unprompted.** That's the single highest-leverage habit for this round.

```python
def reverse_words(s: str) -> str:
    # Manual version first (no split) — interviewers may explicitly ask for this
    words, word = [], []
    for ch in s:
        if ch == ' ':
            if word:
                words.append(''.join(word))
                word = []
        else:
            word.append(ch)
    if word:
        words.append(''.join(word))
    return ' '.join(reversed(words))
    # One-liner once you've shown the manual version: ' '.join(s.split()[::-1])
# O(n) time, O(n) space


def first_non_repeating(s: str) -> str | None:
    counts = {}
    for ch in s:
        counts[ch] = counts.get(ch, 0) + 1
    for ch in s:                     # second pass preserves original order
        if counts[ch] == 1:
            return ch
    return None
# O(n) time (two passes, still linear), O(k) space, k = distinct chars
# Why not nested loops: for each char, scanning the rest is O(n) -> O(n^2) total


def two_sum(nums: list[int], target: int) -> tuple[int, int] | None:
    seen = {}                        # value -> index
    for i, n in enumerate(nums):
        complement = target - n
        if complement in seen:
            return (seen[complement], i)
        seen[n] = i
    return None
# O(n) time, O(n) space. One pass suffices because by the time we reach index i,
# every earlier value is already in the dict — we only need to check "have I seen
# the number that completes me?", not "do I pair with someone ahead of me?"


def binary_search(sorted_nums: list[int], target: int) -> int:
    lo, hi = 0, len(sorted_nums) - 1
    while lo <= hi:                  # <=, not <, else you miss the single-element window
        mid = (lo + hi) // 2
        if sorted_nums[mid] == target:
            return mid
        elif sorted_nums[mid] < target:
            lo = mid + 1              # not just `mid` — infinite loop otherwise
        else:
            hi = mid - 1
    return -1
# O(log n) time, O(1) space


def merge_sorted(a: list[int], b: list[int]) -> list[int]:
    i = j = 0
    result = []
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            result.append(a[i]); i += 1
        else:
            result.append(b[j]); j += 1
    result.extend(a[i:])
    result.extend(b[j:])
    return result
# O(n+m) time, O(n+m) space — this IS the merge step of mergesort


def dedupe_keep_order(items: list) -> list:
    seen = set()
    out = []
    for it in items:
        if it not in seen:
            seen.add(it)
            out.append(it)
    return out
# O(n) time, O(n) space. set() alone doesn't work because sets are unordered —
# you'd lose "first-seen" order. Items must be hashable (immutable) to go in the set.


def char_count(s: str) -> dict:
    counts = {}
    for ch in s:
        counts[ch] = counts.get(ch, 0) + 1
    return counts
# Ladder to mention: plain dict + if/else -> dict.get(c,0)+1 -> collections.Counter(s)
# O(n) time, O(k) space


def is_anagram(s1: str, s2: str) -> bool:
    if len(s1) != len(s2):
        return False
    return char_count(s1) == char_count(s2)
# O(n) time via counting. Alternative: sorted(s1) == sorted(s2), O(n log n) —
# simpler to write, worse complexity; mention the trade-off unprompted.


def fibonacci(n: int) -> int:
    a, b = 0, 1
    for _ in range(n):
        a, b = b, a + b
    return a
# O(n) time, O(1) space. Naive recursion is O(2^n) — the call tree branches in two
# at every level, most of it recomputing the same subproblems. Fix: memoize
# (functools.lru_cache) turns it into O(n) by caching each unique call.


def flatten(nested: list) -> list:
    out = []
    for item in nested:
        if isinstance(item, list):
            out.extend(flatten(item))
        else:
            out.append(item)
    return out
# O(n) time where n = total element count, O(d) extra stack space, d = max nesting depth
# Explicit-stack version avoids Python's ~1000 default recursion limit on deep nesting:
def flatten_iterative(nested: list) -> list:
    out, stack = [], list(reversed(nested))
    while stack:
        item = stack.pop()
        if isinstance(item, list):
            stack.extend(reversed(item))
        else:
            out.append(item)
    return out


def moving_average(nums: list[float], window: int) -> list[float]:
    if window <= 0 or window > len(nums):
        return []
    running_sum = sum(nums[:window])
    result = [running_sum / window]
    for i in range(window, len(nums)):
        running_sum += nums[i] - nums[i - window]   # slide: add new, drop oldest
        result.append(running_sum / window)
    return result
# O(n) time via running sum, not O(n*window) recomputing each window from scratch
```

---

## 3. Live Coding — Classes & the Data Model

```python
class Trade:
    def __init__(self, symbol, quantity, price):
        self.symbol = symbol
        self.quantity = quantity
        self.price = price

    @property
    def notional(self):
        return self.quantity * self.price

    def __repr__(self):
        return f"Trade({self.symbol!r}, {self.quantity}, {self.price})"

    def __eq__(self, other):
        if not isinstance(other, Trade):
            return NotImplemented
        return (self.symbol, self.quantity, self.price) == \
               (other.symbol, other.quantity, other.price)

    def __hash__(self):
        return hash((self.symbol, self.quantity, self.price))
    # Contract: a == b implies hash(a) == hash(b). Define __eq__ without __hash__
    # and Python sets __hash__ to None -> instances become unhashable, can't
    # live in a set/dict. Fix: hash the same fields __eq__ compares, and only
    # hash immutable state.


class Portfolio:
    def __init__(self):
        self._trades = []

    def add(self, trade):
        self._trades.append(trade)

    def __len__(self):
        return len(self._trades)

    def __iter__(self):
        yield from self._trades

    def total_notional(self):
        return sum(t.notional for t in self._trades)

    def __contains__(self, symbol: str) -> bool:
        return any(t.symbol == symbol for t in self._trades)
    # Dunder methods are how a custom object plugs into Python's built-in syntax
    # (len(), for x in, x in obj) — that IS "the data model."
```

**Conceptual follow-ups to have ready (one sentence each):**
- Instance method takes `self`, acts on one object. `@classmethod` takes `cls` — alternative constructors (`Trade.from_csv_row()`). `@staticmethod` takes neither — just a namespaced function.
- `@dataclass` auto-generates `__init__`, `__repr__`, `__eq__` from field declarations; `order=True` adds ordering, `frozen=True` adds immutability + hashing. Use it for data-carrying classes; hand-write dunders only when you need custom behavior.
- `__init__` vs `__new__`: `__new__` allocates and returns the instance (rarely overridden — singletons, subclassing immutables); `__init__` initializes the already-created instance, returns `None`.
- `super()` calls the next class in MRO, not simply "the parent" — matters for multiple inheritance / diamond hierarchies (`ClassName.__mro__`).
- When *not* to use a class: no state to bundle with behavior → a function or module is simpler. A class with only `__init__` and one method is usually a function in disguise.

---

## 4. Live Coding — Trees & Graphs

**Draw the structure on paper before coding — the official doc explicitly calls this out as what separates strong candidates.**

```python
from collections import deque

class Node:
    def __init__(self, val, left=None, right=None):
        self.val, self.left, self.right = val, left, right


def dfs_inorder(root) -> list:
    if root is None:
        return []
    return dfs_inorder(root.left) + [root.val] + dfs_inorder(root.right)
# Left, node, right. On a BST this returns SORTED order — because every left
# subtree is entirely < node < entirely right subtree, recursively.
# O(n) time, O(h) space for the call stack (h = height).
# preorder = node, L, R.  postorder = L, R, node.


def bfs_level_order(root) -> list:
    if root is None:
        return []
    q, out = deque([root]), []
    while q:
        node = q.popleft()
        out.append(node.val)
        if node.left:  q.append(node.left)
        if node.right: q.append(node.right)
    return out
# DFS = stack (or recursion). BFS = queue. Say this every time — it's the
# single most-tested distinction. O(n) time, O(n) space (widest level).


def tree_height(root) -> int:
    if root is None:
        return 0
    return 1 + max(tree_height(root.left), tree_height(root.right))
# O(n) time, O(h) space


def bst_contains(root, target) -> bool:
    node = root
    while node:
        if node.val == target:
            return True
        node = node.left if target < node.val else node.right
    return False
# O(h) — O(log n) balanced, O(n) degenerate. "Binary search wearing a tree costume."


def dfs_iterative(root) -> list:
    if root is None:
        return []
    stack, out = [root], []
    while stack:
        node = stack.pop()
        out.append(node.val)
        if node.right: stack.append(node.right)   # push right first
        if node.left:  stack.append(node.left)     # so left pops first
    return out
# Preorder with an explicit stack — proves recursion IS a stack under the hood,
# and sidesteps Python's ~1000 default recursion depth limit.


# --- Graphs: adjacency list = dict of node -> list of neighbors ---

def graph_bfs(graph: dict, start: str) -> list:
    visited = {start}
    q, out = deque([start]), []
    while q:
        node = q.popleft()
        out.append(node)
        for nb in graph[node]:
            if nb not in visited:
                visited.add(nb)
                q.append(nb)
    return out
# Critical difference from trees: MUST track visited, or cycles loop forever.


def graph_dfs(graph: dict, start: str, visited=None, out=None) -> list:
    if visited is None:
        visited, out = set(), []
    visited.add(start)
    out.append(start)
    for nb in graph[start]:
        if nb not in visited:
            graph_dfs(graph, nb, visited, out)
    return out


def connected_components(graph: dict) -> int:
    visited, count = set(), 0
    for node in graph:
        if node not in visited:
            count += 1
            stack = [node]
            visited.add(node)
            while stack:
                cur = stack.pop()
                for nb in graph[cur]:
                    if nb not in visited:
                        visited.add(nb)
                        stack.append(nb)
    return count
# Pattern: loop all nodes; unvisited -> traverse from it, count 1. Composes a
# traversal into a real algorithm — common "level 2" follow-up.


def has_path(graph: dict, start: str, end: str) -> bool:
    return end in graph_bfs(graph, start)
# Follow-up: "shortest path?" -> BFS gives fewest-edges shortest path on an
# unweighted graph; weighted graphs need Dijkstra (name-drop, don't implement
# unless asked).
```

---

## 5. Live Coding — Sorting

```python
def merge_sort(nums: list) -> list:
    if len(nums) <= 1:
        return nums
    mid = len(nums) // 2
    left, right = merge_sort(nums[:mid]), merge_sort(nums[mid:])
    return merge_sorted(left, right)      # from Section 2
# O(n log n) always, O(n) extra space, stable. Divide and conquer poster child.


def quicksort(nums: list) -> list:
    if len(nums) <= 1:
        return nums
    pivot = nums[len(nums) // 2]
    less    = [x for x in nums if x < pivot]
    equal   = [x for x in nums if x == pivot]
    greater = [x for x in nums if x > pivot]
    return quicksort(less) + equal + quicksort(greater)
# O(n log n) average, O(n^2) worst case (already-sorted input + always picking
# an endpoint as pivot). Fix: randomize the pivot, or use median-of-three.
```

**Talking points (no code needed):** Python's built-in `sort`/`sorted` is **Timsort** — a hybrid merge/insertion sort, stable, adaptive (runs in O(n) on already-sorted or nearly-sorted data). "When would you hand-roll a sort?" → almost never in production; the question tests understanding, not utility. **Stability** matters when sorting by multiple keys across passes — equal elements must keep their relative order from the previous pass.

**Finance-flavored composite — plausible SIG question:**
```python
def max_profit(prices: list[float]) -> float:
    if not prices:
        return 0
    min_price, best = prices[0], 0
    for p in prices[1:]:
        best = max(best, p - min_price)
        min_price = min(min_price, p)
    return best
# O(n) one pass: track running min and running best profit. The naive O(n^2)
# all-pairs comparison is the trap — name it, then don't write it.
```

---

## 6. Python & Core Programming (conceptual)

### "Explain how decorators work under the hood, write one that logs execution time."
"A decorator is a higher-order function: it takes a function and returns a new callable that wraps it. `@timer` above a function is just sugar for `slow_add = timer(slow_add)`. `functools.wraps` copies over `__name__`/`__doc__` so introspection and stack traces still point at the original function instead of `wrapper`."

```python
import time
import functools

def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__} took {elapsed:.4f}s")
        return result
    return wrapper

@timer
def slow_add(a, b):
    time.sleep(0.1)
    return a + b
```

### "Generator vs list comprehension — memory and execution?"
"A list comprehension eagerly builds the entire list in memory — O(n) space up front. A generator expression (parens instead of brackets) is lazy: it produces one value at a time on `next()`, computed on demand, O(1) space, and can only be iterated once. Use generators for large or streaming data, or when chaining a pipeline of transforms without materializing intermediates; use a list when you need random access, `len()`, or to iterate more than once."

### "How does the GIL impact multi-threaded data processing, and how do you bypass it?"
"The GIL means only one thread executes Python bytecode at a time, so CPU-bound pure-Python threads don't get real parallelism — they take turns. Threads still help for I/O-bound work because the GIL is released during blocking I/O (network, disk, `time.sleep`). To bypass it for CPU-bound work: use `multiprocessing` (separate processes, separate GILs, real parallelism, at the cost of IPC/serialization overhead), or drop into C-extension code that releases the GIL during heavy computation — which is exactly what NumPy/Pandas do under the hood for vectorized ops. `asyncio` is a different axis entirely: single-threaded cooperative concurrency, great for thousands of concurrent I/O waits, but doesn't help CPU-bound work either."

### "Deep copy vs shallow copy — when would you use each?"
"A shallow copy (`copy.copy`, `list(x)`, slicing) creates a new outer container but the nested objects inside are still shared references with the original. A deep copy (`copy.deepcopy`) recursively copies everything, so the two structures become fully independent — `deepcopy` also handles reference cycles via an internal memo dict, so it won't infinite-loop on self-referential structures. Use shallow copy when you only need to mutate the top level and nested objects are immutable or intentionally shared (cheaper); use deep copy when you need full independence of nested mutable state — it costs more time and memory, so don't reach for it by default."

### "How does Python manage memory? What does the GC do?"
"CPython's primary mechanism is reference counting: every object carries a count of references pointing at it; when the count hits zero, the object is freed immediately and deterministically. That alone can't free reference cycles — two objects pointing at each other never reach zero — so there's a generational cyclic garbage collector (three generations, on the theory most objects die young) that periodically finds and breaks unreachable cycles. Refcounting does the everyday work instantly; the GC is the backstop for cycles.

Connective tissue worth having ready: refcount updates aren't thread-safe on their own — the GIL is largely what protects them, which ties this back to the concurrency answer. And this is *why* dtype work in Pandas/NumPy isn't just about speed: a 2M-row `object` column is 2M individually refcounted Python objects; a `float64` column is one object wrapping a raw C buffer — you're taking the data out of Python's object machinery entirely."

### "Instance/class/static method, `is` vs `==`, mutable default args, closures, scoping, memory management deep-dive, OOP patterns, threads vs processes vs asyncio, race conditions, deadlocks"
Full spoken answers for these already live in `R2_CONCEPT.md` in this folder — that file is the answer key for the "Data types & object model," "Functions," "Classes," "Memory management," "OOP design patterns," and "Concurrency" sections. Read it once out loud before the interview; it's written in the same 30–60s spoken-answer format as this doc.

---

## 7. Pandas Internals

### "How does Pandas manage data under the hood? What is the BlockManager?"
"A DataFrame isn't a dict of independent Series — internally, columns sharing the same dtype are grouped into contiguous NumPy-backed 'blocks,' and the `BlockManager` tracks which block owns which columns. That's what lets same-dtype operations vectorize efficiently across a whole block at once. The implication: a DataFrame with lots of mixed dtypes fragments into many small blocks, and operations that add/drop columns or change a dtype can trigger block consolidation, which has a real cost. It's also the root cause of `SettingWithCopyWarning` — whether a slice you took is a *view* into an existing block or a fresh *copy* depends on block layout, so mutating it may or may not affect the original. Worth name-dropping: pandas 2.0+ is moving toward an Arrow-backed backend / `ArrayManager` that relaxes some of this, but BlockManager is still the classic mental model."

### "How would you optimize a slow row-by-row Pandas operation over millions of rows?"
"First move: stop iterating in Python. `df.iterrows()` and `.apply(axis=1)` both drop into per-row Python function calls — no vectorization, and `iterrows()` also reconstructs a Series per row, which is expensive. Replace with:
- vectorized arithmetic directly on columns (`df['a'] + df['b']`)
- `np.where` / `np.select` for row-wise conditional logic
- `.map()` for dict-style lookups, `.groupby(...).transform(...)` instead of a manual loop with an accumulator
- `category` dtype for low-cardinality repeated strings
- if truly nothing vectorizes cleanly, `.apply` with `engine='numba'` or dropping to `.to_numpy()` and vectorizing in raw NumPy as a last resort

The underlying reason all of this matters: vectorized ops loop in C over a contiguous memory buffer; the Python-level loop pays per-element bytecode dispatch and object overhead on top of the actual work — that gap is what you're eliminating."

### "loc, iloc, and basic indexing — performance and behavior?"
"`loc` is label-based — it indexes by index/column labels, and slices are *inclusive* of the end label. `iloc` is purely positional — integer offsets, slices exclusive of the end, just like normal Python slicing. Plain `df[...]` is overloaded and inconsistent: a single label or list selects columns, but a slice selects rows by position — that ambiguity is exactly why `loc`/`iloc` exist, and I default to them for clarity. The real performance/correctness trap isn't `loc` vs `iloc`, it's *chained* indexing — `df[cond][col] = x` — which can silently operate on a copy instead of a view and throws `SettingWithCopyWarning`; the fix is a single `.loc[cond, col] = x`."

### "How does Pandas handle missing data across dtypes, and what are the performance implications of casting?"
"Pandas represents missing float data with `np.nan`, which is itself a float — so a numeric column that picks up even one missing value gets silently upcast to `float64`, even if it started as `int8` or `int32`. That's not just a type change, it's a real memory cost — an `int8` column with one NaN becomes 8x larger as `float64`. Object/string columns mix `None`/`np.nan` and fall back to slower Python-object-level comparisons instead of vectorized NumPy ops. Pandas' newer nullable dtypes (`Int64`, `boolean`, `StringDtype`, using `pd.NA`) fix the upcasting problem by supporting missingness natively, at the cost of some operations being less mature/slightly slower than the classic NumPy-backed path."

### "Explain vectorization and why it's faster than Python loops."
"Vectorization means expressing an operation as a single call over an entire array, which NumPy/Pandas execute as a tight loop in compiled C over a contiguous memory buffer — no per-element Python bytecode dispatch, no per-element Python object creation. A Python `for` loop over a Series does both of those things on every single element. Same asymptotic complexity (O(n) either way) — the difference is entirely in the constant factor, and at millions of rows that constant factor is the whole story."

---

## 8. Data Engineering Architecture

### "Design an ETL pipeline to ingest and process high-frequency market data with minimal latency."
- **Ingest:** capture raw off the exchange feed (FIX/multicast/vendor API) into an append-only log (Kafka or similar) as close to wire format as possible — minimal transformation at the door, stamp both exchange time and receipt time immediately. Append-only gives replayability for free.
- **Process:** a streaming layer (Flink/Kafka Streams, or hand-rolled with NumPy-vectorized batches) does normalization, dedup, sequence-gap detection, and derives bars/aggregates. In the hot path, avoid per-message Python object churn — batch into NumPy/Arrow buffers rather than one Python dict per tick.
- **Store:** hot tier optimized for point lookups/recent data (in-memory, or a low-latency columnar store); cold tier as partitioned Parquet (by date/symbol) on object storage for backtesting and historical research.
- **Latency levers:** compact binary serialization over JSON, zero-copy where feasible, pinned threads, and a deliberate choice between blocking for out-of-order packets vs. emitting immediately and correcting downstream.
- **Data quality:** monitor sequence numbers for gaps, cross-check against a secondary vendor feed, alert on latency/volume anomalies.
- Frame the answer around the real trade-off: **throughput vs. latency vs. completeness** — that's the sentence that shows judgment, not just component-naming.

### "Row-oriented (Avro) vs column-oriented (Parquet) — what factors drive the choice?"
"Avro is row-oriented with the schema embedded in the file/message — good for write-heavy, full-record access patterns: streaming payloads, Kafka topics, anything read record-by-record. Its schema evolution story (add optional fields with defaults) is genuinely excellent, which is the biggest reason it's the default for event/message formats. Parquet is column-oriented — great for analytical read patterns that scan a handful of columns across millions of rows: better compression (similar values sit together), column pruning, and per-row-group statistics that let query engines (Spark, Athena, Presto) skip data entirely. My default split: Avro for the transport/write path, converted to Parquet for the analytical/backtesting layer."

### "Approach to data quality checks and monitoring in a production pipeline."
- Schema validation at ingestion — quarantine records that don't conform rather than failing the whole batch (dead-letter queue).
- Completeness/null checks and business-rule range checks (price > 0, quantity within bounds).
- Volume and freshness monitoring — row counts vs. historical baseline, SLA on data arrival time.
- Reconciliation — counts/sums cross-checked against the source system.
- Idempotency/dedup checks so replays and backfills don't double-count.
- Tooling to name-drop: Great Expectations or dbt tests for the assertions, Grafana/PagerDuty for alerting on the resulting metrics.

### "Handling schema evolution for pipelines feeding downstream quant models."
"I'd put a schema registry (Confluent Schema Registry style) in front of the pipeline enforcing compatibility rules — backward/forward/full — so producers and consumers can evolve independently. Additive changes (new optional field with a default) are safe by construction; renames, type changes, or removals are breaking and need a versioned schema plus a translation layer, or a coordinated dual-write/dual-read migration window. The quant-model angle is the important nuance: a schema change that silently alters what a feature *means* (not just its name) won't crash anything — the model will just quietly degrade. So the real requirement is a frozen, versioned feature contract with contract tests, and proactively communicating any change to the consuming team before it ships."

### "Optimize a slow SQL query joining several large transaction tables."
1. `EXPLAIN ANALYZE` first — find sequential scans, bad join order, and cardinality mis-estimates before touching anything.
2. Confirm join keys are indexed (composite indexes matching join + filter columns, leftmost-prefix rule).
3. Push filters down — filter before joining, not after; for outer joins, know the difference between a `WHERE` filter (silently turns a LEFT JOIN into an INNER JOIN) and an `ON` filter.
4. Reduce volume pre-join — pre-aggregate, or filter to a relevant partition (date-partitioned tables let you prune whole partitions).
5. Watch for implicit type casts on join keys — they silently defeat index usage.
6. If it's still slow at scale: precomputed summary tables for hot repeated queries, broadcast joins for small dimension tables, or move the heavy lift to a columnar engine (Spark/Snowflake/BigQuery) built for large joins.

---

## 9. SQL Question Bank

*(from the "questions most likely to come up" table — sorted by relevance in the source doc)*

**1. Calculate Monthly Sales Growth by Product Category**
```sql
WITH monthly_sales AS (
  SELECT category,
         DATE_TRUNC('month', order_date) AS month,
         SUM(amount) AS total_sales
  FROM orders
  GROUP BY category, DATE_TRUNC('month', order_date)
)
SELECT category, month, total_sales,
       LAG(total_sales) OVER (PARTITION BY category ORDER BY month) AS prev_month,
       ROUND(100.0 * (total_sales - LAG(total_sales) OVER (PARTITION BY category ORDER BY month))
             / NULLIF(LAG(total_sales) OVER (PARTITION BY category ORDER BY month), 0), 2) AS growth_pct
FROM monthly_sales
ORDER BY category, month;
```
`LAG` gets the prior period within each category's window; `NULLIF` guards divide-by-zero when a prior month had 0 sales.

**2. Multi-Level Aggregations in SQL**
```sql
SELECT category, region, SUM(amount) AS total
FROM orders
GROUP BY ROLLUP (category, region)
ORDER BY category, region;
```
`ROLLUP` adds subtotal rows per category plus one grand-total row; `CUBE` would add every combination of subtotals (category-only, region-only, and grand total). `GROUPING SETS` if you need an arbitrary custom set of aggregation levels.

**3. Choosing INNER vs LEFT JOIN**
"INNER JOIN keeps only rows with a match on both sides. LEFT JOIN keeps every row from the left table, filling `NULL` for unmatched right-side columns — use it when 'no match' is itself meaningful, e.g., customers with zero orders. The classic bug: putting a right-table filter in `WHERE` instead of `ON` silently turns a LEFT JOIN back into an INNER JOIN, because the filter runs *after* the join and drops the NULL rows you were trying to keep."

**4. Troubleshoot Nightly Orders Pipeline Failure** — see [Section 10](#10-pipeline-troubleshooting-scenarios).

**5. Understanding Database Indexing Purpose**
"An index is an auxiliary structure — typically a B-tree — that lets the engine locate rows without a full table scan, at the cost of extra storage and slower writes (every insert/update/delete also maintains the index). Best applied to high-selectivity columns that are frequently filtered, joined, or sorted on. For composite indexes, column order matters — the leftmost-prefix rule means an index on `(a, b)` helps queries filtering on `a` or `a AND b`, but not on `b` alone. Over-indexing a write-heavy table is a real anti-pattern."

**6. Discuss Core SQL Query Experience** — open prompt; be ready to speak concretely about: window functions (`LAG`/`LEAD`/`ROW_NUMBER`/running aggregates), CTEs for readability, query-plan-driven tuning, joining normalized schemas, and — given SIG's domain — comfort with time-series/tick-style queries (as-of joins, sessionization).

**7. Data Quality in ETL Pipelines** — see [Section 8](#8-data-engineering-architecture), "data quality checks and monitoring."

**8 / 10. Prioritizing Across Competing Projects / Conflicting High-Stakes Work** — see [Section 11](#11-behavioral--leadership).

**9. Handling Missing Data in Pipelines**
"First question is whether it's missing-and-expected or missing-and-anomalous. For expected gaps in time series, forward-fill or a documented default — but watch for lookahead bias if you're filling from future data. For anomalous gaps, don't silently interpolate financial data — flag it (a `data_quality`/`is_imputed` column) so downstream consumers, especially a quant model, know the value isn't a real observation. Whether to drop, impute, or flag-and-pass-through depends entirely on what the downstream consumer can tolerate."

**11. Choosing Batch vs Real Time**
"Real-time/streaming when the cost of staleness exceeds the cost of the added complexity — trading signals, fraud detection, live dashboards. Batch when correctness and completeness matter more than latency, reprocessing/backfill needs to be easy, and the use case tolerates delay — end-of-day reporting, training set generation. In practice a lot of systems end up hybrid (Lambda/Kappa-style): a streaming path for freshness, a batch path for reconciliation and the source of truth."

**12. Leading Through an Ambiguous Project Crisis** — see [Section 11](#11-behavioral--leadership).

**13. Cloud AI Deployment Pipeline Experience**
Talk concretely about: CI/CD for models (retrain → validate → deploy gates), containerization, monitoring for data/model drift post-deployment, and a defined rollback strategy if a new model version regresses.

**14. Diagnose an Integration Pipeline Issue**
Framework: reproduce → isolate which stage is losing/corrupting data → check the contract/schema between the two systems at that boundary → use logs/tracing to pinpoint → check row counts at each stage to localize where volume drops → fix, add a regression test, add a monitor so it self-reports next time instead of being rediscovered.

**15. Influencing a Cross-Functional Decision** — see [Section 11](#11-behavioral--leadership).

**16. Real-Time Dashboard Data Pipeline**
Architecture: source → streaming ingestion (Kafka) → stream processing with windowed aggregation → low-latency serving store (Redis/Druid/ClickHouse) → dashboard via websocket push or short-poll. Trade-off to name: push (server initiates, lower latency, more server-side complexity) vs. poll (simpler, adds latency = poll interval); and pre-aggregating at write time vs. aggregating at query time.

**17. Explaining Technical Complexity to Business Partners** — see [Section 11](#11-behavioral--leadership).

**18 / 19. Resolving Conflict Within Your Team / on a Client Account** — see [Section 11](#11-behavioral--leadership).

**20. Integrating Multiple Data Sources**
Talk about: schema harmonization into a canonical model, entity resolution when sources use different keys for the "same" thing, handling differing update cadences and time zones, and establishing a data contract with each source owner so upstream changes don't silently break the integration.

---

## 10. Pipeline Troubleshooting Scenarios

**"Nightly orders pipeline failed overnight — walk me through how you'd diagnose it."**
1. Check the job's logs and exit code first — is it a crash, a timeout, or silent bad data?
2. Check upstream: did the source data land on time and in full? (Freshness/completeness of the *input* before you touch the pipeline.)
3. Check for schema drift — a new/renamed/retyped column breaking a parser is the single most common silent failure.
4. Check resource limits — OOM, disk full, connection pool exhaustion.
5. Check for partial/duplicate runs — did a retry double-write before failing? Idempotency matters here.
6. Fix the immediate issue, then close the loop: add a monitor/alert so this exact failure mode pages someone next time instead of being discovered the next morning, and write a short postmortem if it was customer/desk-visible.

This is also the shape of a good answer to "Diagnose an Integration Pipeline Issue" (#14 above) — same diagnostic ladder, different boundary (between two systems instead of one nightly job).

---

## 11. Behavioral & Leadership

These are evaluated on **structure + specificity**, not on technical correctness — use **STAR** (Situation, Task, Action, Result) and make sure the "Action" section is about *your* decisions, not the team's. Below is the framework for each; slot in your own real example — a fabricated story will fall apart under a follow-up question, and SIG's own tip sheet explicitly says "we want to hear your real life examples."

| # | Question | What a strong answer covers |
|---|---|---|
| 8 | Prioritizing Across Competing Client Projects | How you assessed urgency/impact objectively (not just "who shouted loudest"), what trade-off you made explicit to stakeholders, and the outcome |
| 10 | Prioritizing Conflicting High-Stakes Work | A concrete prioritization framework (impact × urgency, blast radius, reversibility) applied to a real conflict, and how you communicated the trade-off upward |
| 12 | Leading Through an Ambiguous Project Crisis | How you created clarity under uncertainty — what you did *first* when the scope wasn't defined, how you got stakeholder alignment, the concrete result |
| 15 | Influencing a Cross-Functional Decision | A case where you didn't have authority but needed buy-in — what evidence/framing changed minds, not just "I explained it well" |
| 17 | Explaining Technical Complexity to Business Partners | A specific analogy or framing you used, and evidence it landed (they made a correct decision based on it) |
| 18 | Resolving Conflict Within Your Team | Focus on the process you used to surface and resolve disagreement, not just the resolution — and what you'd do differently |
| 19 | Resolving Conflict on a Client Account | Similar to #18 but with an external party — emphasize maintaining the relationship while still solving the technical/scope disagreement |

**Prep move:** write one real STAR example per row above (bullet points, not full prose) before the interview — five minutes each, twenty-five minutes total. Several of these questions are close enough in shape that one or two well-chosen stories can answer three or four of them with different framing.

---

## Quick Pre-Interview Checklist
- [ ] Ran `r2_exercises.py` and `r2_exercises_part2.py` cold, checked against Sections 2–5 above, redone-from-scratch anything you needed help on
- [ ] Read `R2_CONCEPT.md` out loud once
- [ ] Read Sections 6–8 above out loud once (Python internals / Pandas / architecture)
- [ ] Picked one real STAR story per row in Section 11
- [ ] Pencil and paper ready for the live call — official SIG instruction, for tree/graph problems
- [ ] Confirmed CodeSignal access works on your machine before the call
