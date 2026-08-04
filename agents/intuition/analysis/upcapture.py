"""Afternoon 8/3: is my sleeve's underperformance the PRICE of low beta, or just bad?
Book has trailed SPY on 3 consecutive risk-on days. Cash explains ~half. Measure the rest.
Sleeve = XLF/RSP/XLV at CURRENT weights, normalized within the equity sleeve.
"""
import sys
from datetime import datetime, timedelta, timezone
sys.path.insert(0, "tools")
from alpaca.data.enums import Adjustment
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from common import get_env_keys

SYMS = ["SPY", "RSP", "XLF", "XLV"]
MV = {"XLF": 1147.30, "RSP": 1085.85, "XLV": 811.25}
tot = sum(MV.values())
W = {k: v / tot for k, v in MV.items()}
print("sleeve weights (within equity):", {k: round(v, 4) for k, v in W.items()})
CASH_FRAC = 1988.24 / 5032.64
print(f"cash fraction of equity: {CASH_FRAC:.4f}\n")

key, sec = get_env_keys()
client = StockHistoricalDataClient(key, sec)
end = datetime.now(timezone.utc) - timedelta(minutes=30)
start = end - timedelta(days=500)
bars = client.get_stock_bars(StockBarsRequest(
    symbol_or_symbols=SYMS, timeframe=TimeFrame.Day, start=start, end=end,
    adjustment=Adjustment.ALL)).data
closes = {s: [b.close for b in bars[s]] for s in SYMS}
n = min(len(v) for v in closes.values())
closes = {s: v[-n:] for s, v in closes.items()}
dates = [b.timestamp.date() for b in bars["SPY"]][-n:]

def rets(s):
    c = closes[s]
    return [(c[i] / c[i-1] - 1) * 100 for i in range(1, len(c))]

R = {s: rets(s) for s in SYMS}
N = len(R["SPY"])
sleeve = [sum(W[s] * R[s][i] for s in W) for i in range(N)]
book = [(1 - CASH_FRAC) * sleeve[i] for i in range(N)]  # cash earns ~0 daily
spy = R["SPY"]
print(f"sessions: {N}  ({dates[1]} -> {dates[-1]})\n")

def stats(label, series, mask):
    idx = [i for i in range(N) if mask(i)]
    if not idx: return
    avg = sum(series[i] for i in idx) / len(idx)
    print(f"  {label:22s} n={len(idx):4d}  avg {avg:+.4f}%")
    return avg

for window, lo in (("last 252 sessions", max(0, N - 252)), ("full sample", 0)):
    print(f"--- {window} ---")
    up = lambda i: i >= lo and spy[i] > 0
    dn = lambda i: i >= lo and spy[i] < 0
    big = lambda i: i >= lo and spy[i] > 1.0
    su = stats("sleeve | SPY up", sleeve, up); pu = stats("SPY   | SPY up", spy, up)
    sd = stats("sleeve | SPY down", sleeve, dn); pd = stats("SPY   | SPY down", spy, dn)
    sb = stats("sleeve | SPY > +1%", sleeve, big); pb = stats("SPY   | SPY > +1%", spy, big)
    bu = stats("BOOK(+cash)| SPY up", book, up)
    bd = stats("BOOK(+cash)| SPY down", book, dn)
    if su and pu and sd and pd:
        print(f"  up-capture   (sleeve): {su/pu*100:6.1f}%   down-capture: {sd/pd*100:6.1f}%")
        print(f"  up-capture   (book)  : {bu/pu*100:6.1f}%   down-capture: {bd/pd*100:6.1f}%")
        print(f"  ==> sleeve capture ratio (up/down, >1 is good): {(su/pu)/(sd/pd):.3f}")
    print()

# beta of sleeve to SPY, last 252
lo = max(0, N - 252)
xs = spy[lo:]; ys = sleeve[lo:]
mx = sum(xs)/len(xs); my = sum(ys)/len(ys)
cov = sum((xs[i]-mx)*(ys[i]-my) for i in range(len(xs)))/len(xs)
var = sum((x-mx)**2 for x in xs)/len(xs)
import math
sd_s = math.sqrt(sum((y-my)**2 for y in ys)/len(ys))
sd_p = math.sqrt(var)
print(f"sleeve beta to SPY (252d): {cov/var:.3f}")
print(f"sleeve daily vol {sd_s*math.sqrt(252):.2f}% ann  vs SPY {sd_p*math.sqrt(252):.2f}% ann")
print(f"sleeve total 252d return: {(1+sum(ys)/100):.4f} approx-arith {sum(ys):+.2f}% vs SPY {sum(xs):+.2f}%")
