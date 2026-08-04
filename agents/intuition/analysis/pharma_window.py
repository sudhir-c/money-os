"""Premarket 8/4: I documented pharma's weakness as a ONE-DAY event (8/3, PPH -1.85%).
The bars say PPH has fallen FOUR consecutive sessions off its 7/28 peak. Measure the window,
not the day. Questions:
  1. XLV beta to SPY -> is XLV's drawdown since 7/28 explained by beta, or is it real?
  2. PPH vs IHI over the same window -> how big is the pharma/devices split really?
  3. Base rate: after PPH falls 4 straight sessions, what does it do next?
     (Decision-relevant: `pharma-story-break` sits at 105.50, -2.6% below the 8/3 close.)
Lesson 3: measure the mechanism before acting on it. Lesson 5: read closes, from bars.
"""
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, "tools")
from alpaca.data.enums import Adjustment
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from common import get_env_keys

SYMS = ["SPY", "XLV", "PPH", "IHI"]

key, sec = get_env_keys()
client = StockHistoricalDataClient(key, sec)
end = datetime.now(timezone.utc) - timedelta(minutes=30)
start = end - timedelta(days=800)
bars = client.get_stock_bars(StockBarsRequest(
    symbol_or_symbols=SYMS, timeframe=TimeFrame.Day, start=start, end=end,
    adjustment=Adjustment.ALL)).data

series = {s: [(b.timestamp.date(), b.close) for b in bars[s]] for s in SYMS}
for s in SYMS:
    print(f"{s}: {len(series[s])} sessions, {series[s][0][0]} -> {series[s][-1][0]}")
print()

# ---- align on SPY's calendar (PPH has a shorter/patchier history) ----
def rets(sym):
    c = [p for _, p in series[sym]]
    return [(c[i] - c[i - 1]) / c[i - 1] for i in range(1, len(c))]


# ---- 1. XLV beta to SPY, last 252 sessions ----
xlv_d = dict(series["XLV"])
spy_d = dict(series["SPY"])
common = sorted(set(xlv_d) & set(spy_d))[-253:]
xr, sr = [], []
for i in range(1, len(common)):
    a, b = common[i - 1], common[i]
    xr.append((xlv_d[b] - xlv_d[a]) / xlv_d[a])
    sr.append((spy_d[b] - spy_d[a]) / spy_d[a])
mx, ms = sum(xr) / len(xr), sum(sr) / len(sr)
cov = sum((x - mx) * (s - ms) for x, s in zip(xr, sr)) / len(xr)
var = sum((s - ms) ** 2 for s in sr) / len(sr)
beta = cov / var
print(f"--- 1. XLV beta to SPY over {len(xr)} sessions: {beta:.3f}")

# ---- 2. the window: 7/28 peak -> 8/3 ----
def move(sym, d0, d1):
    d = dict(series[sym])
    return (d[d1] - d[d0]) / d[d0] * 100

from datetime import date
D0, D1 = date(2026, 7, 28), date(2026, 8, 3)
spy_w = move("SPY", D0, D1)
xlv_w = move("XLV", D0, D1)
pph_w = move("PPH", D0, D1)
ihi_w = move("IHI", D0, D1)
print(f"\n--- 2. window {D0} close -> {D1} close (4 sessions)")
print(f"  SPY {spy_w:+.2f}%   XLV {xlv_w:+.2f}%   PPH {pph_w:+.2f}%   IHI {ihi_w:+.2f}%")
print(f"  pharma vs devices split: {pph_w - ihi_w:+.2f} pts")
print(f"  XLV expected on beta {beta:.3f}: {beta * spy_w:+.2f}%  | actual {xlv_w:+.2f}%"
      f"  -> unexplained {xlv_w - beta * spy_w:+.2f} pts")

# ---- 3. base rate: PPH after 4 consecutive down closes ----
pph = [p for _, p in series["PPH"]]
pph_dates = [d for d, _ in series["PPH"]]
r = [(pph[i] - pph[i - 1]) / pph[i - 1] for i in range(1, len(pph))]
hits = []
for i in range(3, len(r)):
    if all(r[i - k] < 0 for k in range(4)):
        hits.append(i)  # index into r; price index i+1 is the 4th down close
print(f"\n--- 3. PPH: runs of >=4 consecutive down closes, sample {len(pph)} sessions")
print(f"  occurrences: {len(hits)}")
for horizon in (1, 3, 5, 10):
    fwd = []
    for i in hits:
        p0 = i + 1
        p1 = p0 + horizon
        if p1 < len(pph):
            fwd.append((pph[p1] - pph[p0]) / pph[p0] * 100)
    if not fwd:
        continue
    pos = sum(1 for x in fwd if x > 0)
    lo = min(fwd)
    print(f"  fwd {horizon:2d}d: n={len(fwd):3d}  avg {sum(fwd)/len(fwd):+.2f}%"
          f"  median {sorted(fwd)[len(fwd)//2]:+.2f}%  positive {pos}/{len(fwd)}"
          f"  worst {lo:+.2f}%")

# how often does a 4-down run extend far enough to travel another -2.6%?
TRIG = -2.64  # 108.36 -> 105.50
for horizon in (3, 5, 10):
    n = tot = 0
    for i in hits:
        p0 = i + 1
        seg = pph[p0 + 1:p0 + 1 + horizon]
        if len(seg) < horizon:
            continue
        tot += 1
        if min(seg) <= pph[p0] * (1 + TRIG / 100):
            n += 1
    if tot:
        print(f"  traded {TRIG:.2f}% below the 4th down close within {horizon:2d}d: "
              f"{n}/{tot} = {n/tot*100:.0f}%")

# unconditional control: same question from ANY day
for horizon in (5,):
    n = tot = 0
    for p0 in range(len(pph) - horizon - 1):
        seg = pph[p0 + 1:p0 + 1 + horizon]
        tot += 1
        if min(seg) <= pph[p0] * (1 + TRIG / 100):
            n += 1
    print(f"  CONTROL (any day): fell {TRIG:.2f}% within {horizon}d: {n}/{tot} = {n/tot*100:.0f}%")
