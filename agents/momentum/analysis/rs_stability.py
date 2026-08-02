"""How stable is `screen.py`'s RS percentile — the input to trend-template criterion 8
and to the top-decile (RS>=90) gate on the pullback trigger — under changes to the
universe it is measured against? Read-only experiment, deterministic seed."""
import sys, random, statistics
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
bars = d.get_stock_bars(StockBarsRequest(symbol_or_symbols=syms, timeframe=TimeFrame.Day,
    start=datetime.now(timezone.utc)-timedelta(days=500), adjustment=Adjustment.ALL))

momo = {}
for sym in syms:
    b = list(bars.data.get(sym, []))
    if len(b) < 253: continue
    c = [float(x.close) for x in b]
    momo[sym] = (c[-22]/c[-253]-1)*100
full = sorted(momo, key=lambda x: momo[x])
rs_full = {s_: i/(len(full)-1)*100 for i, s_ in enumerate(full)}

watch = ["STLD","BIIB","CRWD","DDOG","PANW","VLO","DELL","CVS","DAL","UNH","APH","NTAP","MNST","MRK","MPC","LLY"]
print(f"full universe n={len(momo)}   ret_12_1 and RS percentile\n")
print(f"{'sym':6}{'ret12_1':>10}{'RS_full':>9}   RS over 200 random 260-name subsets: p5..p95   P(RS>=90)")
rng = random.Random(20260802)
subs = [rng.sample(list(momo), 260) for _ in range(200)]
for w in watch:
    vals = []
    for sub in subs:
        u = sub if w in sub else sub[:-1] + [w]
        r = sorted(u, key=lambda x: momo[x])
        vals.append(r.index(w)/(len(r)-1)*100)
    vals.sort()
    p5, p95 = vals[10], vals[189]
    pge = sum(1 for v in vals if v >= 90)/len(vals)
    print(f"{w:6}{momo[w]:>+9.2f}%{rs_full[w]:>9.0f}   {p5:>5.1f} .. {p95:<5.1f}"
          f"{'':14}{pge:>6.0%}")

# how many names sit in the zone where the top-decile gate is a coin flip
band = [s_ for s_ in momo if 86 <= rs_full[s_] <= 94]
print(f"\nnames with RS_full in 86-94 (the zone where a universe change flips the "
      f"RS>=90 gate): {len(band)} of {len(momo)}")
print("  " + " ".join(sorted(band, key=lambda x: -rs_full[x])))

# absolute alternative: what ret_12_1 does RS>=90 correspond to, and how stable is THAT?
cut = sorted(momo.values())[int(0.90*(len(momo)-1))]
print(f"\nRS>=90 in this universe == ret_12_1 >= {cut:+.2f}%")
cuts = []
for sub in subs:
    v = sorted(momo[x] for x in sub)
    cuts.append(v[int(0.90*(len(v)-1))])
cuts.sort()
print(f"  same cutoff over the 200 subsets: p5 {cuts[10]:+.2f}%  median "
      f"{statistics.median(cuts):+.2f}%  p95 {cuts[189]:+.2f}%")
