# Reshaping Practice — melt / pivot / stack / MultiIndex

**Data:** `wide_prices.csv`, `monthly_pnl.csv`, `long_positions.csv`
(regenerate anytime with `python generate_reshape_data.py`).

The mental model to keep saying out loud:
- **melt** = wide → long ("columns become rows")
- **pivot / pivot_table** = long → wide ("rows become columns")
- **stack/unstack** = the same two moves, but via the index
- **MultiIndex** = what groupby with 2+ keys hands you; know how to read,
  slice, and flatten it

---

## Part A — melt (wide → long)

`wide_prices.csv` is the classic vendor export: dates as rows, one column
per symbol.

1. Melt it into tidy long format with columns `date, symbol, price`.
   (Know the vocabulary: `id_vars`, `value_vars`, `var_name`, `value_name`.)
2. After melting, drop the rows where price is missing. Why is dropping NaNs
   *easier* in long format than in wide format? (Say the answer out loud —
   it's a classic "why tidy data" point.)
3. `monthly_pnl.csv` has TWO id columns (`trader`, `region`) and six month
   columns. Melt it to `trader, region, month, pnl`. Then convert `month`
   to a proper datetime (hint: it's `YYYY-MM`, use `pd.to_datetime(...,
   format="%Y-%m")`).
4. From the melted PnL, compute each trader's cumulative PnL over months
   (`groupby` + `cumsum`) — a task that's awkward in wide format but two
   lines in long format. Feel that difference; it's the whole argument for
   melting.

## Part B — pivot and pivot_table (long → wide)

5. Take your melted prices from Q1 and pivot them BACK to wide format
   (`index="date"`, `columns="symbol"`, `values="price"`). Confirm you
   round-tripped (same shape as the original).
6. Pivot `long_positions.csv` to a table of date × trader showing total
   position in AAPL... and watch `pivot()` **raise an error**. Why?
   (The data contains duplicate (date, trader, symbol) rows — I planted
   them.) Fix it two ways:
   a) dedupe/aggregate first, then `pivot()`
   b) use `pivot_table(aggfunc="sum")` directly
   **This is the single most common reshaping interview question:** the
   difference between `pivot` (no duplicates allowed, pure reshape) and
   `pivot_table` (aggregates duplicates, essentially groupby + reshape).
7. Build a pivot_table from `long_positions.csv`: rows = trader,
   columns = symbol, values = mean absolute position
   (hint: create an `abs_pos` column first, or pass a custom aggfunc).
   Add `margins=True` and explain what the "All" row/column means.
8. `pd.crosstab(long.trader, long.symbol)` — what does it show, and how is
   it just a special case of pivot_table?

## Part C — stack / unstack

9. Set `["date", "symbol"]` as the index of your long prices, then
   `.unstack("symbol")`. Compare with the pivot from Q5 — same result,
   different route. When would you use unstack instead of pivot?
   (Typical answer: when the data is *already* MultiIndexed, e.g. straight
   out of a groupby.)
10. Take the wide prices (dates × symbols), set `date` as index, and
    `.stack()`. What did you get back? (long format as a Series) —
    stack is melt's index-based cousin.
11. The money pattern — groupby straight into a matrix:
    `long_positions.groupby(["trader", "symbol"])["position"].sum().unstack()`
    One line from tidy data to a trader × symbol matrix, with NaN where a
    trader never touched a symbol. Then `.unstack(fill_value=0)` to control
    the holes.

## Part D — MultiIndex survival kit

Build: `g = long.groupby(["date", "trader", "symbol"])["position"].sum()`
(a 3-level MultiIndexed Series). Now, without googling:

12. Select everything for one date: `g.loc["2026-01-02"]`.
13. Select one exact cell: `g.loc[("2026-01-02", "trader_06", "GOOG")]`.
14. Select ALL dates for one trader — the awkward middle-level selection.
    Two idioms to know:
    a) `g.xs("trader_06", level="trader")`
    b) `idx = pd.IndexSlice; g.loc[idx[:, "trader_06", :]]`
15. `swaplevel` + `sort_index` to reorder levels so trader comes first.
    Why does pandas warn about performance if you slice an unsorted
    MultiIndex? (lexsorted index → binary search; unsorted → scan.)
16. Flatten it all back: `.reset_index()` — and know that this is usually
    the right move before merging or exporting. Also know
    `groupby(..., as_index=False)` to avoid the MultiIndex from the start.
17. Columns can be MultiIndexed too:
    `agg = long.groupby("trader").agg({"position": ["sum", "mean", "count"]})`
    gives two-level columns. Flatten them:
    `agg.columns = ["_".join(c) for c in agg.columns]`
    — memorize this one-liner; interviewers love asking how to clean up
    post-agg column names. (Alternative: named aggregation,
    `.agg(pos_sum=("position","sum"))`, avoids the problem entirely.)

---

## The three soundbites to walk away with

- "**pivot is a pure reshape and errors on duplicate keys; pivot_table is
  groupby + reshape** — it aggregates duplicates, so it always works but you
  must choose the aggfunc consciously."
- "**melt to long for computation, pivot to wide for humans** — groupby,
  cumsum, merges all want long data; reports and heatmaps want wide."
- "**groupby with multiple keys returns a MultiIndex; `.unstack()` turns the
  inner level into columns, `.reset_index()` flattens everything** — those
  two moves cover 90% of MultiIndex handling."
