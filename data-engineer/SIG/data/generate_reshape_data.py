"""
Generates data for reshaping practice (melt / pivot / stack / MultiIndex):

  wide_prices.csv   - dates as rows, one COLUMN PER SYMBOL (classic wide
                      format, as exported by many market-data vendors)
  monthly_pnl.csv   - wide "report-style" table: trader rows, one column
                      per month, plus a region column
  long_positions.csv - long/tidy format: (date, trader, symbol, position),
                      ready to be pivoted the other way

Run: python generate_reshape_data.py
"""
import numpy as np
import pandas as pd

rng = np.random.default_rng(11)

symbols = ["AAPL", "MSFT", "GOOG", "AMZN", "NVDA"]
dates = pd.date_range("2026-01-02", "2026-03-31", freq="B")

# --- 1. wide prices: one column per symbol ---
base = {"AAPL": 190, "MSFT": 410, "GOOG": 175, "AMZN": 195, "NVDA": 135}
wide = pd.DataFrame({"date": dates.strftime("%Y-%m-%d")})
for s in symbols:
    walk = base[s] + np.cumsum(rng.normal(0, 1.5, len(dates)))
    walk[rng.random(len(dates)) < 0.05] = np.nan  # some missing prices
    wide[s] = walk.round(2)
wide.to_csv("wide_prices.csv", index=False)

# --- 2. monthly pnl report: trader rows, month columns ---
traders = [f"trader_{i:02d}" for i in range(12)]
regions = rng.choice(["EU", "US", "APAC"], len(traders))
months = ["2026-01", "2026-02", "2026-03", "2026-04", "2026-05", "2026-06"]
pnl = pd.DataFrame({"trader": traders, "region": regions})
for m in months:
    pnl[m] = (rng.normal(50_000, 40_000, len(traders))).round(0)
pnl.loc[rng.random(len(traders)) < 0.2, months[-1]] = np.nan  # month not closed yet
pnl.to_csv("monthly_pnl.csv", index=False)

# --- 3. long/tidy positions ---
rows = []
for d in dates[::5]:  # weekly-ish snapshots
    for t in rng.choice(traders, 6, replace=False):
        for s in rng.choice(symbols, 3, replace=False):
            rows.append({
                "date": d.strftime("%Y-%m-%d"),
                "trader": t,
                "symbol": s,
                "position": int(rng.integers(-5000, 5000)),
            })
long_pos = pd.DataFrame(rows)
# inject a duplicate (same date/trader/symbol twice) - pivot() will choke on it
long_pos = pd.concat([long_pos, long_pos.sample(3, random_state=2)], ignore_index=True)
long_pos.to_csv("long_positions.csv", index=False)

print("Wrote wide_prices.csv:", wide.shape)
print("Wrote monthly_pnl.csv:", pnl.shape)
print("Wrote long_positions.csv:", long_pos.shape)
