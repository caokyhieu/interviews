# SIG R2 — Timed Mock Set (exam conditions)

> **Rules — enforce them.** No AI tools, no Googling, blank editor, pencil & paper allowed, single timer running. Narrate out loud (record yourself, or type comments) as if the engineer is watching. Only open **Part B — Solution Key** after time is up.
>
> Two mocks below, matching the two shapes R2 can take. Fresh problems — none repeat [R2-prep-guide.md](R2-prep-guide.md) or [R2-practice-drills.md](R2-practice-drills.md).

---

# MOCK 1 — CodeSignal format · ⏱ 75 minutes · 4 tasks

Difficulty escalates T1 → T4 (matches real candidate reports). **Suggested budget: T1 10m · T2 15m · T3 25m · T4 25m.** Bank time on early tasks. Read all four first.

### T1 — Easy (single-pass) · target 10 min
A hiker's path is a string of `'U'` (up) and `'D'` (down) steps, each 1 unit, starting at sea level (0). A **valley** is a maximal sequence of steps below sea level. Return the number of valleys walked through.
Example: `"DDUUUUDD" → 1`; `"UDDDUDUU" → 1`; `"" → 0`.
```
# Clarify / approach / Big-O:

# Code:



# Tested on example? Edge cases (empty, all up)?
```

### T2 — Easy-Medium (prefix sum + hash map) · target 15 min
Given an integer array `nums` and integer `k`, return the **number of contiguous subarrays** whose sum equals `k`. Values may be negative.
Example: `nums=[1,1,1], k=2 → 2`; `nums=[1,-1,0], k=0 → 3`.
```
# Clarify / approach / Big-O:

# Code:



# Why does a hash map of prefix-sum counts work? What about the empty prefix?
```

### T3 — Medium-Hard (2D matrix traversal) · target 25 min
Given an `m x n` matrix, return **all elements in spiral order** (right → down → left → up, spiraling inward).
Example: `[[1,2,3],[4,5,6],[7,8,9]] → [1,2,3,6,9,8,7,4,5]`. Non-square allowed.
```
# Clarify / approach / Big-O:

# Code:



# How do you avoid re-visiting? Boundaries vs visited-set — trade-offs?
```

### T4 — Medium-Hard (data-structure construction) · target 25 min
Design `RandomizedSet` supporting **average O(1)**: `insert(val)` (returns False if already present), `remove(val)` (returns False if absent), and `get_random()` (returns a uniformly random current element).
```
# Clarify / approach / Big-O per op:

# Code:



# How do you get O(1) remove from an array? (hint: swap-with-last)
```

---

# MOCK 2 — Live interview format · ⏱ 60 minutes · 2 problems + follow-ups

This mirrors the real R2: fewer problems, deeper. The interviewer will interrupt with follow-ups — **answer them before moving on**. Budget ~30 min each.

### L1 — Merge Intervals (+ follow-up)
Given a list of intervals `[[start, end], ...]`, merge all overlapping intervals and return the result.
Example: `[[1,3],[2,6],[8,10],[15,18]] → [[1,6],[8,10],[15,18]]`.
```
# Approach / Big-O:

# Code:


```
**Follow-up F1a:** Now the list is already sorted and you must **insert** a new interval `newInterval` into it, merging as needed, in **O(n)** (no re-sort). Example: insert `[4,8]` into `[[1,3],[6,9]] → [[1,3],[4,9]]`.
```
# Code:


```
**Follow-up F1b (verbal):** Intervals arrive as a *stream* too large for memory. How would you compute total covered length? (Think: what must you assume about ordering? What if unsorted?)
```
# Notes:

```

