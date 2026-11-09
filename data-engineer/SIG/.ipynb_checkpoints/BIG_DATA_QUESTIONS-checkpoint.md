# Big Data Practice — Performance Edition

**Data:** `big_trades.csv` (~2M rows, ~100 MB) and `big_reference_prices.csv`.
Or regenerate at any size: `python generate_big_data.py 5000000`.

At 500 rows every approach looks fast. At 2M+ rows, bad patterns visibly
hurt — which is exactly the "how would you optimize this?" follow-up SIG
loves. **Time everything.** In a notebook use `%%time` at the top of a cell;
in a script:

```python
import time
t0 = time.perf_counter()
...
print(f"{time.perf_counter() - t0:.2f}s")
```

---

## Part A — Feel the difference (do these first)

The goal here is visceral: run the slow way AND the fast way, time both,
and remember the ratio. Being able to say "I've measured this, apply was
~40x slower" beats any textbook answer.

1. **Notional value, three ways.** Compute `quantity * price`:
   a) `df.apply(lambda row: row['quantity'] * row['price'], axis=1)`
   b) `df['quantity'] * df['price']`
   c) `df['quantity'].to_numpy() * df['price'].to_numpy()`
   Time all three. (Warning: (a) may take a minute+. That's the point.)

2. **Conditional column, two ways.** Create `signed_qty`: quantity, negative
   for SELL:
   a) with `.apply()` row-wise
   b) with `np.where(df['side'].eq('SELL'), -df['quantity'], df['quantity'])`

3. **String ops at scale.** Uppercase `symbol`:
   a) `.apply(lambda s: s.upper() if isinstance(s, str) else s)`
   b) `.str.upper()`
   c) Bonus: convert symbol to `category` dtype first, then fix casing on
      the categories only (`.cat.rename_categories`). Why is (c) dramatically
      faster? (Hint: 20 unique values vs 2M rows.)

## Part B — Memory

4. Run `df.info(memory_usage='deep')`. Note total memory. Now:
   - convert `symbol`, `side`, `trader` to `category`
   - downcast `quantity` (`pd.to_numeric(..., downcast='integer')` after
     handling NaNs, or use nullable `Int32`)
   Re-measure. You should see a large reduction — know roughly what % you got.
5. Explain (out loud, 30 seconds): why does an object-dtype string column use
   so much more memory than a category column with 20 unique values?
6. Load `big_trades.csv` in chunks of 200k rows (`pd.read_csv(...,
   chunksize=200_000)`) and compute total notional per symbol across chunks —
   i.e. aggregate per chunk, then combine. This is the canonical
   "data bigger than RAM" pattern; practice it once so you can sketch it
   fluently.

## Part C — The real tasks, at scale

7. Full cleaning pipeline from the small kit (mixed dates, casing, dupes,
   missing values) — but now **time it end-to-end**. Mixed-format date
   parsing is often the bottleneck at this size. Try:
   a) `pd.to_datetime(col, format='mixed')`
   b) parsing the two formats separately with explicit `format=` strings and
      combining (hint: parse with one format using `errors='coerce'`, then
      `.fillna()` with the second parse)
   (b) is usually much faster — explicit formats skip per-row inference.
8. The merge with reference prices, at 2M rows. Time `merge` vs `merge_asof`
   (remember: both frames must be sorted for `merge_asof`; time the sort too
   and mention it).
9. Groupby at scale: total notional per (symbol, trader). Then the top-3
   traders per symbol two ways:
   a) `.groupby(level=0).nlargest(3)`
   b) `sort_values` + `groupby().head(3)`
   Time both.
10. `.transform('sum')` for pct-of-daily-volume (Q17 from the small kit) —
    confirm it stays fast at 2M rows, and contrast with what
    `.apply()`-based logic would cost.

## Part D — Interview soundbites to earn

After doing the above, you should be able to say, from experience:
- "Row-wise apply on 2M rows took X seconds; the vectorized version took Y
  milliseconds."
- "Converting the string columns to category cut memory by roughly Z%."
- "Explicit date formats parsed ~Nx faster than mixed-format inference."

Concrete numbers from your own runs are far more convincing than adjectives.
