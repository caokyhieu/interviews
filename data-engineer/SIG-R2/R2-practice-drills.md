# SIG R2 — Practice Drills (problems first, solutions at the end)

> **How to use this:** Cover the bottom half. For each problem — (1) restate it & ask clarifying Qs, (2) state your approach + Big-O **before** coding, (3) write the solution in the space provided, (4) test on the example, (5) check against the solution key. Time-box each to ~15 min like the real CodeSignal round.
>
> Companion to [R2-prep-guide.md](R2-prep-guide.md). Weighted toward **DP & graphs** as requested.

---

# PART A — Problems

## Warm-ups (arrays / hashing / strings)

**P1. Contains Duplicate Within K.** Given `nums` and integer `k`, return `True` if there are two equal values at indices `i, j` with `|i - j| <= k`.
Example: `nums=[1,2,3,1], k=3 → True`; `k=2 → False`.
```
# Approach + Big-O:

# Your code:



```

**P2. Product of Array Except Self.** Return `out[i] = product of all nums except nums[i]`, **without division**, in O(n).
Example: `[1,2,3,4] → [24,12,8,6]`.
```
# Approach + Big-O:

# Your code:



```

**P3. First Non-Repeating Character.** Return the index of the first char in `s` that appears once, else `-1`.
Example: `"leetcode" → 0`, `"aabb" → -1`.
```
# Approach + Big-O:

# Your code:



```

---

## Graphs (BFS / DFS / topological / union-find / Dijkstra)

**G1. Clone Graph.** Given a reference to a node in a connected undirected graph (each node has `val` and `neighbors`), return a deep copy.
```
# Approach + Big-O:

# Your code:



```

**G2. Number of Connected Components.** `n` nodes labeled `0..n-1` and an edge list `edges`. Return the number of connected components.
Example: `n=5, edges=[[0,1],[1,2],[3,4]] → 2`.
```
# Approach + Big-O:

# Your code:



```

**G3. Course Schedule (cycle detection / topological sort).** `numCourses` and `prerequisites[i]=[a,b]` meaning b before a. Return `True` if all courses can be finished (i.e., the directed graph is a DAG).
Example: `2, [[1,0]] → True`; `2, [[1,0],[0,1]] → False`.
```
# Approach + Big-O:

# Your code:



```

**G4. Rotting Oranges (multi-source BFS).** Grid of `0` empty, `1` fresh, `2` rotten. Each minute, rotten oranges rot 4-adjacent fresh ones. Return minutes until none fresh, or `-1` if impossible.
Example: `[[2,1,1],[1,1,0],[0,1,1]] → 4`.
```
# Approach + Big-O:

# Your code:



```

**G5. Network Delay Time (Dijkstra).** `times[i]=[u,v,w]` directed edge with travel time `w`, `n` nodes `1..n`, source `k`. Return the time for all nodes to receive the signal, or `-1`.
Example: `times=[[2,1,1],[2,3,1],[3,4,1]], n=4, k=2 → 2`.
```
# Approach + Big-O:

# Your code:



```

---

## Dynamic Programming (1D → 2D)

**D1. House Robber.** Max sum of non-adjacent elements in `nums`.
Example: `[2,7,9,3,1] → 12` (2+9+1).
```
# Approach + Big-O:

# Your code:



```

**D2. Coin Change.** Fewest coins from `coins` summing to `amount`, else `-1`. Unlimited coins.
Example: `coins=[1,2,5], amount=11 → 3` (5+5+1).
```
# Approach + Big-O:

# Your code:



```

**D3. Longest Increasing Subsequence.** Length of the LIS in `nums`.
Example: `[10,9,2,5,3,7,101,18] → 4` ([2,3,7,101]).
```
# Approach + Big-O:  (aim to discuss O(n^2) DP AND O(n log n) patience sort)

# Your code:



```

**D4. 0/1 Knapsack.** `weights`, `values`, capacity `W`. Max value; each item used at most once.
Example: `w=[1,3,4,5], v=[1,4,5,7], W=7 → 9` (items with w=3,4 → v=4+5).
```
# Approach + Big-O:

# Your code:



```

**D5. Unique Paths (grid DP).** Robot at top-left of `m x n` grid moves only right/down. How many paths to bottom-right?
Example: `m=3, n=7 → 28`.
```
# Approach + Big-O:

# Your code:



```

**D6. Edit Distance (2D string DP).** Min single-char insert/delete/replace operations to turn `word1` into `word2`.
Example: `"horse", "ros" → 3`.
```
# Approach + Big-O:

# Your code:



```

