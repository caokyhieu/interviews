# R2 Concept Sheet — Python Depth, Spoken Answers

Same format as before: each answer written the way you'd say it in 30-60s.
The exercises file (r2_exercises.py) is the doing; this is the explaining.
Interviewers at this level alternate: "make it work" → "now explain why."

---

## Data types & the object model

**"What's the difference between a list and a tuple?"**
Mutability is the surface answer; go one level deeper: "Lists are mutable,
tuples immutable — which means tuples are hashable (if their contents are)
and can be dict keys or set members; lists can't. Tuples also signal intent:
fixed-shape record vs growable collection. Memory-wise tuples are slightly
lighter and lists over-allocate to make repeated append amortized O(1)."

**"Why must dict keys be hashable? How does a dict work?"**
"A dict is a hash table: it computes hash(key) to pick a slot, giving
average O(1) lookup/insert. That requires the key's hash to never change —
which is why keys must be immutable/hashable. If a key could mutate after
insertion, its hash would change and the dict could never find it again.
Collisions are handled internally (open addressing); worst case degrades
toward O(n) but that's pathological."

**"is vs == ?"**
"`==` asks equal value (calls __eq__); `is` asks same object in memory
(identity). Use `is` only for None/True/False singletons. Gotcha: small
ints and some strings are interned so `is` may *appear* to work — never
rely on it."

**"How does assignment work in Python?"** (the aliasing question)
"Variables are references to objects, not boxes containing values.
`b = a` makes both names point at the same object — mutate through one,
the other sees it. That's why we need copy vs deepcopy, and it's the root
cause of the mutable-default-argument bug and the `[[0]*3]*3` trap."

**"Mutable default argument — explain the bug."**
"Default values are evaluated ONCE, at function definition, and stored on
the function object. So `def f(x, acc=[])` shares one list across all
calls. Fix: default to None, create the list inside. This is probably the
#1 Python interview gotcha — know it cold."

## Functions

**"What's a closure?"**
"A function that captures variables from its enclosing scope — the inner
function keeps a reference to them after the outer function returns.
Gotcha: it captures the *variable*, not its value at definition time —
late binding — which is why `[lambda: i for i in range(3)]` all return 2.
Fix: `lambda i=i: i` (default binds now) or functools.partial."

**"*args / **kwargs?"**
"*args collects extra positional arguments into a tuple, **kwargs collects
extra keyword arguments into a dict. Same syntax in reverse unpacks:
f(*mylist, **mydict). Essential for decorators — the wrapper must accept
anything: def wrapper(*args, **kwargs)."

**"Generators?"** (you have this from the first cheat sheet — one upgrade:)
Add: "`yield` makes a function return a generator object; execution pauses
at each yield and resumes on next(). `yield from` delegates to a
sub-generator — handy in recursive generators like flattening."

**"Scoping rules?"**
"LEGB — Local, Enclosing, Global, Builtin, searched in that order.
Assignment inside a function makes a name local for the WHOLE function
(hence UnboundLocalError if you read before assigning). `nonlocal` writes
to the enclosing scope, `global` to module scope — both are usually a
design smell outside decorators/closures."

## Classes

**"Instance vs class vs static method?"**
"Instance methods take self and act on one object. Classmethods take cls —
typical use: alternative constructors like Trade.from_csv_row(). Static
methods take neither — just a function namespaced inside the class for
organization."

**"What does @dataclass give you?"**
"Auto-generated __init__, __repr__, __eq__ from the field declarations;
opt into ordering with order=True, immutability + hashing with
frozen=True. Use it for data-carrying classes — like a Trade record — and
write dunders by hand only when you need custom behavior."

**"__eq__ / __hash__ contract?"**
"If a == b then hash(a) must equal hash(b). Defining __eq__ without
__hash__ sets hash to None — instances become unhashable, can't go in
sets/dicts. Standard fix: hash a tuple of the same fields __eq__
compares. And only hash immutable state."

**"__init__ vs __new__?"**
"__new__ allocates and returns the instance (rarely overridden — think
singletons or subclassing immutables like int/str); __init__ initializes
the already-created instance and returns None. 99% of the time you only
touch __init__."

**"super()?"**
"Calls the next class in Method Resolution Order — not simply 'the
parent'. With single inheritance that's the parent; with multiple
inheritance the MRO (C3 linearization) defines a deterministic order —
inspect it with ClassName.__mro__. Cooperative super().__init__() calls
keep diamond hierarchies sane."

**"When would you NOT use a class?"**
Great question to answer confidently: "When there's no state to bundle
with behavior — a module of functions is simpler. A class with only
__init__ and one method is usually just a function in disguise. In data
work most logic is pipeline functions over dataframes; classes earn their
keep for things like a connection manager or a domain object with
invariants."

## Memory management & garbage collection
(direct question from the prep guide — learn this one as a set piece)