### L2 — Top K Frequent Elements (+ follow-up)
Given `nums` and integer `k`, return the `k` most frequent elements (any order).
Example: `nums=[1,1,1,2,2,3], k=2 → [1,2]`.
```
# Approach / Big-O:  (can you beat O(n log n)?)

# Code:


```
**Follow-up F2a:** Give an **O(n)** solution (no full sort). Hint: bucket by frequency.
```
# Code:


```
**Follow-up F2b (DE-flavored, verbal):** Same query over an unbounded event stream, memory-bounded, approximate answer acceptable. What structure? (Expected: **Count-Min Sketch** + a bounded min-heap / "heavy hitters" / space-saving algorithm.) Explain the accuracy/memory trade-off.
```
# Notes:

```

---

## Self-scoring rubric (score yourself honestly, per problem)

| Dimension | 0 | 1 | 2 |
|---|---|---|---|
| **Clarified** before coding (assumptions, edge cases) | skipped | partial | asked the right Qs |
| **Stated Big-O** (time *and* space) before coding | no | one | both, correct |
| **Correctness** on example + an edge case | fails | example only | example + edges |
| **Optimality** (hit the intended complexity) | brute force | 1 level better | optimal |
| **Communication** (narrated approach clearly) | silent | some | clear throughout |

**Interpretation:** Mock 1 (4 tasks × 10) and Mock 2 (2 problems × 10, follow-ups fold in). Per mock: **≥40/50 or ≥16/20** = interview-ready pace. Note *which dimension* you lose points on — that's your drill target for tomorrow.

---
---
<br><br><br>
---
---
# PART B — Solution Key (open only after time is up)
---
---

## Mock 1

**T1 — Count Valleys.** Track altitude; a valley is entered each time you step **up to sea level (0) from below** (i.e., the step that ends at 0 having started at -1).
```python
def count_valleys(path):
    altitude = 0
    valleys = 0
    for step in path:
        if step == 'U':
            altitude += 1
            if altitude == 0:        # just climbed out of a valley back to sea level
                valleys += 1
        else:
            altitude -= 1
    return valleys
# Time O(n), Space O(1).
```

**T2 — Subarray Sum Equals K.** Prefix sum + hash map of how many times each prefix sum has occurred. A subarray `(j, i]` sums to `k` iff `prefix[i] - prefix[j] == k` → look up `prefix[i] - k`. Seed with `{0: 1}` for the empty prefix (handles subarrays starting at index 0).
```python
from collections import defaultdict

def subarray_sum(nums, k):
    counts = defaultdict(int)
    counts[0] = 1                    # empty prefix seen once
    prefix = 0
    result = 0
    for n in nums:
        prefix += n
        result += counts[prefix - k] # how many earlier prefixes make a window summing to k
        counts[prefix] += 1
    return result
# Time O(n), Space O(n). Handles negatives (sliding window would NOT).
```

**T3 — Spiral Order.** Shrink four boundaries as you peel layers. Guard the inner two directions to avoid double-counting a single leftover row/column.
```python
def spiral_order(matrix):
    if not matrix or not matrix[0]:
        return []
    top, bottom = 0, len(matrix) - 1
    left, right = 0, len(matrix[0]) - 1
    out = []
    while top <= bottom and left <= right:
        for c in range(left, right + 1):          # top row L->R
            out.append(matrix[top][c])
        top += 1
        for r in range(top, bottom + 1):          # right col T->B
            out.append(matrix[r][right])
        right -= 1
        if top <= bottom:                         # bottom row R->L (guard)
            for c in range(right, left - 1, -1):
                out.append(matrix[bottom][c])
            bottom -= 1
        if left <= right:                         # left col B->T (guard)
            for r in range(bottom, top - 1, -1):
                out.append(matrix[r][left])
            left += 1
    return out
# Time O(m*n), Space O(1) extra (output aside). Boundary approach avoids a visited-set (less memory).
```

