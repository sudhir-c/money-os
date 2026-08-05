"""Morning 8/4. Two questions I own real money on and have never measured.

Q1 (lesson 3 — measure the mechanism BEFORE sizing, and I sized first):
    I bought XLV as "my one uncorrelated defensive leg." Does it actually DEFEND?
    Test: XLV's behaviour on SPY's worst days. If XLV's whole value is insurance,
    it has to pay on the days the insurance is for. If it doesn't, I own a 16%
    position for a job it does not do, and the 5-session drag is not "the premium."

Q2: My RSP leg is a bet on BREADTH. Over 7/28 -> 8/4 RSP is -0.03% while SPY is
    +3.21%. How unusual is a 5-day RSP-minus-SPY gap that wide, and what has
    historically FOLLOWED it? (Does narrow leadership mean-revert toward breadth,
    or does the equal-weight keep losing?)

All figures from force-adjusted Alpaca daily bars. Free-tier feed needs an end
timestamp ~30 min in the past; today's forming bar is therefore excluded from the
historical sample and quoted separately from live quotes in the journal.
"""
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, "tools")
from alpaca.data.enums import Adjustment
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from common import get_env_keys

SYMS = ["SPY", "RSP", "XLF", "XLV", "PPH", "IHI"]

key, sec = get_env_keys()
client = StockHistoricalDataClient(key, sec)
end = datetime.now(timezone.utc) - timedelta(minutes=30)
start = end - timedelta(days=1100)
bars = client.get_stock_bars(StockBarsRequest(
    symbol_or_symbols=SYMS, timeframe=TimeFrame.Day, start=start, end=end,
    adjustment=Adjustment.ALL)).data

series = {s: {b.timestamp.date(): b.close for b in bars[s]} for s in SYMS}
common = sorted(set.intersection(*(set(v) for v in series.values())))
print(f"common sample: {common[0]} -> {common[-1]}  ({len(common)} sessions)\n")

C = {s: [series[s][d] for d in common] for s in SYMS}


def rets(s, sample=None):
    c = C[s]
    r = [(c[i] / c[i - 1] - 1) * 100 for i in range(1, len(c))]
    return r if sample is None else r[-sample:]


# ---------------------------------------------------------------- Q1: defence
print("=" * 68)
print("Q1. Does XLV defend on the days defence is for?")
print("=" * 68)

spy = rets("SPY")
xlv = rets("XLV")
rsp = rets("RSP")
xlf = rets("XLF")
N = len(spy)