**D7. Word Break.** Given `s` and a dictionary `words`, can `s` be segmented into a space-separated sequence of dictionary words?
Example: `s="leetcode", words=["leet","code"] → True`.
```
# Approach + Big-O:

# Your code:



```

---

<br><br><br>

---
---
# PART B — Solution Key
---
---

## Warm-ups

**S-P1. Contains Duplicate Within K** — sliding window of the last `k` values in a set.
```python
def contains_nearby_duplicate(nums, k):
    window = set()
    for i, n in enumerate(nums):
        if n in window:
            return True
        window.add(n)
        if len(window) > k:              # keep window size <= k
            window.discard(nums[i - k])
    return False
# Time O(n), Space O(min(n, k)).
```

**S-P2. Product of Array Except Self** — prefix products then suffix products.
```python
def product_except_self(nums):
    n = len(nums)
    out = [1] * n
    prefix = 1
    for i in range(n):                   # out[i] = product of everything left of i
        out[i] = prefix
        prefix *= nums[i]
    suffix = 1
    for i in range(n - 1, -1, -1):       # multiply in product of everything right of i
        out[i] *= suffix
        suffix *= nums[i]
    return out
# Time O(n), Space O(1) extra (output aside). No division needed.
```

**S-P3. First Non-Repeating Character** — count, then first with count 1.
```python
from collections import Counter

def first_uniq_char(s):
    counts = Counter(s)
    for i, ch in enumerate(s):
        if counts[ch] == 1:
            return i
    return -1
# Time O(n), Space O(alphabet).
```

---

## Graphs

**S-G1. Clone Graph** — DFS/BFS with a `visited` map from original node → clone.
```python
class Node:
    def __init__(self, val, neighbors=None):
        self.val = val
        self.neighbors = neighbors or []

def clone_graph(node):
    if not node:
        return None
    clones = {}                          # original -> clone

    def dfs(orig):
        if orig in clones:
            return clones[orig]
        copy = Node(orig.val)
        clones[orig] = copy              # register BEFORE recursing (handles cycles)
        for nb in orig.neighbors:
            copy.neighbors.append(dfs(nb))
        return copy

    return dfs(node)
# Time O(V + E), Space O(V).
```

**S-G2. Number of Connected Components** — Union-Find (or DFS flood).
```python
def count_components(n, edges):
    parent = list(range(n))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]   # path compression
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
            return True                     # merged two components
        return False

    components = n
    for a, b in edges:
        if union(a, b):
            components -= 1
    return components
# Time ~O((V+E) * α(V)) ≈ near-linear, Space O(V).
```

**S-G3. Course Schedule** — Kahn's algorithm (BFS topological sort); DAG iff all nodes processed.
```python
from collections import deque, defaultdict

def can_finish(num_courses, prerequisites):
    graph = defaultdict(list)
    indegree = [0] * num_courses
    for a, b in prerequisites:           # b -> a  (take b before a)
        graph[b].append(a)
        indegree[a] += 1

    q = deque([i for i in range(num_courses) if indegree[i] == 0])
    processed = 0
    while q:
        node = q.popleft()
        processed += 1
        for nxt in graph[node]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                q.append(nxt)
    return processed == num_courses      # if a cycle exists, some nodes never reach indegree 0
# Time O(V + E), Space O(V + E).
```

**S-G4. Rotting Oranges** — multi-source BFS: seed the queue with ALL rotten cells at once.
```python
from collections import deque

def oranges_rotting(grid):
    rows, cols = len(grid), len(grid[0])
    q = deque()
    fresh = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 2:
                q.append((r, c, 0))      # (row, col, minute)
            elif grid[r][c] == 1:
                fresh += 1

    minutes = 0
    while q:
        r, c, t = q.popleft()
        minutes = max(minutes, t)
        for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1:
                grid[nr][nc] = 2         # mark rotten to avoid re-visiting
                fresh -= 1
                q.append((nr, nc, t + 1))
    return minutes if fresh == 0 else -1
# Time O(rows*cols), Space O(rows*cols).
```

**S-G5. Network Delay Time** — Dijkstra with a min-heap.
```python
import heapq
from collections import defaultdict

def network_delay_time(times, n, k):
    graph = defaultdict(list)
    for u, v, w in times:
        graph[u].append((v, w))

    dist = {}
    heap = [(0, k)]                      # (cumulative_time, node)
    while heap:
        time, node = heapq.heappop(heap)
        if node in dist:                 # already finalized (first pop = shortest)
            continue
        dist[node] = time
        for nb, w in graph[node]:
            if nb not in dist:
                heapq.heappush(heap, (time + w, nb))

    return max(dist.values()) if len(dist) == n else -1
# Time O(E log V), Space O(V + E).
```

