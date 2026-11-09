# SIG (Susquehanna International Group) — Data Engineer **R2 / Technical Phone Interview** Prep Guide

> **Location:** Dublin, Ireland · **Round:** R2 — live technical interview with a Software Engineer
> **Compiled:** 2026-07-20 · Sources at the bottom.

---

## 1. What this round actually is

Cross-referencing the three HR documents ([context-hr.md](context-hr.md), the official *Technical Phone Interview* PDF, and the *SIG Data Engineer 2026 guide* PDF) with real candidate reports online:

| Attribute | Detail |
|---|---|
| **Interviewer** | A Software Engineer who develops in *your* language of expertise (Python), on a team aligned to your skillset. |
| **Duration** | 60–90 minutes. |
| **Tool** | Live **CodeSignal** session — you share a computer and code with the engineer in real time. Have **pencil & paper** handy. |
| **Format** | Walk through 1–2 coding problems, narrating your thought process. Expect follow-ups pushing on complexity & edge cases. |
| **Rules** | ❌ No automated / external code-generation tools (no Copilot, no ChatGPT). |
| **Topics (official)** | Data structures, algorithms, OOP design patterns, Big-O, tree/graph traversals, recursion, searching/sorting, hash tables, concurrency. |
| **Difficulty** | Medium → Medium-Hard LeetCode-style. Common areas: arrays/strings, hash maps, linked lists, trees/graphs, 2D matrix traversal, light DP. |

### What HR (Killian) stressed — read this twice
- **"A lot more in depth than R1. Heavily focused on Python — data types, functions, classes."**
- **"Practice basic CS algorithms."**
- **"Some candidates skip that low-level code, which catches them out."** → Don't only prep Pandas/ETL talking points; be able to *implement* algorithms from scratch, cleanly, in Python.

### How to win the room (SIG-specific)
1. **Think out loud.** They evaluate *approach*, not just the final answer. State assumptions, name the data structure, give Big-O *before* coding.
2. **Explain how things work under the hood** — SIG explicitly "values deep technical understanding over superficial framework knowledge." Being able to say *why* a `set` lookup is O(1) or *why* vectorization beats a Python loop scores points.
3. **Clarify first, then code.** Ask about input size, duplicates, empties, sorted-ness.
4. **Optimize iteratively.** Brute force → identify bottleneck → improve. Verbalize the trade-off.
5. **Test your own code** on a small example and an edge case before saying "done."

---

## 2. Python language internals (verbal Q&A — the PDF's "Python & Core Programming")

These are near-certain warm-up / follow-up questions. Answer concisely, then show you can back it with code.

### 2.1 How do decorators work? Write a timing decorator.
A decorator is a callable that takes a function and returns a new function, letting you wrap behavior *around* it without editing it. `@deco` above `def f` is sugar for `f = deco(f)`. Use `functools.wraps` to preserve the wrapped function's `__name__`/`__doc__`.

```python
import functools, time

def timeit(func):
    @functools.wraps(func)               # keep name, docstring, signature metadata
    def wrapper(*args, **kwargs):
        start = time.perf_counter()      # perf_counter: monotonic, high-resolution
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__} took {elapsed:.6f}s")
        return result
    return wrapper

@timeit
def process(rows):
    return sum(r ** 2 for r in rows)
```
**Follow-up — decorator with arguments** (an extra layer of nesting = a decorator *factory*):
```python
def retry(times):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*a, **kw):
            for attempt in range(times):
                try:
                    return func(*a, **kw)
                except Exception:
                    if attempt == times - 1:
                        raise
        return wrapper
    return decorator
```

### 2.2 Generator vs list comprehension — memory & execution
- **List comp `[x for x in it]`** builds the *entire* list in memory eagerly → O(n) memory.
- **Generator `(x for x in it)`** is **lazy**: yields one item at a time, holds O(1) state, computes on demand. Ideal for streaming large market-data files you can't fit in RAM.
```python
squares_list = [x*x for x in range(10_000_000)]   # ~ hundreds of MB, all at once
squares_gen  = (x*x for x in range(10_000_000))   # a few hundred bytes; nothing computed yet
total = sum(squares_gen)                           # streamed, constant memory
```
Trade-off: generators are single-pass (exhausted after one iteration) and not indexable/`len()`-able.

### 2.3 The GIL and multi-threaded data processing
The **Global Interpreter Lock** allows only one thread to execute Python bytecode at a time, so **CPU-bound** work does *not* speed up with threads. Ways around it:
- **`multiprocessing`** — separate processes, each with its own interpreter/GIL → true parallelism (cost: IPC/serialization).
- **Release the GIL in C extensions** — NumPy/Pandas/Polars do heavy numeric work in C with the GIL released, so vectorized ops parallelize internally.
- **`threading` is still great for I/O-bound** work (network/disk waits release the GIL).
- **`asyncio`** for high-concurrency I/O on one thread.
- (Modern note: Python 3.13+ ships an experimental **free-threaded / no-GIL** build.)

