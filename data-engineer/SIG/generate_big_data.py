"""
Big-data generator for performance practice.

Usage:
    python generate_big_data.py            # default: 2,000,000 trades
    python generate_big_data.py 5000000    # custom row count

Outputs:
    big_trades.csv          - large messy trade blotter
    big_reference_prices.csv - per-symbol daily closes (with gaps)

Scale guide (approx): 2M rows ≈ 130 MB CSV, generates in ~30-60s.
Run locally with any size your machine handles.
"""
import sys
import numpy as np
import pandas as pd

N = int(sys.argv[1]) if len(sys.argv) > 1 else 2_000_000
rng = np.random.default_rng(42)

symbols = np.array([
    "AAPL","MSFT","GOOG","AMZN","NVDA","META","TSLA","JPM","XOM","UNH",
    "V","MA","HD","PG","KO","PEP","ORCL","CRM","AMD","INTC",
])
base_prices = rng.uniform(50, 500, size=len(symbols)).round(2)
traders = np.array([f"trader_{i:03d}" for i in range(150)])
dates = pd.date_range("2024-01-02", "2026-06-30", freq="B")

print(f"Generating {N:,} trades (vectorized)...")

sym_idx = rng.integers(0, len(symbols), N)
date_idx = rng.integers(0, len(dates), N)

df = pd.DataFrame({
    "trade_id": np.arange(N),
    "trade_date": dates.to_numpy()[date_idx],
    "symbol": symbols[sym_idx],
    "side": rng.choice(["BUY", "SELL"], N),
    "quantity": rng.integers(1, 10_000, N).astype("float64"),
    "price": (base_prices[sym_idx] * rng.normal(1, 0.03, N)).round(2),
    "trader": traders[rng.integers(0, len(traders), N)],
})

# --- inject realistic messiness, vectorized ---
# ~3% missing quantity, ~3% missing price
df.loc[rng.random(N) < 0.03, "quantity"] = np.nan
df.loc[rng.random(N) < 0.03, "price"] = np.nan

# ~8% lowercase symbols
lower_mask = rng.random(N) < 0.08
df.loc[lower_mask, "symbol"] = df.loc[lower_mask, "symbol"].str.lower()

# mixed date formats: store as string, ~12% in DD/MM/YYYY
date_str = pd.Series(df["trade_date"]).dt.strftime("%Y-%m-%d")
alt_mask = rng.random(N) < 0.12
date_str[alt_mask] = pd.Series(df["trade_date"]).dt.strftime("%d/%m/%Y")[alt_mask]
df["trade_date"] = date_str
# ~1% missing dates
df.loc[rng.random(N) < 0.01, "trade_date"] = np.nan

# duplicate ~0.5% of rows
dupes = df.sample(frac=0.005, random_state=1)
df = pd.concat([df, dupes], ignore_index=True)
df = df.sample(frac=1, random_state=7).reset_index(drop=True)

df.to_csv("big_trades.csv", index=False)
print(f"Wrote big_trades.csv: {df.shape}")

# --- reference prices with gaps ---
print("Generating reference prices...")
ref_frames = []
for i, sym in enumerate(symbols):
    walk = base_prices[i] + np.cumsum(rng.normal(0, base_prices[i] * 0.005, len(dates)))
    keep = rng.random(len(dates)) > 0.10  # ~10% missing days per symbol
    ref_frames.append(pd.DataFrame({
        "date": dates[keep].strftime("%Y-%m-%d"),
        "symbol": sym,
        "close_price": walk[keep].round(2),
    }))
ref = pd.concat(ref_frames, ignore_index=True)
ref.to_csv("big_reference_prices.csv", index=False)
print(f"Wrote big_reference_prices.csv: {ref.shape}")
