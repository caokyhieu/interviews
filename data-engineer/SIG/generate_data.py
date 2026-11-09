"""
Generates two messy, realistic CSVs mimicking a trading/research context:
  - trades.csv        : individual trade records (messy: missing values, mixed
                         date formats, duplicate rows, inconsistent casing)
  - reference_prices.csv : daily reference/closing prices per symbol (has gaps
                         in the date range, i.e. missing trading days)

Run this once to (re)generate the data. Seeded, so it's reproducible.
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)

symbols = ["AAPL", "MSFT", "GOOG", "AMZN", "NVDA"]
traders = ["J. Byrne", "A. Kowalski", "S. Rao", "M. Chen", "L. O'Sullivan"]
sides = ["BUY", "SELL"]

n = 500
dates = pd.date_range("2026-01-02", "2026-03-31", freq="B")  # business days

rows = []
for i in range(n):
    d = rng.choice(dates)
    sym = rng.choice(symbols)
    side = rng.choice(sides)
    qty = int(rng.integers(10, 5000))
    price = round(float(rng.normal({"AAPL":190,"MSFT":410,"GOOG":175,"AMZN":195,"NVDA":135}[sym], 5)), 2)
    trader = rng.choice(traders)

    # introduce messiness
    date_str = pd.Timestamp(d).strftime("%Y-%m-%d")
    if rng.random() < 0.15:
        date_str = pd.Timestamp(d).strftime("%d/%m/%Y")  # inconsistent format
    if rng.random() < 0.08:
        date_str = None  # missing date

    if rng.random() < 0.05:
        qty = None  # missing quantity

    if rng.random() < 0.05:
        price = None  # missing price

    if rng.random() < 0.1:
        sym = sym.lower()  # inconsistent casing

    rows.append({
        "trade_id": f"T{1000+i}",
        "trade_date": date_str,
        "symbol": sym,
        "side": side,
        "quantity": qty,
        "price": price,
        "trader": trader,
    })

trades = pd.DataFrame(rows)

# inject some exact duplicate rows (common real-world issue)
dupes = trades.sample(12, random_state=1)
trades = pd.concat([trades, dupes], ignore_index=True)
trades = trades.sample(frac=1, random_state=7).reset_index(drop=True)  # shuffle

trades.to_csv("trades.csv", index=False)

# --- reference prices, with GAPS in the date range (missing trading days) ---
ref_rows = []
for sym in symbols:
    base = {"AAPL":190,"MSFT":410,"GOOG":175,"AMZN":195,"NVDA":135}[sym]
    walk = base
    for d in dates:
        walk += float(rng.normal(0, 1.2))
        # randomly drop ~10% of days per symbol to create gaps
        if rng.random() < 0.10:
            continue
        ref_rows.append({"date": d.strftime("%Y-%m-%d"), "symbol": sym, "close_price": round(walk, 2)})

ref = pd.DataFrame(ref_rows)
ref.to_csv("reference_prices.csv", index=False)

print("Wrote trades.csv:", trades.shape)
print("Wrote reference_prices.csv:", ref.shape)