### 2.4 Deep copy vs shallow copy
- **Shallow (`copy.copy` / `list[:]` / `dict(d)`)** copies the top-level container but shares references to nested objects.
- **Deep (`copy.deepcopy`)** recursively copies everything → fully independent.
```python
import copy
a = [[1, 2], [3, 4]]
b = copy.copy(a)          # shallow
b[0].append(99)           # also mutates a[0] -> [1, 2, 99]
c = copy.deepcopy(a)      # independent; safe to mutate c without touching a
```
Use shallow when nested objects are immutable or intentionally shared; deep when you need isolation (e.g., snapshotting config before mutation).

### 2.5 Memory management, reference counting & the GC
CPython manages memory primarily by **reference counting**: each object tracks how many references point to it; when the count hits 0 it's freed immediately. Reference counting *alone* can't reclaim **reference cycles** (A→B→A), so a **generational garbage collector** (`gc` module, 3 generations) periodically detects and frees unreachable cycles. Objects surviving collections are promoted to older generations, collected less often. `sys.getrefcount(obj)` inspects counts.

---

## 3. Pandas internals (verbal Q&A — likely, given the DE role)

Concise, high-signal answers:

- **BlockManager:** A DataFrame isn't stored column-by-column separately — Pandas consolidates columns of the **same dtype** into 2D NumPy "blocks" managed by the `BlockManager`. Contiguous same-dtype storage is cache-friendly and enables vectorization, but repeated `df['new'] = ...` can trigger costly block consolidation/copies.
- **Vectorization:** Operations run as compiled C loops over contiguous NumPy arrays (SIMD, no per-element Python object overhead), vs a Python `for`/`iterrows` loop that boxes each value into a Python object. Often 10–100×+ faster.
- **Optimize row-by-row on millions of rows:** ditch `iterrows`/`apply(axis=1)`. Prefer **vectorized** array ops → `np.where`/`np.select` for conditionals → `groupby().agg` → `numba`/`Cython`/`polars`/`pyarrow` as escalation. Downcast dtypes (`int64→int32`, `object→category`) to cut memory & speed up.
- **`loc` vs `iloc` vs `[]`:** `loc` = label-based, `iloc` = integer-position-based, `df['col']`/`df[mask]` = column select or boolean mask. Chained indexing `df[...][...]` risks `SettingWithCopyWarning` — use single `.loc[rows, cols]` for assignment.
- **NaN handling:** `NaN` is a float, so an integer column with a missing value is upcast to `float64` (or use the newer nullable `Int64`/`pyarrow` dtypes). Casting large columns is O(n) and can double memory transiently.

---

## 4. Coding problems — the core of R2 (Python solutions + Big-O)

These are representative of SIG's live CodeSignal problems: arrays/strings, hash maps, two pointers, linked lists, stacks, trees/graphs, matrix, recursion, sorting, light DP. Practice **writing them from a blank editor** and stating complexity out loud.

### 4.1 Two Sum (hash map) — the archetypal warm-up
```python
def two_sum(nums, target):
    seen = {}                       # value -> index
    for i, n in enumerate(nums):
        if target - n in seen:      # O(1) average lookup
            return [seen[target - n], i]
        seen[n] = i
    return []
# Time O(n), Space O(n). Talking point: set/dict lookup is O(1) avg via hashing.
```

### 4.2 Valid Anagram / group anagrams (hashing, counting)
```python
from collections import Counter, defaultdict

def is_anagram(s, t):
    return Counter(s) == Counter(t)          # O(n)

def group_anagrams(words):
    groups = defaultdict(list)
    for w in words:
        key = tuple(sorted(w))               # or a 26-length count tuple
        groups[key].append(w)
    return list(groups.values())
# is_anagram: O(n). group_anagrams: O(N * k log k) with k=word length.
```

### 4.3 Two pointers — pair sum in a sorted array / reverse in place
```python
def pair_sum_sorted(arr, target):            # arr is sorted
    lo, hi = 0, len(arr) - 1
    while lo < hi:
        s = arr[lo] + arr[hi]
        if s == target:
            return (lo, hi)
        if s < target:
            lo += 1
        else:
            hi -= 1
    return None
# Time O(n), Space O(1). Contrast with the hash-map version's O(n) space.
```

### 4.4 Sliding window — longest substring without repeating characters
```python
def longest_unique_substring(s):
    last = {}                        # char -> last index seen
    start = best = 0
    for i, ch in enumerate(s):
        if ch in last and last[ch] >= start:
            start = last[ch] + 1     # shrink window past the duplicate
        last[ch] = i
        best = max(best, i - start + 1)
    return best
# Time O(n), Space O(min(n, alphabet)).
```