**"How does Python manage memory? What does the GC do?"**
"CPython's primary mechanism is **reference counting**: every object
carries a count of references pointing at it; the count hits zero, the
object is freed immediately and deterministically. sys.getrefcount() shows
it. But refcounting alone can't free **reference cycles** — two objects
pointing at each other never reach zero. That's what the **cyclic garbage
collector** is for: a generational collector (three generations, on the
theory that most objects die young) that periodically finds and breaks
unreachable cycles. So: refcounting does the everyday work instantly; the
GC is the backstop for cycles. The gc module lets you inspect or disable
it — some low-latency systems disable cyclic GC during hot paths to avoid
pause spikes, which is a relevant detail in a trading context."

Follow-ups they might chain:
- **"What creates a reference?"** — assignment, container membership,
  function arguments, closures. `del x` removes a *name*, not necessarily
  the object.
- **"How does this connect to the GIL?"** — refcount updates aren't
  thread-safe on their own; the GIL is largely what protects them. (Nice
  link back to the GIL answer — interviewers love when you connect the
  two.)
- **"Why do NumPy/Pandas matter here?"** — a 2M-row object column is 2M
  refcounted Python objects; a float64 column is ONE object wrapping a raw
  C buffer. That's the memory-management story behind everything you
  measured in the big-data exercises — dtype work isn't just speed, it's
  taking data OUT of Python's object machinery.
- **"weakref?"** — a reference that doesn't increment the count; used for
  caches that shouldn't keep objects alive. Name-drop only.

## OOP design patterns (official doc topic — conversational depth, not code)

Don't memorize the Gang of Four. Know 4-5 patterns at say-and-sketch level,
each with a one-liner and a Python-flavored note:

- **Singleton** — one shared instance (config, connection pool). Pythonic
  take: "usually a module-level object does the job — modules are natural
  singletons." Saying that shows judgment, not just pattern trivia.
- **Factory** — a function/classmethod that decides which class to build.
  You already know the Python idiom: alternative constructors like
  `Trade.from_csv_row()` ARE factory methods.
- **Strategy** — swap behavior by passing it in. In Python: just pass a
  function (first-class functions replace the class ceremony) — e.g.
  passing an aggfunc into pivot_table is strategy in the wild.
- **Observer** — subscribers get notified on events; the pub/sub idea
  behind market-data feeds — natural to mention in a trading context.
- **Decorator (pattern)** — wrap an object to add behavior; note it's the
  same *idea* as Python's @decorators applied at function level.

The winning meta-answer if asked broadly: "Python's first-class functions
and duck typing make several classic patterns lighter or unnecessary —
strategy becomes passing a function, singleton becomes a module. I reach
for patterns as vocabulary for design conversations more than as
templates." That's an experienced-engineer answer.

## Concurrency (beyond the GIL one-liner)

The GIL answer (cheat sheet §7) is your opener. Depth they may push into:

**"Threads vs processes vs asyncio — when each?"**
"Threads: I/O-bound work — downloads, DB calls, API requests — the GIL
releases during waits. Processes: CPU-bound pure-Python work — real
parallelism, cost is serialization/IPC overhead. Asyncio: high-volume
I/O concurrency in one thread via an event loop — thousands of
connections without thread overhead, but the whole call chain must be
async-aware. Practical default: concurrent.futures ThreadPoolExecutor /
ProcessPoolExecutor — same API, easy to switch."

**"What's a race condition? How do you prevent one?"**
"Two threads read-modify-write shared state and interleave —
counter += 1 is read, add, write: two threads can both read 5 and both
write 6, losing an increment. Fix: a Lock around the critical section
(`with lock:`), or avoid shared mutable state entirely — queue.Queue for
passing work between threads is the idiomatic Python answer."

**"Deadlock?"**
"Two threads each hold a lock the other needs — nobody proceeds. Classic
avoidance: always acquire multiple locks in a consistent global order, or
use timeouts."

Trading-context flourish if it fits: "in latency-sensitive systems you
also think about GC pauses and avoiding allocation in hot paths" — links
back to the memory-management answer.

## Complexity — the vocabulary layer over Part 2

Know cold, for the structures you actually use:
- list: index O(1), append amortized O(1), insert/delete at front O(n),
  membership `x in list` O(n)
- dict/set: lookup/insert/delete average O(1)
- sorting: O(n log n) — Python's sort is Timsort, stable, and it's why
  "sort then scan" O(n log n) sometimes beats "dict" O(n) in practice for
  small n (constants!) — saying that earns points
- string concatenation in a loop: O(n²) — build a list and ''.join it

The move that wins the room: after ANY solution, unprompted, state its
time and space complexity in one sentence. Make it a reflex this week.

---

## How to drill with the time you have

1. Part 1 of r2_exercises.py FIRST: write predictions as comments, run,
   score yourself. Each miss = a concept to read up on same day.
2. Parts 2-3 over two or three sittings, in a plain editor, no
   autocomplete, tests as your feedback loop. Re-do from scratch any you
   needed help on — from-scratch-twice is the retention trick.
3. Read this sheet out loud once, then have someone (or me) fire the
   quoted questions at you randomly.
4. When Marcus's document arrives → send it over and we re-prioritize.
