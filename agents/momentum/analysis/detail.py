#!/usr/bin/env python3
"""Full detail on a shortlist: base geometry, breakout volume, and BOTH sizings
(breakout-at-pivot vs pullback-at-market). Read-only.

    .venv/bin/python agents/momentum/analysis/detail.py SYM [SYM ...]
"""
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, "tools")

from alpaca.data.enums import Adjustment
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

from common import get_env_keys

EQUITY, RISK_UNIT, MAX_POS_PCT, MAX_STOP = 5000.0, 0.01, 0.25, 0.10


def size_for(entry, atr, swing_low):
    """Rulebook 8 + 1-3: stop = wider of 2xATR / defining swing low, capped at 10%.

    NOTE on "defining swing low": Rule 8 does not fix a lookback. The 20-session low is
    the wrong choice when the base is deep or the name has run — it sits below the whole
    structure and the 10% cap then binds mechanically on every name, which is how last
    week's watchlist ended up with seven identically-sized positions. The defining low is
    the low of the CURRENT structure: the pullback low for a pullback entry, the low of
    the immediate consolidation (~10 sessions) for a breakout.
    """
    stop = min(entry - 2 * atr, swing_low)
    capped = stop < entry * (1 - MAX_STOP)
    stop = max(stop, entry * (1 - MAX_STOP))
    frac = (entry - stop) / entry
    size = min(EQUITY * RISK_UNIT / frac, EQUITY * MAX_POS_PCT)
    sh = int(size // entry)
    return stop, frac, size, sh, sh * entry, capped


def main():
    syms = [s.upper() for s in sys.argv[1:]]
    key, secret = get_env_keys()
    data = StockHistoricalDataClient(key, secret)
    bars = data.get_stock_bars(StockBarsRequest(
        symbol_or_symbols=syms, timeframe=TimeFrame.Day,
        start=datetime.now(timezone.utc) - timedelta(days=500),
        adjustment=Adjustment.ALL))

    for sym in syms:
        b = list(bars.data.get(sym, []))
        c = [float(x.close) for x in b]
        h = [float(x.high) for x in b]
        lo = [float(x.low) for x in b]
        v = [float(x.volume) for x in b]
        px, last_date = c[-1], b[-1].timestamp.date()

        pivot = max(c[-21:-1])
        hi20, lo20 = max(h[-21:-1]), min(lo[-21:-1])
        sma50 = sum(c[-50:]) / 50
        sma200 = sum(c[-200:]) / 200
        trs = [max(h[i] - lo[i], abs(h[i] - c[i - 1]), abs(lo[i] - c[i - 1]))
               for i in range(len(b) - 14, len(b))]
        atr = sum(trs) / 14
        vol_ratio = v[-1] / (sum(v[-51:-1]) / 50)
        # base depth: how tight the 20-session range is (Minervini VCP proxy)
        base_depth = (hi20 / lo20 - 1) * 100

        lo10 = min(lo[-11:-1])                  # immediate consolidation low
        # pullback low = lowest low since the 20-day high printed
        idx_hi = max(range(len(h) - 21, len(h)), key=lambda i: h[i])
        pb_low = min(lo[idx_hi:]) if idx_hi < len(lo) - 1 else lo[-1]

        bo = size_for(pivot, atr, lo10)
        pb = size_for(px, atr, pb_low)

        print(f"\n=== {sym}  close {px:.2f} ({last_date})")
        print(f"  pivot(20d prior close hi) {pivot:8.2f}   close vs pivot {(px/pivot-1)*100:+6.2f}%")
        print(f"  20d hi/lo {hi20:.2f} / {lo20:.2f}  base depth {base_depth:5.1f}%"
              f"   off 20d hi {(px/hi20-1)*100:+6.2f}%")
        print(f"  10d swing low {lo10:.2f}   pullback low {pb_low:.2f}")
        print(f"  50d {sma50:8.2f} ({(px/sma50-1)*100:+6.2f}%)   200d {sma200:8.2f} ({(px/sma200-1)*100:+6.2f}%)")
        print(f"  ATR14 {atr:6.2f} ({atr/px*100:.2f}%)   last-day volume {vol_ratio:.2f}x 50d avg")
        print(f"  BREAKOUT entry@pivot {pivot:8.2f} stop {bo[0]:8.2f} ({bo[1]*100:4.1f}%"
              f"{' CAPPED' if bo[5] else ''})  size ${bo[2]:.0f} -> {bo[3]} sh = ${bo[4]:.0f} ({bo[4]/EQUITY*100:.1f}% E)")
        print(f"  PULLBACK entry@last {px:8.2f} stop {pb[0]:8.2f} ({pb[1]*100:4.1f}%"
              f"{' CAPPED' if pb[5] else ''})  size ${pb[2]:.0f} -> {pb[3]} sh = ${pb[4]:.0f} ({pb[4]/EQUITY*100:.1f}% E)")
        print(f"  last 5 closes: {[round(x,2) for x in c[-5:]]}")


if __name__ == "__main__":
    main()