### 4.5 Binary search (know it cold — off-by-ones are a classic trap)
```python
def binary_search(arr, target):      # arr sorted ascending
    lo, hi = 0, len(arr) - 1
    while lo <= hi:
        mid = (lo + hi) // 2         # in Python no int overflow; still a good habit: lo + (hi-lo)//2
        if arr[mid] == target:
            return mid
        if arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1
# Time O(log n), Space O(1). Follow-up: leftmost/rightmost insertion -> use bisect_left / bisect_right.
```

### 4.6 Linked list — reverse, and detect a cycle (Floyd's)
```python
class ListNode:
    def __init__(self, val=0, nxt=None):
        self.val, self.next = val, nxt

def reverse_list(head):
    prev = None
    while head:
        head.next, prev, head = prev, head, head.next   # atomic swap
    return prev
# O(n) time, O(1) space.

def has_cycle(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:
            return True
    return False
# O(n) time, O(1) space — the tortoise & hare.
```

### 4.7 Stack — valid parentheses
```python
def is_valid_parens(s):
    pairs = {')': '(', ']': '[', '}': '{'}
    stack = []
    for ch in s:
        if ch in pairs.values():          # opening bracket
            stack.append(ch)
        elif ch in pairs:                 # closing bracket
            if not stack or stack.pop() != pairs[ch]:
                return False
    return not stack
# O(n) time, O(n) space.
```

### 4.8 Trees — BFS, DFS, and a common validity check
```python
from collections import deque

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val, self.left, self.right = val, left, right

def bfs_levels(root):                      # level-order traversal
    if not root:
        return []
    out, q = [], deque([root])
    while q:
        level = []
        for _ in range(len(q)):
            node = q.popleft()
            level.append(node.val)
            if node.left:  q.append(node.left)
            if node.right: q.append(node.right)
        out.append(level)
    return out

def inorder(root):                         # recursive DFS
    return inorder(root.left) + [root.val] + inorder(root.right) if root else []

def is_valid_bst(root, lo=float('-inf'), hi=float('inf')):
    if not root:
        return True
    if not (lo < root.val < hi):
        return False
    return (is_valid_bst(root.left, lo, root.val) and
            is_valid_bst(root.right, root.val, hi))
# All O(n) time; recursion uses O(h) stack (h = height).
```

### 4.9 Graphs — BFS shortest path on a grid / DFS island count
```python
from collections import deque

def num_islands(grid):                     # 2D matrix traversal — a SIG favorite
    if not grid:
        return 0
    rows, cols = len(grid), len(grid[0])
    seen = set()

    def dfs(r, c):
        stack = [(r, c)]
        while stack:
            i, j = stack.pop()
            if (0 <= i < rows and 0 <= j < cols
                    and grid[i][j] == '1' and (i, j) not in seen):
                seen.add((i, j))
                stack.extend([(i+1, j), (i-1, j), (i, j+1), (i, j-1)])

    count = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == '1' and (r, c) not in seen:
                dfs(r, c)
                count += 1
    return count
# Time O(rows*cols), Space O(rows*cols). Note: iterative DFS avoids recursion-depth limits.

def shortest_path_grid(grid, start, goal):  # unweighted -> BFS
    rows, cols = len(grid), len(grid[0])
    q = deque([(start, 0)])
    seen = {start}
    while q:
        (r, c), dist = q.popleft()
        if (r, c) == goal:
            return dist
        for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
            nr, nc = r+dr, c+dc
            if (0 <= nr < rows and 0 <= nc < cols
                    and grid[nr][nc] == 0 and (nr, nc) not in seen):
                seen.add((nr, nc))
                q.append(((nr, nc), dist + 1))
    return -1
```

### 4.10 Matrix manipulation — rotate 90° in place / spiral
```python
def rotate_90_clockwise(m):                # in-place, n x n
    n = len(m)
    for i in range(n):                     # transpose
        for j in range(i + 1, n):
            m[i][j], m[j][i] = m[j][i], m[i][j]
    for row in m:                          # reverse each row
        row.reverse()
    return m
# O(n^2) time, O(1) extra space.
```

### 4.11 Sorting — implement merge sort (know the recurrence)
```python
def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left, right = merge_sort(arr[:mid]), merge_sort(arr[mid:])
    return merge(left, right)

def merge(a, b):
    out, i, j = [], 0, 0
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:                   # <= keeps it stable
            out.append(a[i]); i += 1
        else:
            out.append(b[j]); j += 1
    out.extend(a[i:]); out.extend(b[j:])
    return out
# Time O(n log n) always; Space O(n). Stable. Contrast: quicksort O(n log n) avg / O(n^2) worst, in-place.
```
> **Be ready to state Big-O for the common sorts:** quicksort avg `O(n log n)`/worst `O(n²)`, merge/heap `O(n log n)`, and that Python's built-in `sorted`/`list.sort` is **Timsort** — `O(n log n)`, stable, near-`O(n)` on partially sorted data.

