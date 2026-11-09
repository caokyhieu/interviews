# Reshaping Solutions

```python
import pandas as pd
import numpy as np

wide = pd.read_csv("wide_prices.csv")
pnl = pd.read_csv("monthly_pnl.csv")
long = pd.read_csv("long_positions.csv")
```

## Part A — melt

```python
# Q1
prices = wide.melt(id_vars="date", var_name="symbol", value_name="price")

# Q2
prices = prices.dropna(subset=["price"])
```
Q2 talking point: in long format a missing price is one *row* you can drop
without touching anything else; in wide format it's a *hole in a matrix* —
dropping the row would discard four valid prices from other symbols.

```python
# Q3
pnl_long = pnl.melt(
    id_vars=["trader", "region"], var_name="month", value_name="pnl"
)
pnl_long["month"] = pd.to_datetime(pnl_long["month"], format="%Y-%m")

# Q4
pnl_long = pnl_long.sort_values(["trader", "month"])
pnl_long["cum_pnl"] = pnl_long.groupby("trader")["pnl"].cumsum()
```
(Note the sort before cumsum — cumulative ops depend on row order.)

## Part B — pivot / pivot_table

```python
# Q5 — round trip
wide_again = prices.pivot(index="date", columns="symbol", values="price")

# Q6 — pivot() raises ValueError: Index contains duplicate entries
aapl = long[long.symbol == "AAPL"]
# aapl.pivot(index="date", columns="trader", values="position")  # BOOM

# fix (a): aggregate away the duplicates first
dedup = aapl.groupby(["date", "trader"], as_index=False)["position"].sum()
p1 = dedup.pivot(index="date", columns="trader", values="position")

# fix (b): pivot_table aggregates for you
p2 = aapl.pivot_table(index="date", columns="trader",
                      values="position", aggfunc="sum")
```
The line to say: "pivot is a pure reshape — one value per (index, column)
cell or it errors. pivot_table is groupby+reshape — duplicates get
aggregated, so I must consciously pick the aggfunc; the default is mean,
which silently averages things if I'm not paying attention." That last
clause (default=mean, silent) is the depth signal.

```python
# Q7
long["abs_pos"] = long["position"].abs()
pt = long.pivot_table(index="trader", columns="symbol",
                      values="abs_pos", aggfunc="mean", margins=True)
```
`margins=True` adds an "All" row/column = the aggregation over everything
(row-wise / column-wise means here).

```python
# Q8
pd.crosstab(long.trader, long.symbol)
```
Crosstab counts co-occurrences — equivalent to
`pivot_table(aggfunc="count")` / `size`. Special-purpose shortcut.

## Part C — stack / unstack

```python
# Q9
p3 = prices.set_index(["date", "symbol"])["price"].unstack("symbol")

# Q10
s = wide.set_index("date").stack()          # long Series, (date, symbol) index

# Q11 — the money pattern
matrix = (long.groupby(["trader", "symbol"])["position"]
              .sum().unstack(fill_value=0))
```

## Part D — MultiIndex

```python
g = long.groupby(["date", "trader", "symbol"])["position"].sum()

g.loc["2026-01-02"]                              # Q12
g.loc[("2026-01-02", "trader_06", "GOOG")]       # Q13

# Q14
g.xs("trader_06", level="trader")
idx = pd.IndexSlice
g.loc[idx[:, "trader_06", :]]

# Q15
g2 = g.swaplevel("date", "trader").sort_index()
```
Q15 talking point: a sorted (lexsorted) MultiIndex allows binary-search
slicing; unsorted forces a full scan, hence the PerformanceWarning.

```python
# Q16
flat = g.reset_index()
# or avoid it upfront:
long.groupby(["date", "trader", "symbol"], as_index=False)["position"].sum()

# Q17
agg = long.groupby("trader").agg({"position": ["sum", "mean", "count"]})
agg.columns = ["_".join(c) for c in agg.columns]
# cleaner alternative — named aggregation:
agg2 = long.groupby("trader").agg(
    pos_sum=("position", "sum"),
    pos_mean=("position", "mean"),
    n_trades=("position", "count"),
)
```
If you only memorize one thing from Part D, make it named aggregation
(`agg2`) — it sidesteps MultiIndex columns entirely and reads beautifully
in a live interview.
