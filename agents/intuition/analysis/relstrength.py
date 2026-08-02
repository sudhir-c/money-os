#!/usr/bin/env python3
"""Saturday deep-work scratchpad (intuition agent).

Questions I want my own data on, not someone's summary:
  1. Is "equal weight beats cap weight" a durable regime or a 3-month blip?
  2. Are my three holdings actually diversified, or one macro bet wearing three hats?
  3. Does XLE hedge my book, or just add beta?
  4. What does my book do on days long yields rise? (TLT down = yields up proxy)
All returns computed from split/dividend-ADJUSTED bars (Adjustment.ALL).
"""
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, "tools")

from alpaca.data.enums import Adjustment
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

from common import get_env_keys

SYMS = ["SPY", "RSP", "XLF", "XLV", "XLE", "XLY", "XLK", "TLT", "IWM", "XLP"]

key, sec = get_env_keys()
client = StockHistoricalDataClient(key, sec)
end = datetime.now(timezone.utc) - timedelta(minutes=30)  # free tier: no recent SIP
start = end - timedelta(days=900)
bars = client.get_stock_bars(
    StockBarsRequest(
        symbol_or_symbols=SYMS,
        timeframe=TimeFrame.Day,
        start=start,
        end=end,
        adjustment=Adjustment.ALL,
    )
).data

closes = {s: [b.close for b in bars[s]] for s in SYMS if s in bars}
dates = {s: [b.timestamp.date() for b in bars[s]] for s in SYMS if s in bars}
n = min(len(v) for v in closes.values())
closes = {s: v[-n:] for s, v in closes.items()}
d = dates["SPY"][-n:]
print(f"bars: {n} sessions, {d[0]} -> {d[-1]}\n")


def ret(s, back):
    c = closes[s]
    return (c[-1] / c[-1 - back] - 1) * 100


print("=== Q1: RSP vs SPY, rolling 63-session (3mo) relative return, stepped back ===")
print("  (positive = equal-weight winning; I want to see how long this has been true)")
hdr = "offset(sessions ago)".ljust(22) + "".join(f"{x:>9}" for x in [0, 21, 42, 63, 126, 189, 252, 378, 504])
print(hdr)
row = "RSP-SPY 63d rel %".ljust(22)
for off in [0, 21, 42, 63, 126, 189, 252, 378, 504]:
    a, b = closes["RSP"], closes["SPY"]
    i = len(a) - 1 - off
    r = (a[i] / a[i - 63] - 1) - (b[i] / b[i - 63] - 1)
    row += f"{r*100:>9.2f}"
print(row)

print("\n=== Q2/Q3/Q4: daily-return correlations, last 63 sessions ===")


def dr(s, k=63):
    c = closes[s]
    return [(c[i] / c[i - 1] - 1) for i in range(len(c) - k, len(c))]


def corr(x, y):
    mx, my = sum(x) / len(x), sum(y) / len(y)
    cov = sum((a - mx) * (b - my) for a, b in zip(x, y))
    vx = sum((a - mx) ** 2 for a in x) ** 0.5
    vy = sum((b - my) ** 2 for b in y) ** 0.5
    return cov / (vx * vy)


use = ["SPY", "RSP", "XLF", "XLV", "XLE", "XLK", "TLT", "IWM"]
print("      " + "".join(f"{s:>7}" for s in use))
for a in use:
    print(f"{a:>5} " + "".join(f"{corr(dr(a), dr(b)):>7.2f}" for b in use))

print("\n=== Q4: conditional behaviour on rising-long-yield days (TLT down >0.4%) ===")
tlt = dr("TLT", 252)
idx = [i for i, r in enumerate(tlt) if r < -0.004]
print(f"  {len(idx)} such days in the last 252 sessions")
for s in ["SPY", "RSP", "XLF", "XLV", "XLE", "XLK", "IWM"]:
    rs = dr(s, 252)
    avg = sum(rs[i] for i in idx) / len(idx) * 100
    allavg = sum(rs) / len(rs) * 100
    print(f"  {s:>4}: avg {avg:+.3f}% on yield-up days vs {allavg:+.3f}% unconditional"
          f"  -> spread {avg-allavg:+.3f}%")

print("\n=== My book vs alternatives: realized vol and drawdown, last 126 sessions ===")
BOOK = {"XLF": 1138.80, "RSP": 1075.05, "XLV": 812.75}
tot = sum(BOOK.values())
w = {k: v / tot for k, v in BOOK.items()}
print(f"  weights (of invested $3,026.60): " + ", ".join(f"{k} {v:.1%}" for k, v in w.items()))
k = 126
book_r = [sum(w[s] * dr(s, k)[i] for s in BOOK) for i in range(k)]
for name, series in [("BOOK(invested)", book_r), ("SPY", dr("SPY", k)), ("RSP", dr("RSP", k))]:
    mu = sum(series) / len(series)
    sd = (sum((r - mu) ** 2 for r in series) / (len(series) - 1)) ** 0.5
    cum, peak, mdd = 1.0, 1.0, 0.0
    for r in series:
        cum *= 1 + r
        peak = max(peak, cum)
        mdd = min(mdd, cum / peak - 1)
    print(f"  {name:>14}: ann.vol {sd*252**0.5*100:5.1f}%  126d ret {(cum-1)*100:+6.2f}%"
          f"  maxDD {mdd*100:6.2f}%  ret/vol {(cum-1)/(sd*252**0.5):+.2f}")

print("\n=== trailing returns table (adjusted) ===")
print("sym   " + "".join(f"{lbl:>9}" for lbl in ["1mo", "3mo", "6mo", "12mo"]))
for s in use + ["XLY", "XLP"]:
    print(f"{s:>5} " + "".join(f"{ret(s, b):>8.2f}%" for b in [21, 63, 126, 252]))
