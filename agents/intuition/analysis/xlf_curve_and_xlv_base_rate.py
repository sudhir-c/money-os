"""Evening 8/4. Two questions I have deferred for four sessions, both decision-relevant.

Q1 (weekly backlog 7b — MY LARGEST POSITION, 22.9% of equity):
    My XLF rationale is a STEEPENER story: "short rates anchored at 3.50-3.75% while
    the 30-year runs to 5.1% IS net-interest-margin expansion." But the event I have
    been treating as bullish for XLF is a September HIKE, and a hike raises the SHORT
    end, which FLATTENS. Those cannot both be right. I have never tested which one
    XLF actually wants. Regress XLF daily returns on d(2y), d(30y) and d(slope), and
    condition on steepening vs flattening days.

    Extra urgency from today's tape: XLF has now closed UP on three consecutive days
    in which TLT ROSE (long yields FELL) - 8/3 +0.77%, 8/4 +0.87% - and printed a
    52-week high while its stated mechanism ran backwards. Either the mechanism is
    not what is driving it, or the mechanism is not what I think it is.

Q2 (weekly backlog 11 — XLV, 16% of equity, 4 sessions of "cause not established"):
    I hold XLV through an idiosyncratic drawdown I cannot name a cause for. This
    morning I measured that it is NOT explained by beta. Tonight the base rate:
    how unusual is a 5-session XLV-minus-SPY gap this wide, and what has followed?
    Unlike this morning's breadth question (n=2, unusable), healthcare relative
    drawdowns should have a real sample.

All prices from force-adjusted Alpaca daily bars; all yields from FRED (lesson 1).
Free-tier feed needs an end timestamp ~30 min in the past.
"""
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, "tools")
from alpaca.data.enums import Adjustment
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from common import get_env_keys

SYMS = ["SPY", "XLF", "XLV", "KRE", "TLT"]

key, sec = get_env_keys()
client = StockHistoricalDataClient(key, sec)
end = datetime.now(timezone.utc) - timedelta(minutes=30)
start = end - timedelta(days=1100)
bars = client.get_stock_bars(StockBarsRequest(
    symbol_or_symbols=SYMS, timeframe=TimeFrame.Day, start=start, end=end,
    adjustment=Adjustment.ALL)).data

px = {s: {b.timestamp.date(): b.close for b in bars[s]} for s in SYMS}

# ---- FRED yields out of the local db data.py maintains -------------------
dbp = [p for p in (Path("tools/data.db"), Path("data.db"), Path("tools/moneyos.db"))
       if p.exists()]
if not dbp:
    hits = list(Path(".").rglob("*.db"))
    dbp = [h for h in hits if "fred" in
           {r[0] for r in sqlite3.connect(h).execute(
               "SELECT name FROM sqlite_master WHERE type='table'").fetchall()}]
conn = sqlite3.connect(dbp[0])
print(f"fred db: {dbp[0]}")


def fred(series):
    rows = conn.execute("SELECT date, value FROM fred WHERE series=?", (series,)).fetchall()
    return {datetime.fromisoformat(d).date(): v for d, v in rows}


y2, y30, y10 = fred("DGS2"), fred("DGS30"), fred("DGS10")

common = sorted(set(px["SPY"]) & set(px["XLF"]) & set(px["XLV"]) & set(px["KRE"])
                & set(px["TLT"]) & set(y2) & set(y30) & set(y10))
print(f"common sample (bars AND FRED): {common[0]} -> {common[-1]}  ({len(common)} sessions)\n")


def rets(s):
    return [(px[s][common[i]] / px[s][common[i - 1]] - 1) * 100
            for i in range(1, len(common))]


spy, xlf, xlv, kre = rets("SPY"), rets("XLF"), rets("XLV"), rets("KRE")
# yield CHANGES in basis points, aligned to the same [1:] index as the returns
d2 = [(y2[common[i]] - y2[common[i - 1]]) * 100 for i in range(1, len(common))]
d30 = [(y30[common[i]] - y30[common[i - 1]]) * 100 for i in range(1, len(common))]
slope = [y30[d] - y2[d] for d in common]
dslope = [(slope[i] - slope[i - 1]) * 100 for i in range(1, len(common))]
dates = common[1:]
N = len(spy)


def mean(v):
    return sum(v) / len(v) if v else float("nan")


def ols(y, xs):
    """Plain multiple regression via normal equations. xs = list of columns."""
    n = len(y)
    X = [[1.0] + [c[i] for c in xs] for i in range(n)]
    k = len(X[0])
    XtX = [[sum(X[i][a] * X[i][b] for i in range(n)) for b in range(k)] for a in range(k)]
    Xty = [sum(X[i][a] * y[i] for i in range(n)) for a in range(k)]
    # gaussian elimination
    M = [row[:] + [Xty[r]] for r, row in enumerate(XtX)]
    for c in range(k):
        p = max(range(c, k), key=lambda r: abs(M[r][c]))
        M[c], M[p] = M[p], M[c]
        for r in range(k):
            if r != c and M[c][c]:
                f = M[r][c] / M[c][c]
                for j in range(c, k + 1):
                    M[r][j] -= f * M[c][j]
    beta = [M[r][k] / M[r][r] if M[r][r] else float("nan") for r in range(k)]
    yhat = [sum(beta[a] * X[i][a] for a in range(k)) for i in range(n)]
    ybar = mean(y)
    ss_res = sum((y[i] - yhat[i]) ** 2 for i in range(n))
    ss_tot = sum((v - ybar) ** 2 for v in y)
    return beta, (1 - ss_res / ss_tot if ss_tot else float("nan"))


