"""
R2 Practice — Python fundamentals & basic algorithms
=====================================================
Implement each function marked TODO, then run this file:

    python r2_exercises.py

Each exercise has asserts that tell you if you got it right.
NO imports allowed inside your solutions except where noted —
the point is raw Python fluency, not library knowledge.

Work top to bottom; they're ordered by importance for a live round.
"""

# =====================================================================
# PART 1 — PREDICT THE OUTPUT (don't run first — write your answer as a
# comment, THEN run and compare. These are classic gotchas.)
# =====================================================================

def gotchas():
    # 1.1 Mutable default argument — THE classic
    def append_to(item, target=[]):
        target.append(item)
        return target
    a = append_to(1) # [1]
    b = append_to(2) # [2]
    print("1.1:", a, b)          # predict: ?

    # 1.2 Late binding in closures
    funcs = [lambda: i for i in range(3)]
    print("1.2:", [f() for f in funcs])   # predict: ?

    # 1.3 is vs ==
    x = [1, 2]; y = [1, 2]
    print("1.3:", x == y, x is y)          # predict: ?

    # 1.4 Aliasing vs copying
    m = [[0] * 3] * 3
    m[0][0] = 9
    print("1.4:", m)                       # predict: ?

    # 1.5 Tuple "immutability"
    t = ([1, 2], 3)
    t[0].append(99)
    print("1.5:", t)                       # predict: ?

    # 1.6 Integer division & modulo with negatives
    print("1.6:", -7 // 2, -7 % 2)         # predict: ?

    # 1.7 Chained comparison
    print("1.7:", 3 > 2 > 1, (3 > 2) > 1)  # predict: ?

    # 1.8 Dict ordering (3.7+) and set ordering
    d = {"b": 1, "a": 2}; d["c"] = 3
    print("1.8:", list(d))                 # predict: ?


# =====================================================================
# PART 2 — IMPLEMENT: core algorithm patterns
# =====================================================================

def reverse_words(s: str) -> str:
    """'hello world foo' -> 'foo world hello'. No .split()[::-1] one-liner
    first — do it once manually (walk the string), THEN write the one-liner.
    Interviewers often say 'now without split' — be ready."""
    # TODO
    raise NotImplementedError


def first_non_repeating(s: str) -> str | None:
    """Return the first character that appears exactly once, else None.
    Target O(n). Say out loud why two nested loops would be O(n^2)."""
    # TODO
    raise NotImplementedError


def two_sum(nums: list[int], target: int) -> tuple[int, int] | None:
    """Return INDICES (i, j), i < j, with nums[i] + nums[j] == target.
    O(n) with a dict — the single most-asked warmup in live rounds.
    Explain: what does the dict map, and why one pass suffices?"""
    # TODO
    raise NotImplementedError


def binary_search(sorted_nums: list[int], target: int) -> int:
    """Return index of target or -1. Write it from memory; off-by-one
    errors here are exactly the 'low level code' that catches people out.
    Know: why lo <= hi, why mid +/- 1, complexity O(log n)."""
    # TODO
    raise NotImplementedError


def merge_sorted(a: list[int], b: list[int]) -> list[int]:
    """Merge two sorted lists into one sorted list in O(len(a)+len(b)).
    No sorted(a + b) — that's O(n log n) and dodges the question.
    This is the heart of mergesort; be able to say that."""
    # TODO
    raise NotImplementedError


def dedupe_keep_order(items: list) -> list:
    """Remove duplicates, preserving first-seen order, O(n).
    Why does set() alone not work? What must items be for this to work
    at all? (hashable — be ready to define that word.)"""
    # TODO
    raise NotImplementedError


def char_count(s: str) -> dict:
    """Count characters. Write it three ways (any one passes the test):
    plain dict + if, dict.get(c, 0) + 1, and know that
    collections.Counter exists. Interviewers like seeing the ladder."""
    # TODO
    raise NotImplementedError


def is_anagram(s1: str, s2: str) -> bool:
    """O(n) using your char_count. Also know the sorted(s1)==sorted(s2)
    version and its O(n log n) complexity — mention the trade-off."""
    # TODO
    raise NotImplementedError


def fibonacci(n: int) -> int:
    """fib(0)=0, fib(1)=1. Write it ITERATIVELY (O(n) time, O(1) space).
    Be ready to discuss: why is naive recursion O(2^n)? How does
    memoization fix it? (functools.lru_cache name-drop.)"""
    # TODO
    raise NotImplementedError


def flatten(nested: list) -> list:
    """Flatten arbitrarily nested lists: [1,[2,[3,4]],5] -> [1,2,3,4,5].
    Natural recursion practice. Bonus: rewrite with an explicit stack
    and explain when recursion depth becomes a real problem in Python
    (default limit ~1000)."""
    # TODO
    raise NotImplementedError


def moving_average(nums: list[float], window: int) -> list[float]:
    """Sliding window: averages of each consecutive `window` elements.
    O(n) with a running sum, not O(n*window) recomputing each window.
    Finance-flavored — plausible in this interview."""
    # TODO
    raise NotImplementedError


# =====================================================================
# PART 3 — IMPLEMENT: classes & the data model
# =====================================================================

class Trade:
    """A trade with symbol, quantity, price.
    Implement:
      - __init__(symbol, quantity, price)
      - notional property (quantity * price)  [use @property]
      - __repr__ -> "Trade('AAPL', 100, 190.5)"
      - __eq__ so two Trades with same fields are equal
      - __hash__ so Trades can live in a set (rule: objects that are
        == must have the same hash; easiest: hash a tuple of fields)
    Talking points: why does defining __eq__ without __hash__ make the
    class unhashable? What's the contract between them?
    """
    # TODO
    pass


class Portfolio:
    """Holds Trades. Implement:
      - add(trade)
      - __len__ -> number of trades
      - __iter__ -> iterate over trades       [hint: yield from / iter()]
      - total_notional() -> sum of trade notionals
      - __contains__(symbol: str) -> True if any trade has that symbol,
        so `'AAPL' in portfolio` works.
    Talking point: dunder methods are how your objects plug into
    Python's built-in syntax (len, in, for) — that's 'the data model'.
    """
    # TODO
    pass


# Also be ready to DISCUSS (no code needed here, just say-out-loud prep):
#  - instance method vs @classmethod vs @staticmethod — one sentence each
#  - what @dataclass generates for you (init/repr/eq) and when you'd use it
#  - __init__ vs __new__ (one allocates/returns the instance, one initializes)
#  - when NOT to write a class (a function or dict would do)
#  - what `self` actually is (explicit instance reference, no magic)


# =====================================================================
# TESTS — run the file to check yourself
# =====================================================================

def run_tests():
    tests_passed = 0
    def check(name, cond):
        nonlocal tests_passed
        if cond:
            tests_passed += 1
            print(f"  PASS {name}")
        else:
            print(f"  FAIL {name}")

    print("\n--- Part 2 tests ---")
    try:
        check("reverse_words", reverse_words("hello world foo") == "foo world hello")
    except NotImplementedError: print("  TODO reverse_words")
    try:
        check("first_non_repeating", first_non_repeating("aabbcdd") == "c"
              and first_non_repeating("aabb") is None)
    except NotImplementedError: print("  TODO first_non_repeating")
    try:
        r = two_sum([2, 7, 11, 15], 9)
        check("two_sum", r == (0, 1) and two_sum([1, 2], 100) is None)
    except NotImplementedError: print("  TODO two_sum")
    try:
        check("binary_search", binary_search([1, 3, 5, 7, 9], 7) == 3
              and binary_search([1, 3, 5], 4) == -1
              and binary_search([], 1) == -1
              and binary_search([5], 5) == 0)
    except NotImplementedError: print("  TODO binary_search")
    try:
        check("merge_sorted", merge_sorted([1, 4, 6], [2, 3, 7]) == [1, 2, 3, 4, 6, 7]
              and merge_sorted([], [1]) == [1])
    except NotImplementedError: print("  TODO merge_sorted")
    try:
        check("dedupe_keep_order", dedupe_keep_order([3, 1, 3, 2, 1]) == [3, 1, 2])
    except NotImplementedError: print("  TODO dedupe_keep_order")
    try:
        check("char_count", char_count("aab") == {"a": 2, "b": 1})
    except NotImplementedError: print("  TODO char_count")
    try:
        check("is_anagram", is_anagram("listen", "silent") and not is_anagram("ab", "abb"))
    except NotImplementedError: print("  TODO is_anagram")
    try:
        check("fibonacci", [fibonacci(i) for i in range(7)] == [0, 1, 1, 2, 3, 5, 8])
    except NotImplementedError: print("  TODO fibonacci")
    try:
        check("flatten", flatten([1, [2, [3, 4]], 5]) == [1, 2, 3, 4, 5])
    except NotImplementedError: print("  TODO flatten")
    try:
        ma = moving_average([1, 2, 3, 4, 5], 2)
        check("moving_average", ma == [1.5, 2.5, 3.5, 4.5])
    except NotImplementedError: print("  TODO moving_average")

    print("\n--- Part 3 tests ---")
    try:
        t1 = Trade("AAPL", 100, 190.5)
        t2 = Trade("AAPL", 100, 190.5)
        check("Trade.notional", t1.notional == 19050.0)
        check("Trade.__eq__", t1 == t2)
        check("Trade.__hash__", len({t1, t2}) == 1)
        check("Trade.__repr__", repr(t1) == "Trade('AAPL', 100, 190.5)")
        p = Portfolio()
        p.add(t1); p.add(Trade("MSFT", 10, 400.0))
        check("Portfolio.__len__", len(p) == 2)
        check("Portfolio.__iter__", sum(1 for _ in p) == 2)
        check("Portfolio.total_notional", p.total_notional() == 19050.0 + 4000.0)
        check("Portfolio.__contains__", "AAPL" in p and "GOOG" not in p)
    except (TypeError, AttributeError) as e:
        print(f"  TODO/FIX Part 3 ({e})")

    print(f"\n{tests_passed} checks passed.")


if __name__ == "__main__":
    print("--- Part 1: predict THEN run ---")
    gotchas()
    run_tests()
