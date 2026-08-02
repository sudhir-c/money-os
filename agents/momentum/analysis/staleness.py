import sys
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
from collections import Counter
last = {}
for sym in syms:
    b = list(bars.data.get(sym, []))
    last[sym] = b[-1].timestamp.date().isoformat() if b else "NO DATA"
c = Counter(last.values())
print("last-bar-date distribution:", dict(c))
newest = max(c)
for sym, dt in sorted(last.items()):
    if dt != newest:
        print(f"  STALE/MISSING  {sym:6} last bar {dt}")