print("=" * 74)
print("Q1. Does XLF want a HIKE (flattener) or a STEEPENER?  [backlog 7b]")
print("=" * 74)

# XLF's raw return conflates the market. Strip it: XLF minus its SPY beta.
b_spy, _ = ols(xlf, [spy])
xlf_ex = [xlf[i] - (b_spy[0] + b_spy[1] * spy[i]) for i in range(N)]
print(f"XLF beta to SPY (full sample, n={N}): {b_spy[1]:.3f}")
print("Below, XLF_ex = XLF return with the market component regressed out.\n")

for label, win in (("full sample", N), ("last 252", 252), ("last 126", 126)):
    s = slice(N - win, N)
    beta, r2 = ols(xlf_ex[s], [d2[s], d30[s]])
    bslope, r2s = ols(xlf_ex[s], [dslope[s]])
    print(f"-- {label} (n={win})")
    print(f"   XLF_ex ~ d2y + d30y :  d2y {beta[1]:+.4f} %/bp   "
          f"d30y {beta[2]:+.4f} %/bp   R2={r2:.3f}")
    print(f"   XLF_ex ~ d(30y-2y)  :  dslope {bslope[1]:+.4f} %/bp   R2={r2s:.3f}")

print("\n   Read: a STEEPENER story wants d30y POSITIVE and d2y NEGATIVE (long end up,")
print("   short end down) => a positive dslope coefficient. A HIKE story wants d2y")
print("   POSITIVE. The signs tell me which trade I am actually in.\n")

# Conditional view, which is harder to argue with than a coefficient.
print("-- Conditional means of XLF_ex (%/day), full sample")
buckets = [
    ("steepened (dslope > +2bp)", [i for i in range(N) if dslope[i] > 2]),
    ("flattened (dslope < -2bp)", [i for i in range(N) if dslope[i] < -2]),
    ("30y UP   > +3bp", [i for i in range(N) if d30[i] > 3]),
    ("30y DOWN < -3bp", [i for i in range(N) if d30[i] < -3]),
    ("2y  UP   > +3bp  (hike-pricing)", [i for i in range(N) if d2[i] > 3]),
    ("2y  DOWN < -3bp  (cut-pricing)", [i for i in range(N) if d2[i] < -3]),
    ("bear steepener (30y up, 2y down)",
     [i for i in range(N) if d30[i] > 0 and d2[i] < 0]),
    ("bear flattener (both up, 2y more)",
     [i for i in range(N) if d30[i] > 0 and d2[i] > d30[i]]),
]
for name, idx in buckets:
    if len(idx) < 10:
        print(f"   {name:34s} n={len(idx):4d}  (too few, skipped)")
        continue
    print(f"   {name:34s} n={len(idx):4d}  XLF_ex {mean([xlf_ex[i] for i in idx]):+.4f}"
          f"   raw XLF {mean([xlf[i] for i in idx]):+.3f}"
          f"   KRE {mean([kre[i] for i in idx]):+.3f}")

# Lesson 4: a finding that only exists in one window is not a finding.
print("\n-- WINDOW STABILITY of the key buckets (lesson 4). raw XLF %/day.")
print(f"   {'bucket':34s} {'full':>16s} {'last504':>16s} {'last252':>16s}")
for name, _ in buckets:
    row = f"   {name:34s}"
    ok = True
    for win in (N, 504, 252):
        lo = N - win
        idx = [i for i, (nm, ix) in [(j, b) for j, b in enumerate(buckets)]
               if False]  # placeholder, recomputed below
        sel = {
            "steepened (dslope > +2bp)": lambda i: dslope[i] > 2,
            "flattened (dslope < -2bp)": lambda i: dslope[i] < -2,
            "30y UP   > +3bp": lambda i: d30[i] > 3,
            "30y DOWN < -3bp": lambda i: d30[i] < -3,
            "2y  UP   > +3bp  (hike-pricing)": lambda i: d2[i] > 3,
            "2y  DOWN < -3bp  (cut-pricing)": lambda i: d2[i] < -3,
            "bear steepener (30y up, 2y down)": lambda i: d30[i] > 0 and d2[i] < 0,
            "bear flattener (both up, 2y more)": lambda i: d30[i] > 0 and d2[i] > d30[i],
        }[name]
        idx = [i for i in range(lo, N) if sel(i)]
        if len(idx) < 10:
            row += f"{'n<10':>16s}"
            ok = False
        else:
            row += f"{mean([xlf[i] for i in idx]):+10.3f}(n{len(idx):3d})"
    print(row)

