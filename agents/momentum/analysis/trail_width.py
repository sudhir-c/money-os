"""EXPLORATION — how wide should the trailing stop be?

AGENT.md fixes the trail at 2.5xATR(14) below the highest close, armed after +1xATR.
This asks the only question that tunes that number: over the next 21 sessions, how often
does a 2.5xATR trail eject us from a trend that was still intact, versus how often does it
correctly eject us from one that broke?

Cohorts, formed on every day t where a name is above BOTH its 50d and 200d SMA
(the template's own definition of "in a trend"):
  INTACT  - close at t+21 is still above the 50d SMA at t+21   -> a stop here is a WHIPSAW
  BROKEN  - close at t+21 is below it                          -> a stop here is PROTECTION
For each path we measure the deepest close-to-close drawdown from the running high over
t+1..t+21, in units of ATR(14) measured at t. A trail of k*ATR fires iff that depth >= k.

HONEST LIMITS: ~2 years of daily bars = one regime (an uptrend), overlapping windows so
observations are far from independent, no transaction costs, and a 21-session horizon is a
proxy for "the trend continued", not the real holding period. This ranks trail widths on
recent tape; it is not a backtest and cannot establish an edge.
"""
import sys, statistics
from datetime import datetime, timedelta, timezone
sys.path.insert(0, "tools")
from alpaca.data.enums import Adjustment
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from common import get_env_keys

def load_universe(path="agents/momentum/analysis/universe.txt"):
    """The pinned universe. RS is a percentile INSIDE this list, so the list is a
    strategy parameter — see memory/lessons.md L2. Comment lines start with '#'."""
    out = []
    for line in open(path):
        line = line.split("#", 1)[0]
        out += line.split()
    return sorted(set(out))

syms = load_universe()
k_, s_ = get_env_keys()
d = StockHistoricalDataClient(k_, s_)
bars = d.get_stock_bars(StockBarsRequest(symbol_or_symbols=syms, timeframe=TimeFrame.Day,
    start=datetime.now(timezone.utc)-timedelta(days=500), adjustment=Adjustment.ALL))

H = 21
intact, broken = [], []
for sym in syms:
    b = list(bars.data.get(sym, []))
    if len(b) < 253: continue
    c = [float(x.close) for x in b]
    h = [float(x.high) for x in b]
    lo = [float(x.low) for x in b]
    tr = [0.0]*len(b)
    for i in range(1, len(b)):
        tr[i] = max(h[i]-lo[i], abs(h[i]-c[i-1]), abs(lo[i]-c[i-1]))
    for t in range(200, len(c)-H):
        sma50 = sum(c[t-49:t+1])/50
        sma200 = sum(c[t-199:t+1])/200
        if not (c[t] > sma50 and c[t] > sma200): continue
        atr = sum(tr[t-13:t+1])/14
        if atr <= 0: continue
        run, depth = c[t], 0.0
        for j in range(t+1, t+1+H):
            run = max(run, c[j])
            depth = max(depth, (run - c[j]) / atr)
        e = t + H
        sma50e = sum(c[e-49:e+1])/50
        (intact if c[e] > sma50e else broken).append(depth)

print(f"cohorts over {len(syms)} names, ~2y of daily bars, overlapping 21-session windows")
print(f"  INTACT (trend held, a stop = whipsaw): {len(intact):,}")
print(f"  BROKEN (trend failed, a stop = protection): {len(broken):,}\n")
print(f"{'trail k*ATR':>12}{'whipsaw rate':>14}{'protection rate':>17}{'protect-whipsaw':>17}")
for k in [1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0]:
    w = sum(1 for x in intact if x >= k)/len(intact)
    p = sum(1 for x in broken if x >= k)/len(broken)
    print(f"{k:>12.1f}{w:>13.1%}{p:>16.1%}{p-w:>16.1%}")
for name, arr in (("INTACT", intact), ("BROKEN", broken)):
    arr = sorted(arr)
    q = lambda f: arr[int(f*(len(arr)-1))]
    print(f"\n{name} max-drawdown-from-running-high, in ATR units: "
          f"median {q(.5):.2f}  p75 {q(.75):.2f}  p90 {q(.90):.2f}  p95 {q(.95):.2f}")

# ---- second cut: dollars, not events. Event counts ignore that a wider trail loses more
# per whipsaw. Re-run the same paths and compare realised 21-session return WITH a k*ATR
# trail against simply holding to t+21, in ATR units (so names are comparable).
print("\n\n=== same paths, measured in P&L (ATR units per trade, mean over all cohort days)")
rows = {}
for sym in syms:
    b = list(bars.data.get(sym, []))
    if len(b) < 253: continue
    c = [float(x.close) for x in b]; h=[float(x.high) for x in b]; lo=[float(x.low) for x in b]
    tr=[0.0]*len(b)
    for i in range(1,len(b)): tr[i]=max(h[i]-lo[i],abs(h[i]-c[i-1]),abs(lo[i]-c[i-1]))
    for t in range(200, len(c)-H):
        sma50=sum(c[t-49:t+1])/50; sma200=sum(c[t-199:t+1])/200
        if not (c[t]>sma50 and c[t]>sma200): continue
        atr=sum(tr[t-13:t+1])/14
        if atr<=0: continue
        for k in (2.0,2.5,3.0,3.5,4.0,99.0):
            run, exitp = c[t], None
            for j in range(t+1, t+1+H):
                run = max(run, c[j])
                if (run - c[j]) / atr >= k:      # stop fires on the close that breaches
                    exitp = c[j]; break
            if exitp is None: exitp = c[t+H]
            rows.setdefault(k, []).append((exitp - c[t]) / atr)
hold = statistics.fmean(rows[99.0])
print(f"{'trail k*ATR':>12}{'mean ret (ATR)':>16}{'vs hold-to-21':>15}{'stdev':>9}{'mean/stdev':>12}")
for k in (2.0,2.5,3.0,3.5,4.0,99.0):
    v = rows[k]; m = statistics.fmean(v); sd = statistics.pstdev(v)
    lbl = "no trail" if k == 99.0 else f"{k:.1f}"
    print(f"{lbl:>12}{m:>16.3f}{m-hold:>+15.3f}{sd:>9.3f}{m/sd:>12.3f}")