### 4.12 Light DP — climbing stairs / max subarray (Kadane)
```python
def climb_stairs(n):                       # Fibonacci-shaped DP, O(n) time O(1) space
    a, b = 1, 1
    for _ in range(n):
        a, b = b, a + b
    return a

def max_subarray(nums):                    # Kadane's algorithm
    best = cur = nums[0]
    for x in nums[1:]:
        cur = max(x, cur + x)              # extend or restart
        best = max(best, cur)
    return best
# Both O(n) time, O(1) space.
```

---

## 5. OOP / classes — SIG cares about design (HR called out "classes")

Be able to design a small class hierarchy cleanly. Example: an in-memory **order book / LRU-style cache** is a classic "build a data structure" ask.

### 5.1 Design an LRU cache (dict + doubly-linked list, all O(1))
```python
from collections import OrderedDict

class LRUCache:
    """O(1) get/put using an insertion-ordered dict."""
    def __init__(self, capacity):
        self.capacity = capacity
        self.store = OrderedDict()         # key -> value, ordered by recency

    def get(self, key):
        if key not in self.store:
            return -1
        self.store.move_to_end(key)        # mark most-recently used
        return self.store[key]

    def put(self, key, value):
        if key in self.store:
            self.store.move_to_end(key)
        self.store[key] = value
        if len(self.store) > self.capacity:
            self.store.popitem(last=False)  # evict least-recently used
```

### 5.2 Clean OOP idioms they may probe
```python
class Instrument:
    __slots__ = ("symbol", "price")        # __slots__: no per-instance __dict__ -> less memory, faster attr access

    def __init__(self, symbol, price):
        self.symbol = symbol
        self._price = price                # convention: leading underscore = "internal"

    @property                              # computed/validated attribute access
    def price(self):
        return self._price

    def __repr__(self):                    # dunder for debuggable output
        return f"Instrument({self.symbol!r}, {self._price})"

    def __eq__(self, other):               # value equality; pair with __hash__ if used in sets/dicts
        return isinstance(other, Instrument) and self.symbol == other.symbol
```
Be ready to discuss: `@classmethod` vs `@staticmethod`, `__init__` vs `__new__`, inheritance vs composition, abstract base classes (`abc.ABC`), and why `__slots__`/`@dataclass` matter for memory in data-heavy systems.

---

## 6. Behavioral / experience — keep 2–3 STAR stories ready

The engineer may probe your resume and ask real-life examples. Have crisp stories on: a data pipeline you built/optimized, a nasty bug you diagnosed, batch-vs-realtime trade-offs you made, a data-quality incident, and collaborating with non-engineers (traders/quants). Structure: **Situation → Task → Action → Result**, lead with the result.

---

## 7. Final checklist (the night before)

- [ ] Can I implement, from a blank file: binary search, BFS/DFS, reverse a linked list, merge sort, a hash-map two-pass — **without lookups**?
- [ ] Can I state Big-O time *and* space for each before I code?
- [ ] Can I explain decorators, generators, the GIL, deep/shallow copy, refcount+GC — out loud in 30 seconds each?
- [ ] Can I explain *why* vectorization/`set` lookup/columnar storage is fast (under-the-hood)?
- [ ] CodeSignal environment tested; pencil & paper ready; quiet room; no AI tools open.
- [ ] 3 STAR stories rehearsed.
- [ ] Questions for the interviewer prepared (team, tech stack, what "good" looks like in the role).

---

## Sources
- Official HR docs: [context-hr.md](context-hr.md), *Technical Phone Interview.pdf*, *SIG Data Engineer interview questions & guide 2026.pdf* (in this folder).
- [SIG Data Engineer Interview Guide — InterviewQuery](https://www.interviewquery.com/interview-guides/susquehanna-international-group-llp-sig-data-engineer)
- [SIG Software Engineer Interview Guide — InterviewQuery](https://www.interviewquery.com/interview-guides/susquehanna-international-group-llp-sig-software-engineer)
- [How I Crushed SIG's CodeSignal Assessment — linkjob.ai](https://www.linkjob.ai/interview-questions/susquehanna-international-group-codesignal/)
- [SIG Software Engineer Interviews — Glassdoor](https://www.glassdoor.com/Interview/Susquehanna-International-Group-Software-Engineer-Interview-Questions-EI_IE24446.0,31_KO32,49.htm)
- [20 SIG Interview Questions & Answers — ClimbTheLadder](https://climbtheladder.com/susquehanna-international-group-sig-interview-questions/)
- [Expectations for Live CodeSignal phone interview @SIG — Blind](https://www.teamblind.com/post/Expectations-for-Live-Codesignal-phone-interview-@SIG-KGRER5GC)
