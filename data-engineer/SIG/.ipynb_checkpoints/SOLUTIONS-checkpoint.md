# Solutions & Talking Points

Don't just read these — retype them yourself. The goal is muscle memory plus
being able to *explain* each choice, since that's what's actually graded live.

```python
import pandas as pd
import numpy as np

trades = pd.read_csv("trades.csv")
ref = pd.read_csv("reference_prices.csv")
```

---

## Part 0 — First look

```python
trades.shape, trades.dtypes, trades.isna().sum()
trades.head()
```

Issues to spot out loud: mixed date formats, missing dates, missing
quantity/price, inconsistent symbol casing, duplicate rows, `trade_date` and
`quantity`/`price` loaded as `object`/`float` rather than clean typed columns.

**Talking point:** always run this triage before touching the data — it
signals good habits even before you're asked to fix anything.

---

## Part 1 — Cleaning

**Q3 — mixed date formats**
```python
def parse_date(s):
    return pd.to_datetime(s, errors="coerce", format="%Y-%m-%d")

trades["trade_date"] = pd.to_datetime(trades["trade_date"], format="mixed", errors="coerce")
```
`format="mixed"` (pandas 2.0+) lets pandas infer per-row format; `errors="coerce"`
turns unparseable/missing values into `NaT` instead of raising.

For missing dates: usually you can't safely impute an execution date — drop
those rows for date-dependent analysis, but say explicitly: *"I'd flag these
to the trade desk rather than silently guessing a date."*

**Q4 — casing**
```python
trades["symbol"] = trades["symbol"].str.upper()
```

**Q5 — duplicates**
```python
dupe_mask = trades.duplicated(keep=False)
trades[dupe_mask].sort_values("trade_id")
trades = trades.drop_duplicates()
```
Talking point: true duplicates should match on *every* column including
`trade_id` (or lack a trade_id entirely) — two trades with the same symbol/
qty/price but different `trade_id` are NOT duplicates, they're two real
trades. Always check the likely unique key before blindly deduping.

**Q6 — missing quantity/price**
```python
trades_clean = trades.dropna(subset=["quantity", "price"])
```
Justify: for notional/P&L calculations, imputing a price or quantity would
fabricate money that didn't trade — drop, don't guess. For a purely
descriptive stat (e.g. "average price by symbol") imputation might be more
defensible, but state the trade-off either way.

---

## Part 2 — Filtering

```python
# Q7
trades[(trades.symbol == "NVDA") & (trades.side == "SELL") & (trades.quantity > 1000)]

# Q8
trades[(trades.trader != "J. Byrne") & (trades.trade_date > "2026-02-01")]

# Q9
trades.query("symbol == 'NVDA' and side == 'SELL' and quantity > 1000")
```
`.query()` is more readable for many conditions; boolean masks are more
flexible (e.g. when conditions involve external variables/functions or when
building conditions programmatically).

---

## Part 3 — Joining

**Q10 — plain merge, exposes gaps**
```python
merged = trades_clean.merge(
    ref, left_on=["symbol", "trade_date"], right_on=["symbol", "date"], how="left"
)
merged["close_price"].isna().sum()  # trades with no matching reference price
```

**Q11 — as-of join (the "real" trading-data pattern)**
```python
t = trades_clean.sort_values("trade_date")
r = ref.assign(date=pd.to_datetime(ref["date"])).sort_values("date")

asof = pd.merge_asof(
    t, r, left_on="trade_date", right_on="date",
    by="symbol", direction="backward"  # most recent price on/before trade date
)
```
This is the single strongest "I know finance data" signal you can give —
`merge_asof` is purpose-built for exactly this and most candidates don't know
it exists, so reaching for it (or at least describing the problem correctly
even if you'd need to look up the exact function name) stands out.

**Q12 — notional deviation**
```python
merged["notional_exec"] = merged["quantity"] * merged["price"]
merged["notional_ref"] = merged["quantity"] * merged["close_price"]
merged["deviation"] = (merged["price"] - merged["close_price"]).abs()
merged.sort_values("deviation", ascending=False).head(10)
```

---

## Part 4 — GroupBy / Aggregation

```python
# Q13
trades_clean.groupby("symbol")["quantity"].sum()

# Q14
(trades_clean.assign(notional=trades_clean.quantity * trades_clean.price)
 .groupby("trader")["notional"].sum()
 .sort_values(ascending=False))

# Q15 - top 3 traders by notional per symbol
notional = trades_clean.assign(notional=trades_clean.quantity * trades_clean.price)
top3 = (notional.groupby(["symbol", "trader"])["notional"].sum()
        .groupby(level=0, group_keys=False).nlargest(3))

# Q16 - two-key groupby
trades_clean.groupby(["symbol", "side"])["quantity"].mean()

# Q17 - transform, not apply
daily_symbol_total = trades_clean.groupby(["trade_date", "symbol"])["quantity"].transform("sum")
trades_clean["pct_of_daily_volume"] = trades_clean["quantity"] / daily_symbol_total * 100

# Q18 - resample by day
daily = notional.set_index("trade_date").resample("D")["notional"].sum()
# or: notional.groupby(notional["trade_date"].dt.date)["notional"].sum()
```
On Q17 specifically: `.transform()` returns a Series the same length as the
original frame (broadcast back per-group), which is exactly what you need to
add a new column — much faster than `.apply(lambda row: ..., axis=1)`.

---

## Part 5 — Curveball / debugging

**Q19 — row count grew after a merge**
Almost always a **many-to-many join on a non-unique key** — i.e. duplicate
`(symbol, date)` pairs on one or both sides causing row multiplication.
One-liner check:
```python
ref.duplicated(subset=["symbol", "date"]).sum()
```
This is a very common real interview "gotcha" — naming it unprompted is a
strong signal.

**Q20 — scaling to 500M rows**
Talking points (say 2-3, don't ramble): `.apply(axis=1)` and Python-level
loops become unusable; prefer chunked reading or a columnar engine
(e.g. `pyarrow` backend, Polars, or Dask/Spark for out-of-core); merges on
non-indexed keys get expensive — consider setting an index or sorting before
`merge_asof`; and whether the whole dataset needs to be in memory at once.

---

## Meta note for the live round

If you get stuck, **narrate the stuck-ness** rather than going silent:
*"I know I want a per-group top-N here, I'm just blanking on whether it's
`nlargest` or `sort_values().groupby().head()` — let me try the second since
I'm sure of the syntax."* That's a completely normal, good look in a live
round. Going quiet is the only real failure mode besides not knowing pandas
at all.