# The specific configuration of the last three sessions.
print("\n-- The last 6 sessions, the configuration I am living in right now")
print(f"   {'date':12s} {'d2y':>7s} {'d30y':>7s} {'dslope':>7s} {'XLF':>7s} "
      f"{'XLF_ex':>7s} {'SPY':>7s}")
for i in range(N - 6, N):
    print(f"   {str(dates[i]):12s} {d2[i]:+7.1f} {d30[i]:+7.1f} {dslope[i]:+7.1f} "
          f"{xlf[i]:+7.2f} {xlf_ex[i]:+7.2f} {spy[i]:+7.2f}")

print()
print("=" * 74)
print("Q2. XLV relative drawdown: how extreme, and what follows?  [backlog 11]")
print("=" * 74)

# Q2 needs NO yield data, so it must not inherit Q1's FRED join - DGS only posts
# through 8/3 and that would silently drop today's bar from the whole question.
common = sorted(set(px["SPY"]) & set(px["XLV"]))
print(f"(Q2 sample is bars-only: {common[0]} -> {common[-1]}, {len(common)} sessions)")

# 5-session cumulative XLV-minus-SPY gap, in points.
K = 5
gap = []
for i in range(K, len(common)):
    g = ((px["XLV"][common[i]] / px["XLV"][common[i - K]] - 1)
         - (px["SPY"][common[i]] / px["SPY"][common[i - K]] - 1)) * 100
    gap.append((common[i], g))

vals = sorted(g for _, g in gap)
cur_d, cur = gap[-1]
n = len(vals)


def pct_of(x):
    return 100.0 * sum(1 for v in vals if v <= x) / n


def q(p):
    return vals[max(0, min(n - 1, int(p / 100 * n)))]


print(f"{K}-session XLV-minus-SPY gap, n={n} observations "
      f"({gap[0][0]} -> {gap[-1][0]})")
print(f"  today ({cur_d}): {cur:+.2f} pts  ->  {pct_of(cur):.1f}th percentile")
print(f"  p1 {q(1):+.2f}   p5 {q(5):+.2f}   p10 {q(10):+.2f}   "
      f"median {q(50):+.2f}   p90 {q(90):+.2f}")

# Forward behaviour conditional on a gap at least this wide.
epi = [i for i, (_, g) in enumerate(gap) if g <= cur]
print(f"\n  episodes with a gap <= {cur:+.2f} pts: n={len(epi)} "
      f"(overlapping windows - NOT independent)")
if len(epi) >= 10:
    for h in (1, 3, 5, 10, 20):
        fwd_x, fwd_gap = [], []
        for i in epi:
            j = K + i + h
            if j < len(common):
                base = K + i
                rx = (px["XLV"][common[j]] / px["XLV"][common[base]] - 1) * 100
                rs = (px["SPY"][common[j]] / px["SPY"][common[base]] - 1) * 100
                fwd_x.append(rx)
                fwd_gap.append(rx - rs)
        if fwd_x:
            print(f"   +{h:2d}d  XLV {mean(fwd_x):+6.2f}%   "
                  f"XLV-SPY {mean(fwd_gap):+6.2f} pts   "
                  f"gap positive {100*sum(1 for v in fwd_gap if v>0)/len(fwd_gap):.0f}%"
                  f"  (n={len(fwd_x)})")
    # Unconditional control - without this the numbers above mean nothing.
    print("\n  UNCONDITIONAL control (every day in the sample):")
    for h in (1, 3, 5, 10, 20):
        fwd_x, fwd_gap = [], []
        for base in range(len(common) - h):
            rx = (px["XLV"][common[base + h]] / px["XLV"][common[base]] - 1) * 100
            rs = (px["SPY"][common[base + h]] / px["SPY"][common[base]] - 1) * 100
            fwd_x.append(rx)
            fwd_gap.append(rx - rs)
        print(f"   +{h:2d}d  XLV {mean(fwd_x):+6.2f}%   "
              f"XLV-SPY {mean(fwd_gap):+6.2f} pts   "
              f"gap positive {100*sum(1 for v in fwd_gap if v>0)/len(fwd_gap):.0f}%"
              f"  (n={len(fwd_x)})")
else:
    print("   too few episodes to say anything - recording that, not quoting stats.")

print("\n-- How many of the last 10 sessions did XLV underperform SPY? (bars-only)")
recent = []
for i in range(len(common) - 10, len(common)):
    rx = (px["XLV"][common[i]] / px["XLV"][common[i - 1]] - 1) * 100
    rs = (px["SPY"][common[i]] / px["SPY"][common[i - 1]] - 1) * 100
    recent.append((common[i], rx - rs))
for d, g in recent:
    print(f"   {str(d):12s} {g:+6.2f} pts")
print(f"   under-performed on {sum(1 for _, g in recent if g < 0)} of 10")