for label, lo, hi in [
    ("SPY worst decile", None, sorted(spy)[N // 10]),
    ("SPY down > 1.0%", None, -1.0),
    ("SPY down day (any)", None, 0.0),
    ("SPY up day (any)", 0.0, None),
]:
    idx = [i for i in range(N)
           if (lo is None or spy[i] > lo) and (hi is None or spy[i] < hi)]
    if not idx:
        continue
    n = len(idx)
    m = lambda r: sum(r[i] for i in idx) / n
    print(f"{label:<20} n={n:>4}   SPY {m(spy):+.3f}%   "
          f"XLV {m(xlv):+.3f}%   RSP {m(rsp):+.3f}%   XLF {m(xlf):+.3f}%")

# The sharper question: on SPY's worst days, how often does XLV finish ABOVE SPY,
# and how often is it outright POSITIVE (the thing a true hedge does)?
thr = sorted(spy)[N // 10]
worst = [i for i in range(N) if spy[i] < thr]
beat = sum(1 for i in worst if xlv[i] > spy[i])
pos = sum(1 for i in worst if xlv[i] > 0)
print(f"\non SPY's worst decile (n={len(worst)}, SPY avg {sum(spy[i] for i in worst)/len(worst):+.2f}%):")
print(f"  XLV beat SPY   {beat}/{len(worst)} = {100*beat/len(worst):.0f}%")
print(f"  XLV POSITIVE   {pos}/{len(worst)} = {100*pos/len(worst):.0f}%")

# Trailing-window stability: is the defence a stable property or one regime?
for win in (252, 504, N):
    s2, x2 = spy[-win:], xlv[-win:]
    n2 = len(s2)
    t = sorted(s2)[n2 // 10]
    w = [i for i in range(n2) if s2[i] < t]
    print(f"  window {win:>4}: SPY worst-decile avg {sum(s2[i] for i in w)/len(w):+.2f}% "
          f"-> XLV {sum(x2[i] for i in w)/len(w):+.2f}%  "
          f"(protection {sum(s2[i] for i in w)/len(w) - sum(x2[i] for i in w)/len(w):+.2f} pts)")

# ------------------------------------------------------------- Q2: breadth gap
print("\n" + "=" * 68)
print("Q2. 5-session RSP-minus-SPY gap: how unusual, and what follows?")
print("=" * 68)

cs, cr = C["SPY"], C["RSP"]
gaps = []
for i in range(5, len(cs)):
    g = (cr[i] / cr[i - 5] - 1) * 100 - (cs[i] / cs[i - 5] - 1) * 100
    gaps.append((i, g))

cur = gaps[-1][1]
srt = sorted(g for _, g in gaps)
pct = 100 * sum(1 for g in srt if g < cur) / len(srt)
print(f"latest complete-bar 5d gap (RSP - SPY): {cur:+.2f} pts  "
       f"-> {pct:.1f}th percentile of {len(gaps)} observations")
print(f"  (distribution: p1 {srt[len(srt)//100]:+.2f}  p5 {srt[len(srt)//20]:+.2f}  "
      f"median {srt[len(srt)//2]:+.2f}  p95 {srt[-len(srt)//20]:+.2f})")

# Episodes at least as extreme as today: what happened NEXT to the gap, and to RSP?
thr_g = cur
epi = [i for i, g in gaps if g <= thr_g]
print(f"\nepisodes with a 5d gap <= {thr_g:+.2f} pts: n={len(epi)} "
      f"(overlapping windows — treat n as effective-n much smaller)")
for h in (1, 3, 5, 10):
    fwd_gap, fwd_rsp, fwd_spy = [], [], []
    for i in epi:
        if i + h >= len(cs):
            continue
        fwd_gap.append((cr[i + h] / cr[i] - 1) * 100 - (cs[i + h] / cs[i] - 1) * 100)
        fwd_rsp.append((cr[i + h] / cr[i] - 1) * 100)
        fwd_spy.append((cs[i + h] / cs[i] - 1) * 100)
    if not fwd_gap:
        continue
    n = len(fwd_gap)
    wins = sum(1 for g in fwd_gap if g > 0)
    print(f"  +{h:>2}d (n={n:>3}): RSP {sum(fwd_rsp)/n:+.2f}%  SPY {sum(fwd_spy)/n:+.2f}%  "
          f"gap {sum(fwd_gap)/n:+.2f} pts   gap closes {wins}/{n} = {100*wins/n:.0f}%")

# Unconditional control for the same horizons.
print("\n  unconditional control (all days):")
for h in (1, 3, 5, 10):
    fg = [(cr[i + h] / cr[i] - 1) * 100 - (cs[i + h] / cs[i] - 1) * 100
          for i in range(len(cs) - h)]
    wins = sum(1 for g in fg if g > 0)
    print(f"  +{h:>2}d (n={len(fg):>3}): gap {sum(fg)/len(fg):+.2f} pts   "
          f"gap closes {wins}/{len(fg)} = {100*wins/len(fg):.0f}%")

# ------------------------------------------------- window attribution, 7/28 on
print("\n" + "=" * 68)
print("Window 7/28 close -> last complete bar (adjusted closes)")
print("=" * 68)
try:
    i0 = common.index(datetime(2026, 7, 28).date())
    for s in SYMS:
        print(f"  {s:<4} {C[s][i0]:>9.2f} -> {C[s][-1]:>9.2f}   "
              f"{(C[s][-1]/C[s][i0]-1)*100:+.2f}%")
    print(f"  (last complete bar = {common[-1]})")
except ValueError:
    print("  7/28 not in common sample")
