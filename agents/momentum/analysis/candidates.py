#!/usr/bin/env python3
"""Saturday candidate builder — turns screen.py's 8/8 trend-template passers into
an actionable watchlist: pivot (20-day high), stop, Rulebook size, pullback geometry.

Read-only. Places no orders. Run from repo root:
    .venv/bin/python agents/momentum/analysis/candidates.py SYM [SYM ...] --rs-universe universe.txt

Rules encoded (AGENT.md + risk-management.md):
  pivot   = highest CLOSE of the last 20 sessions (a close-confirmed breakout needs
            a close above it, so the reference is a close, not an intraday high)
  stop    = wider of (entry - 2*ATR14) and (20-session swing low), capped at -10%
  size $  = min(0.01*E / stop_frac, 0.25*E)          Rulebook rules 1,2,3
  RS      = percentile of ret_12_1 within the FULL screened universe, not this subset
"""
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, "tools")

from alpaca.data.enums import Adjustment
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

from common import get_env_keys

EQUITY = 5000.0
RISK_UNIT = 0.01
MAX_POS_PCT = 0.25
MAX_STOP = 0.10


def fetch(symbols):
    key, secret = get_env_keys()
    data = StockHistoricalDataClient(key, secret)
    start = datetime.now(timezone.utc) - timedelta(days=500)
    return data.get_stock_bars(
        StockBarsRequest(symbol_or_symbols=symbols, timeframe=TimeFrame.Day,
                         start=start, adjustment=Adjustment.ALL)
    )


def main():
    argv = sys.argv[1:]
    uni_file = None
    if "--rs-universe" in argv:
        i = argv.index("--rs-universe")
        uni_file = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    cands = [s.upper() for s in argv]
    universe = cands
    if uni_file:
        universe = sorted(set(open(uni_file).read().split()))

    bars = fetch(sorted(set(universe + cands)))

    # RS percentile across the whole universe (same convention as screen.py)
    momo = {}
    for sym in universe:
        b = list(bars.data.get(sym, []))
        if len(b) < 253:
            continue
        c = [float(x.close) for x in b]
        momo[sym] = (c[-22] / c[-253] - 1) * 100
    ranked = sorted(momo, key=lambda s: momo[s])
    rs = {s: i / (len(ranked) - 1) * 100 for i, s in enumerate(ranked)}

    print(f"{'sym':6}{'close':>9}{'RS':>5}{'pivot20':>9}{'to_piv':>8}"
          f"{'sma50':>9}{'vs50d':>8}{'off20dh':>8}{'ATR%':>7}"
          f"{'stop':>9}{'stop%':>7}{'size$':>7}{'sh':>4}{'%E':>6}  trigger")
    out = []
    for sym in cands:
        b = list(bars.data.get(sym, []))
        if len(b) < 253:
            print(f"{sym:6}  insufficient history")
            continue
        c = [float(x.close) for x in b]
        h = [float(x.high) for x in b]
        lo = [float(x.low) for x in b]
        px = c[-1]

        # Pivot = highest close of the 20 sessions BEFORE today. A breakout is a close
        # above a prior consolidation high; including today makes every new high read
        # as "at pivot" and would fire the trigger on the bar that defines it.
        pivot = max(c[-21:-1])
        to_piv = (pivot / px - 1) * 100         # % move needed to clear it
        sma50 = sum(c[-50:]) / 50
        vs50 = (px / sma50 - 1) * 100
        hi20 = max(h[-20:])
        off_hi = (px / hi20 - 1) * 100          # pullback depth from 20d intraday high

        trs = [max(h[i] - lo[i], abs(h[i] - c[i - 1]), abs(lo[i] - c[i - 1]))
               for i in range(len(b) - 14, len(b))]
        atr = sum(trs) / 14

        # Stop is set off the PIVOT (the breakout entry reference), not today's close.
        entry = pivot
        swing_low = min(lo[-20:])
        stop = min(entry - 2 * atr, swing_low)          # wider of the two
        stop = max(stop, entry * (1 - MAX_STOP))        # never wider than 10%
        stop_frac = (entry - stop) / entry
        size = min(EQUITY * RISK_UNIT / stop_frac, EQUITY * MAX_POS_PCT)
        shares = int(size // entry)                     # whole shares (GTC stops)
        notional = shares * entry

        # entry triggers.  AGENT.md gives exactly two.
        #  (a) close-confirmed breakout: today's close clears the prior 20-day high
        #  (b) pullback TO THE 50-DAY in a top-decile name: RS>=90, 3-8% off the 20-day
        #      high, and actually AT the 50-day (0 to +3% above it) without breaking it.
        #      The proximity leg is what "pullback-to-the-50-day" means; a 4% dip in a
        #      name sitting 10% above its 50-day is not this setup.
        trig = []
        if px > pivot:
            trig.append("BREAKOUT-CLOSE")
        near50 = 0 <= vs50 <= 3
        if rs.get(sym, 0) >= 90 and -8 <= off_hi <= -3 and near50:
            trig.append("PULLBACK-ARMED")
        elif rs.get(sym, 0) >= 90:
            why = []
            if not (-8 <= off_hi <= -3):
                why.append("depth")
            if not near50:
                why.append("not-at-50d")
            trig.append("rs-ok/fails:" + "+".join(why))

        print(f"{sym:6}{px:>9.2f}{rs.get(sym, 0):>5.0f}{pivot:>9.2f}{to_piv:>+7.2f}%"
              f"{sma50:>9.2f}{vs50:>+7.2f}%{off_hi:>+7.2f}%{atr / px * 100:>6.2f}%"
              f"{stop:>9.2f}{stop_frac * 100:>6.1f}%{size:>7.0f}{shares:>4}"
              f"{notional / EQUITY * 100:>5.1f}%  {','.join(trig)}")
        out.append(dict(sym=sym, px=px, rs=rs.get(sym, 0), pivot=pivot, to_piv=to_piv,
                        sma50=sma50, vs50=vs50, off_hi=off_hi, atr=atr, stop=stop,
                        stop_frac=stop_frac, shares=shares, notional=notional))
    return out


if __name__ == "__main__":
    main()
