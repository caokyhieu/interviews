"""
R2 Practice Part 2 — Trees, Graphs, Sorting
============================================
Covers the topics from SIG's official document not in r2_exercises.py:
tree/graph traversals, searching/sorting, recursion at depth.

Run:  python r2_exercises_part2.py

Rule from the official doc worth honoring in practice: have PENCIL AND
PAPER next to you. For every tree/graph problem, DRAW the structure
first, trace your algorithm on paper, THEN code. That's not a crutch —
it's what strong candidates do in the actual interview.
"""

# =====================================================================
# TREES
# =====================================================================

class Node:
    def __init__(self, val, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

# Test tree — draw this on paper NOW:
#            8
#          /   \
#         3     10
#        / \      \
#       1   6      14
#          / \    /
#         4   7  13
def make_tree():
    return Node(8,
        Node(3, Node(1), Node(6, Node(4), Node(7))),
        Node(10, None, Node(14, Node(13))))


def dfs_inorder(root) -> list:
    """Left, node, right — recursively. On the test tree this returns
    SORTED order (it's a BST — be ready to say why inorder on a BST is
    sorted). Also be ready for: preorder (node,L,R), postorder (L,R,node),
    and 'what's the complexity?' (O(n) time, O(h) space for the stack)."""
    # TODO
    raise NotImplementedError


def bfs_level_order(root) -> list:
    """Breadth-first: visit level by level, left to right.
    Use a queue — collections.deque, popleft().
    THE interview distinction: DFS = stack (or recursion), BFS = queue.
    Say it out loud every time until it's a reflex."""
    # TODO
    raise NotImplementedError


def tree_height(root) -> int:
    """Height = number of nodes on the longest root-to-leaf path
    (empty tree = 0). Classic 3-line recursion:
    1 + max(height(left), height(right))."""
    # TODO
    raise NotImplementedError


def bst_contains(root, target) -> bool:
    """Search a BST WITHOUT visiting every node — go left or right by
    comparison. O(h), which is O(log n) balanced / O(n) degenerate.
    This is binary search wearing a tree costume — say that connection."""
    # TODO
    raise NotImplementedError


def dfs_iterative(root) -> list:
    """Preorder DFS with an EXPLICIT STACK, no recursion.
    Why it matters: (a) interviewers ask 'now without recursion',
    (b) it proves you know recursion IS a stack, (c) Python's ~1000
    recursion limit is a real constraint you can name."""
    # TODO
    raise NotImplementedError


# =====================================================================
# GRAPHS — adjacency list = dict of node -> list of neighbors
# =====================================================================

# Draw this too. A-B, A-C, B-D, C-D, D-E, F-G (disconnected!)
GRAPH = {
    "A": ["B", "C"], "B": ["A", "D"], "C": ["A", "D"],
    "D": ["B", "C", "E"], "E": ["D"],
    "F": ["G"], "G": ["F"],
}


def graph_bfs(graph: dict, start: str) -> list:
    """Return nodes reachable from start, in BFS visit order.
    THE critical difference from trees: you MUST track visited nodes
    or cycles loop you forever. visited set + deque. Neighbors in
    given order."""
    # TODO
    raise NotImplementedError


def graph_dfs(graph: dict, start: str) -> list:
    """Same but depth-first (recursive or explicit stack, your call)."""
    # TODO
    raise NotImplementedError


def connected_components(graph: dict) -> int:
    """How many disconnected islands? (GRAPH above has 2.)
    Pattern: loop over all nodes; if unvisited, BFS/DFS from it and
    count 1. This composes your traversal into a real algorithm —
    a very common 'level 2' follow-up."""
    # TODO
    raise NotImplementedError


def has_path(graph: dict, start: str, end: str) -> bool:
    """Is there a route from start to end? (Reuse a traversal.)
    Follow-up to be ready for verbally: 'shortest path?' -> BFS gives
    fewest-edges shortest path in unweighted graphs; weighted needs
    Dijkstra (name-drop, don't implement)."""
    # TODO
    raise NotImplementedError


# =====================================================================
# SORTING — implement two, KNOW the rest as talking points
# =====================================================================

def merge_sort(nums: list) -> list:
    """You already wrote merge_sorted() in part 1 — mergesort is just:
    split in half, sort each recursively, merge. O(n log n) always,
    O(n) extra space, stable. Divide and conquer poster child."""
    # TODO
    raise NotImplementedError


def quicksort(nums: list) -> list:
    """Simple version: pick pivot, partition into <, ==, >, recurse.
    O(n log n) average, O(n^2) worst (sorted input + bad pivot — be
    ready to explain WHY and the fix: random pivot).
    Talking points, not code: Python's built-in sort is TIMSORT —
    hybrid mergesort/insertion sort, stable, O(n) on nearly-sorted
    data. 'When would you implement your own sort?' -> almost never;
    the question tests understanding, not utility. Know stability:
    equal elements keep relative order — matters when sorting by
    multiple keys in passes."""
    # TODO
    raise NotImplementedError


# =====================================================================
# ONE FINANCE-FLAVORED COMPOSITE (plausible SIG-style question)
# =====================================================================

def max_profit(prices: list[float]) -> float:
    """Buy once, sell once, maximize profit (0 if impossible).
    e.g. [7,1,5,3,6,4] -> 5  (buy at 1, sell at 6).
    O(n) one pass: track min-so-far and best-profit-so-far.
    The naive O(n^2) all-pairs version is the trap — mention it,
    then don't write it."""
    # TODO
    raise NotImplementedError


# =====================================================================
# TESTS
# =====================================================================

def run_tests():
    passed = 0
    def check(name, cond):
        nonlocal passed
        if cond:
            passed += 1; print(f"  PASS {name}")
        else:
            print(f"  FAIL {name}")

    t = make_tree()
    try: check("dfs_inorder", dfs_inorder(t) == [1, 3, 4, 6, 7, 8, 10, 13, 14])
    except NotImplementedError: print("  TODO dfs_inorder")
    try: check("bfs_level_order", bfs_level_order(t) == [8, 3, 10, 1, 6, 14, 4, 7, 13])
    except NotImplementedError: print("  TODO bfs_level_order")
    try: check("tree_height", tree_height(t) == 4 and tree_height(None) == 0)
    except NotImplementedError: print("  TODO tree_height")
    try: check("bst_contains", bst_contains(t, 13) and not bst_contains(t, 5))
    except NotImplementedError: print("  TODO bst_contains")
    try: check("dfs_iterative", dfs_iterative(t) == [8, 3, 1, 6, 4, 7, 10, 14, 13])
    except NotImplementedError: print("  TODO dfs_iterative")

    try: check("graph_bfs", graph_bfs(GRAPH, "A") == ["A", "B", "C", "D", "E"])
    except NotImplementedError: print("  TODO graph_bfs")
    try: check("graph_dfs", set(graph_dfs(GRAPH, "A")) == {"A", "B", "C", "D", "E"})
    except NotImplementedError: print("  TODO graph_dfs")
    try: check("connected_components", connected_components(GRAPH) == 2)
    except NotImplementedError: print("  TODO connected_components")
    try: check("has_path", has_path(GRAPH, "A", "E") and not has_path(GRAPH, "A", "F"))
    except NotImplementedError: print("  TODO has_path")

    try: check("merge_sort", merge_sort([5, 2, 9, 1, 5, 6]) == [1, 2, 5, 5, 6, 9]
               and merge_sort([]) == [])
    except NotImplementedError: print("  TODO merge_sort")
    try: check("quicksort", quicksort([5, 2, 9, 1, 5, 6]) == [1, 2, 5, 5, 6, 9])
    except NotImplementedError: print("  TODO quicksort")
    try: check("max_profit", max_profit([7, 1, 5, 3, 6, 4]) == 5
               and max_profit([7, 6, 5]) == 0)
    except NotImplementedError: print("  TODO max_profit")

    print(f"\n{passed} checks passed.")


if __name__ == "__main__":
    run_tests()