---

## Dynamic Programming

**S-D1. House Robber** — at each house, rob (skip prev) or skip.
```python
def rob(nums):
    prev, curr = 0, 0                    # prev = best up to i-2, curr = best up to i-1
    for x in nums:
        prev, curr = curr, max(curr, prev + x)
    return curr
# Time O(n), Space O(1).
```

**S-D2. Coin Change** — bottom-up: dp[a] = fewest coins to make amount a.
```python
def coin_change(coins, amount):
    INF = amount + 1
    dp = [0] + [INF] * amount
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a:
                dp[a] = min(dp[a], dp[a - c] + 1)
    return dp[amount] if dp[amount] != INF else -1
# Time O(amount * len(coins)), Space O(amount).
```

**S-D3. Longest Increasing Subsequence** — two approaches; know both.
```python
# O(n^2) classic DP
def lis_n2(nums):
    if not nums:
        return 0
    dp = [1] * len(nums)                 # dp[i] = LIS ending at i
    for i in range(len(nums)):
        for j in range(i):
            if nums[j] < nums[i]:
                dp[i] = max(dp[i], dp[j] + 1)
    return max(dp)

# O(n log n) patience sorting: 'tails[k]' = smallest possible tail of an LIS of length k+1
import bisect
def lis_nlogn(nums):
    tails = []
    for x in nums:
        i = bisect.bisect_left(tails, x)
        if i == len(tails):
            tails.append(x)              # extend
        else:
            tails[i] = x                 # replace to keep tails minimal
    return len(tails)
```

**S-D4. 0/1 Knapsack** — 1D rolling array iterated **right-to-left** so each item is used once.
```python
def knapsack(weights, values, W):
    dp = [0] * (W + 1)                   # dp[c] = best value with capacity c
    for wt, val in zip(weights, values):
        for c in range(W, wt - 1, -1):   # reverse: prevents reusing the same item
            dp[c] = max(dp[c], dp[c - wt] + val)
    return dp[W]
# Time O(n * W), Space O(W).
```

**S-D5. Unique Paths** — dp[j] += dp[j-1] over rows (or the C(m+n-2, n-1) combinatorics answer).
```python
def unique_paths(m, n):
    dp = [1] * n                         # first row: only one way to each cell
    for _ in range(1, m):
        for j in range(1, n):
            dp[j] += dp[j - 1]           # from top (dp[j]) + from left (dp[j-1])
    return dp[-1]
# Time O(m*n), Space O(n).
```

**S-D6. Edit Distance** — 2D DP over the two strings (Levenshtein).
```python
def edit_distance(w1, w2):
    m, n = len(w1), len(w2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i                     # delete all of w1[:i]
    for j in range(n + 1):
        dp[0][j] = j                     # insert all of w2[:j]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if w1[i - 1] == w2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]           # no op
            else:
                dp[i][j] = 1 + min(dp[i - 1][j],      # delete
                                   dp[i][j - 1],      # insert
                                   dp[i - 1][j - 1])  # replace
    return dp[m][n]
# Time O(m*n), Space O(m*n)  (reducible to O(n) with two rows).
```

**S-D7. Word Break** — dp[i] = can s[:i] be segmented.
```python
def word_break(s, words):
    wordset = set(words)
    n = len(s)
    dp = [True] + [False] * n
    for i in range(1, n + 1):
        for j in range(i):
            if dp[j] and s[j:i] in wordset:
                dp[i] = True
                break
    return dp[n]
# Time O(n^2 * k) with substring hashing (k = word length), Space O(n).
```

---

### Big-O cheat card for this set
| Pattern | Time | Key idea |
|---|---|---|
| Sliding-window set (P1) | O(n) | keep window ≤ k |
| Prefix/suffix (P2) | O(n) | two passes, no division |
| Union-Find (G2) | ~O(n·α) | path compression |
| Topological sort / Kahn (G3) | O(V+E) | indegree → queue |
| Multi-source BFS (G4) | O(V+E) | seed all sources |
| Dijkstra (G5) | O(E log V) | min-heap, finalize on pop |
| 1D DP (D1,D2,D5) | O(n) / O(n·m) | rolling array |
| Knapsack (D4) | O(n·W) | reverse loop = 0/1 |
| LIS patience (D3) | O(n log n) | `bisect` on tails |
| 2D string DP (D6) | O(m·n) | insert/delete/replace |
