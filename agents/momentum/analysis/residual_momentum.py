"""EXPLORATION ONLY — not a live signal. Single-factor (market-model) approximation of
Blitz/Huij/Martens residual momentum, to see how much it would reorder our RS ranking.

Blitz et al. use FF3 residuals from 36 monthly obs, scaled by residual stdev. I have
neither FF factors nor 36 months on hand, so this is a DAILY, SINGLE-FACTOR version over
the same 12-1 window screen.py uses. Weaker than the published construction; treat the
output as a directional read, not a replication."""
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
k, s = get_env_keys()
d = StockHistoricalDataClient(k, s)
bars = d.get_stock_bars(StockBarsRequest(symbol_or_symbols=syms+["SPY"], timeframe=TimeFrame.Day,
    start=datetime.now(timezone.utc)-timedelta(days=500), adjustment=Adjustment.ALL))

sc = [float(x.close) for x in bars.data["SPY"]]
# Estimation window MUST be longer than the accumulation window: with OLS-with-intercept
# fitted on the same sample, the residuals sum to zero identically and the signal is noise.
# Blitz/Huij/Martens estimate over 36 months and accumulate residuals over t-12..t-1;
# ~24 months of daily bars is what is available here, so: fit on the full history,
# accumulate over the 12-1 window only.
mkt_all = [sc[i]/sc[i-1]-1 for i in range(1, len(sc))]
FIT = slice(0, len(mkt_all))
ACC = slice(len(mkt_all)-252, len(mkt_all)-21)
mf = mkt_all[FIT]
mbar = statistics.fmean(mf); mvar = sum((x-mbar)**2 for x in mf)

tot, res = {}, {}
for sym in syms:
    b = list(bars.data.get(sym, []))
    if len(b) < 253: continue
    c = [float(x.close) for x in b]
    r_all = [c[i]/c[i-1]-1 for i in range(1, len(c))]
    if len(r_all) != len(mkt_all): continue
    rf = r_all[FIT]
    rbar = statistics.fmean(rf)
    beta = sum((mf[i]-mbar)*(rf[i]-rbar) for i in range(len(rf)))/mvar
    alpha = rbar - beta*mbar
    e_all = [r_all[i] - alpha - beta*mkt_all[i] for i in range(len(r_all))]
    sd = statistics.pstdev(e_all[FIT])
    e = e_all[ACC]
    tot[sym] = (c[-22]/c[-253]-1)*100
    res[sym] = (sum(e)/sd) if sd else 0.0        # t-stat-like scaled residual return

def pct(dd):
    o = sorted(dd, key=lambda x: dd[x])
    return {s_: i/(len(o)-1)*100 for i, s_ in enumerate(o)}
pt, pr = pct(tot), pct(res)

print(f"n={len(tot)}   RS_tot = percentile of ret_12_1 (current rule)")
print(f"          RS_res = percentile of market-model residual momentum, vol-scaled\n")
watch = ["STLD","NTAP","BIIB","DDOG","PANW","VLO","DELL","CVS","DAL","UNH","APH","MNST","MRK","MPC","LLY","CRWD","TRGP","ROST","STT","GM"]
print(f"{'sym':6}{'ret12_1':>10}{'RS_tot':>8}{'beta':>7}{'resmom':>9}{'RS_res':>8}{'shift':>8}")
for w in sorted(watch, key=lambda x: -pt.get(x, 0)):
    if w not in tot: continue
    b_ = list(bars.data[w]); c=[float(x.close) for x in b_]
    ra=[c[i]/c[i-1]-1 for i in range(1,len(c))]; rf=ra[FIT]
    rbar=statistics.fmean(rf); beta=sum((mf[i]-mbar)*(rf[i]-rbar) for i in range(len(rf)))/mvar
    print(f"{w:6}{tot[w]:>+9.2f}%{pt[w]:>8.0f}{beta:>7.2f}{res[w]:>9.2f}{pr[w]:>8.0f}{pr[w]-pt[w]:>+8.0f}")

both = [s_ for s_ in tot if pt[s_]>=90 and pr[s_]>=90]
only_t = [s_ for s_ in tot if pt[s_]>=90 and pr[s_]<90]
only_r = [s_ for s_ in tot if pt[s_]<90 and pr[s_]>=90]
print(f"\ntop decile on BOTH ({len(both)}): {' '.join(sorted(both, key=lambda x:-pt[x]))}")
print(f"top decile on TOTAL only ({len(only_t)}): {' '.join(sorted(only_t, key=lambda x:-pt[x]))}")
print(f"top decile on RESIDUAL only ({len(only_r)}): {' '.join(sorted(only_r, key=lambda x:-pr[x]))}")
