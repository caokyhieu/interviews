# Live Pandas Round — Practice Kit

**Setup:** You have two CSVs — `trades.csv` and `reference_prices.csv` — sitting
next to this file. Load them with pandas and work through the questions below
**in order, out loud, under time pressure.** Set a timer. Don't peek at
`SOLUTIONS.md` until you've genuinely tried each one.

Treat this like the real thing:
- Talk through your plan before typing.
- State assumptions when the data is ambiguous (it will be).
- After each answer, ask yourself: "could this be vectorized better / handle
  edge cases better?"

Suggested total time: ~50 minutes.

---

## Part 0 — First look (5 min)

1. Load both CSVs. Before doing anything else, inspect them: shape, dtypes,
   missing values, a few sample rows.
2. Without fixing anything yet, list out loud every data quality issue you can
   spot in `trades.csv`. (There are at least 5.)

---

## Part 1 — Cleaning (10 min)

3. `trade_date` has inconsistent formats (`YYYY-MM-DD` vs `DD/MM/YYYY`) and
   some missing values. Convert it to a proper datetime column, correctly
   parsing both formats. What do you do with the rows where the date is
   missing entirely?
4. `symbol` has inconsistent casing (`aapl` vs `AAPL`). Normalize it.
5. There are exact duplicate rows in `trades.csv`. Find and remove them —
   but first, explain how you'd confirm they're *true* duplicates and not
   two genuinely separate trades that happen to look identical.
6. `quantity` and `price` have missing values. Decide (and justify) whether to
   drop those rows or impute them. What would change your answer if this were
   a real trading blotter going into P&L calculations?

---

## Part 2 — Filtering (5 min)

7. Return all `SELL` trades in `NVDA` with `quantity > 1000`.
8. Return all trades NOT executed by "J. Byrne", after Feb 1 2026.
9. (Rewrite) Take whatever solution you wrote for Q7/Q8 using boolean masks
   and rewrite it with `.query()`. Which do you prefer and why?

---

## Part 3 — Joining (10 min)

10. `reference_prices.csv` has **gaps** — not every symbol has a price for
    every business day. Merge each trade with the reference `close_price` for
    that symbol on that date. What happens to trades whose date has no
    matching reference price? Try it with `how='left'` and inspect the
    result.
11. Now the harder version: instead of an exact date match, get the **most
    recent available** close price on or before the trade date (i.e. a
    stale/forward-filled price is fine, but a future price is not). This is
    the classic "as-of join" problem in trading data — think about what tool
    fits before reaching for a manual loop.
12. After your merge in Q10, compute the notional value of each trade
    (`quantity * price`, using the trade's own execution price, not the
    reference price) and compare it to `quantity * close_price`. Which trades
    deviate most from the reference price? (This is the kind of "does this
    number look right" instinct they're testing for.)

---

## Part 4 — GroupBy / Aggregation (15 min)

13. Total traded quantity per symbol.
14. Total notional value (`quantity * price`) per trader, sorted descending.
15. For each symbol, the top 3 traders by total notional value. (This is the
    "top-N per group" pattern — think `groupby` + `apply`/`nlargest`, and be
    ready to explain the performance trade-off vs a fully vectorized
    approach.)
16. Average trade size (`quantity`) per symbol **per side** (BUY vs SELL) —
    i.e. group by two keys.
17. Using `.transform()`, add a column to the trades dataframe showing each
    trade's quantity as a percentage of that symbol's total daily volume.
    (Tests: do you reach for `apply` when `transform` is the right, faster
    tool?)
18. Resample: what was the total daily notional traded, across all symbols,
    for each calendar day? (Tip: needs a datetime index or `.resample()` /
    `.groupby(pd.Grouper(...))`.)

---

## Part 5 — Curveball / debugging (5-10 min)

19. Here's a common trap: after merging trades with reference prices, someone
    reports the row count of the merged dataframe is *higher* than the
    original trades dataframe. Before looking at code — what's the most
    likely cause, and how would you check for it in one line?
20. If this dataset were 500 million rows instead of 500, what's the first
    thing in your Part 4 code you'd reconsider, and why?

---

## How to practice this well with one day left

- Do a **first full pass untimed** to make sure you know the mechanics
  (merge args, groupby+agg syntax, `.dt` accessor, `.transform`).
- Then do a **second timed pass** (50 min, no notes) narrating out loud as if
  someone's watching — this is the part people skip and it's the part that
  actually gets tested.
- Say your assumptions out loud before coding, e.g. *"I'll treat missing
  quantity as unusable for notional calcs and drop those rows, but I'd flag
  that assumption to a real trader before doing this on live data."* That
  sentence alone signals seniority.