**T4 — RandomizedSet.** Array for O(1) random; dict `val → index` for O(1) locate. Remove = swap target with the last element, pop, fix the moved element's index.
```python
import random

class RandomizedSet:
    def __init__(self):
        self.vals = []               # dense array of elements
        self.pos = {}                # val -> index in self.vals

    def insert(self, val):
        if val in self.pos:
            return False
        self.pos[val] = len(self.vals)
        self.vals.append(val)
        return True

    def remove(self, val):
        if val not in self.pos:
            return False
        i = self.pos[val]
        last = self.vals[-1]
        self.vals[i] = last          # move last element into the hole
        self.pos[last] = i
        self.vals.pop()              # O(1) pop from the end
        del self.pos[val]
        return True

    def get_random(self):
        return random.choice(self.vals)
# All ops average O(1). Space O(n).
```

---

## Mock 2

**L1 — Merge Intervals.** Sort by start; merge into the last kept interval when it overlaps.
```python
def merge_intervals(intervals):
    intervals.sort(key=lambda x: x[0])
    merged = []
    for start, end in intervals:
        if merged and start <= merged[-1][1]:     # overlap with previous
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return merged
# Time O(n log n) (the sort), Space O(n).
```
**F1a — Insert Interval (O(n), input already sorted).** Three phases: intervals entirely before, the overlapping block (merge), intervals entirely after.
```python
def insert_interval(intervals, new):
    res = []
    i, n = 0, len(intervals)
    # 1) everything ending before new starts
    while i < n and intervals[i][1] < new[0]:
        res.append(intervals[i]); i += 1
    # 2) merge all overlapping into new
    while i < n and intervals[i][0] <= new[1]:
        new = [min(new[0], intervals[i][0]), max(new[1], intervals[i][1])]
        i += 1
    res.append(new)
    # 3) the rest
    while i < n:
        res.append(intervals[i]); i += 1
    return res
# Time O(n), Space O(n). No re-sort needed.
```
**F1b — Streaming coverage.** If the stream is guaranteed sorted by start, you only ever compare against the current open interval → O(1) memory, merge-on-the-fly summing covered length. If **unsorted**, you can't do it exactly in one pass with bounded memory (a later small interval could sit inside an earlier gap); you'd need external sort (spill to disk, sort, then linear merge) or an interval tree if you must answer incrementally.

**L2 — Top K Frequent.** Count, then a size-`k` min-heap over frequencies.
```python
import heapq
from collections import Counter

def top_k_frequent(nums, k):
    counts = Counter(nums)
    # nlargest is a bounded heap under the hood: O(n log k)
    return [val for val, _ in heapq.nlargest(k, counts.items(), key=lambda x: x[1])]
# Time O(n log k), Space O(n).
```
**F2a — O(n) bucket sort by frequency.** Frequencies are bounded by `len(nums)`, so bucket by count and read from the top.
```python
from collections import Counter

def top_k_frequent_linear(nums, k):
    counts = Counter(nums)
    buckets = [[] for _ in range(len(nums) + 1)]   # index = frequency
    for val, freq in counts.items():
        buckets[freq].append(val)
    out = []
    for freq in range(len(buckets) - 1, 0, -1):    # high freq -> low
        for val in buckets[freq]:
            out.append(val)
            if len(out) == k:
                return out
    return out
# Time O(n), Space O(n).
```
**F2b — Streaming heavy hitters.** Use a **Count-Min Sketch** (hash-based sublinear frequency estimator; overcounts, never undercounts) paired with a bounded min-heap of the top candidates, or the **Space-Saving / Misra-Gries** algorithm for approximate top-k. Trade-off: fixed memory (`width × depth` counters) and one pass, at the cost of some over-estimation whose error bound shrinks as you widen the sketch. This is the "right" DE answer — SIG values knowing the streaming/approximate structure, not just the batch heap.

---

### Post-mock review checklist
- [ ] Which task blew the time budget? Why — stuck on approach, or on syntax/bugs?
- [ ] Any task where I coded before stating Big-O? (Fix that habit — it's free points.)
- [ ] Did I catch edge cases *myself*, or only when checking the key?
- [ ] For the follow-ups, could I articulate the streaming/approximate structures out loud?
- [ ] Re-attempt any sub-16/20 mock cold in 2 days.
