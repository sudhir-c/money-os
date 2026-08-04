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
  path    = momentum-trend.md 6 requires the pullback hold the MA: no CLOSE below the
            50-day between the 20-day high and today. Checked, not assumed.
"""
import random
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
# Top-decile gate for the pullback trigger. Stays at 90 = AGENT.md's "top decile".
# The 2026-08-02 weekly session tested raising it to 92 (strategy-ideas.md #2) and
# REJECTED that: moving a percentile threshold does not remove the marginal band, it
# relocates it. Measured, 200 seeded 260-name resamples of the 331-name universe —
# P(RS>=92) is 45% for STLD, 32% for DAL, 14% for CVS. A 92 gate would have made
# STLD's arming a coin flip where the 90 gate made it certain (P(RS>=90) = 100%).
PULLBACK_RS = 90
# What DOES fix it: require the gate verdict itself to be stable. A name arms only if
# it clears the gate in >=90% of resampled universes, so an arming decision never rests
# on which names happen to be in the list. This is a fidelity check on the measurement
# of "top decile", not a change to what top decile means.
RS_STABILITY = 0.90
RESAMPLES = 200
SUBSET = 260
SEED = 20260802


def load_universe(path):
    """Parse universe.txt. Strip '#' comments FIRST — the file documents its own
    removals inline ('BK -> BNY', 'EA -> gone'), and a naive .read().split() feeds
    those very tickers back into the RS denominator, plus any comment word that
    happens to be a valid symbol (the word 'ATR' is AptarGroup). Measured 2026-08-02:
    the naive parser readmitted EA and ATR to a nominally-331-name universe."""
    syms = []
    for line in open(path):
        syms += line.split("#")[0].split()
    return sorted(set(syms))


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
        universe = load_universe(uni_file)

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

    # Stability of each RS gate verdict under universe resampling (see RS_STABILITY).
    rng = random.Random(SEED)
    subsets = [rng.sample(list(momo), min(SUBSET, len(momo))) for _ in range(RESAMPLES)]

    def p_clears(sym, gate):
        """Share of resampled universes in which sym's RS clears `gate`."""
        if sym not in momo:
            return 0.0
        hits = 0
        for sub in subsets:
            u = sub if sym in sub else sub[:-1] + [sym]
            r = sorted(u, key=lambda s: momo[s])
            if r.index(sym) / (len(r) - 1) * 100 >= gate:
                hits += 1
        return hits / len(subsets)

    print(f"{'sym':6}{'close':>9}{'RS':>5}{'P90':>6}{'pivot20':>9}{'to_piv':>8}"
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

        # entry triggers.  AGENT.md gives exactly two.
        #  (a) close-confirmed breakout: today's close clears the prior 20-day high
        #  (b) pullback TO THE 50-DAY in a top-decile name: RS>=90, 3-8% off the 20-day
        #      high, and actually AT the 50-day (0 to +3% above it) without breaking it.
        #      The proximity leg is what "pullback-to-the-50-day" means; a 4% dip in a
        #      name sitting 10% above its 50-day is not this setup.
        # PATH CHECK (§6): the pullback must hold the MA. Walk from the bar that set
        # the 20-day high to today and require no CLOSE below the then-current 50-day.
        # Without this, a month of chop straddling the MA reads as a clean retracement
        # (BIIB, 2026-08-02: closed below its 50d on 7/14, 7/15, 7/22 and still armed).
        i_hi = len(b) - 20 + max(range(20), key=lambda j: h[len(b) - 20 + j])
        breaks = [i for i in range(i_hi, len(b)) if c[i] < sum(c[i - 49:i + 1]) / 50]
        path_ok = not breaks

        breakout = px > pivot
        near50 = 0 <= vs50 <= 3
        rs_sym = rs.get(sym, 0)
        # Stability of the gate this trigger actually leans on (see RS_STABILITY).
        p90 = p_clears(sym, PULLBACK_RS)

        trig = []
        if breakout:
            trig.append("BREAKOUT-CLOSE")
        pullback_geom = rs_sym >= PULLBACK_RS and -8 <= off_hi <= -3 and near50 and path_ok
        if pullback_geom and p90 >= RS_STABILITY:
            trig.append("PULLBACK-ARMED")
        elif pullback_geom:
            trig.append(f"pullback-geom/RS-unstable:P90={p90:.0%}")
        elif rs_sym >= PULLBACK_RS:
            why = []
            if not (-8 <= off_hi <= -3):
                why.append("depth")
            if not near50:
                why.append("not-at-50d")
            if not path_ok:
                why.append(f"broke-50d-x{len(breaks)}")
            trig.append("rs-ok/fails:" + "+".join(why))

        # Entry reference depends on the trigger, and so therefore do the stop and the
        # size. A breakout is entered at the next 9:45 after the confirming close, so
        # the honest planning proxy is that close, not the pivot it cleared (using the
        # pivot understates the stop distance and inflates the share count). The
        # defining swing low is the low of the structure being traded: for a breakout,
        # the base from the pivot bar forward; for a pullback, the pullback itself.
        i_pivot = next(i for i in range(len(b) - 21, len(b) - 1) if c[i] == pivot)
        if pullback_geom:
            entry, i_base = px, i_hi
        else:
            entry, i_base = (px, i_pivot) if breakout else (pivot, i_pivot)
        swing_low = min(lo[i_base:])
        # DEGENERACY GUARD (2026-08-03 evening, lessons.md L6 amendment). "The base from
        # the pivot bar forward" is only the base when the pivot bar is the base's LEFT
        # edge — a prior high the name then retraced from. When a name breaks out on two
        # nearby sessions, pivot20 becomes the FIRST breakout's close, i_pivot lands on
        # the right edge instead, and the span collapses to a handful of bars. A 2-bar
        # "base" has a high swing low, so the 2xATR leg wins, the stop tightens, and size
        # inflates — L6's dangerous direction exactly. Measured on the 2026-08-03 close:
        # 6 of 11 breakout names had a span <= 5 (NTAP 2 bars -> 3 sh where the real base
        # from the 7/14 pivot, low 156.26, forces the 10% cap and 2 sh; ROST 3 bars -> 4 sh
        # vs 1). This FLAGS the condition only and changes no arithmetic: the correct span
        # derivation needs a judgment call about where a base starts and is referred to
        # saturday (strategy-ideas.md #10). Until then, a flagged row's stop and size are
        # NOT usable — re-derive them by hand from the bars (L3).
        base_span = len(b) - i_base
        if base_span <= 5:
            trig.append(f"!BASE-SPAN={base_span}b:stop+size UNSAFE, derive by hand")
        stop = min(entry - 2 * atr, swing_low)          # wider of the two
        stop = max(stop, entry * (1 - MAX_STOP))        # never wider than 10%
        stop_frac = (entry - stop) / entry
        size = min(EQUITY * RISK_UNIT / stop_frac, EQUITY * MAX_POS_PCT)
        shares = int(size // entry)                     # whole shares (GTC stops)
        notional = shares * entry

        print(f"{sym:6}{px:>9.2f}{rs_sym:>5.0f}{p90:>5.0%}{pivot:>9.2f}{to_piv:>+7.2f}%"
              f"{sma50:>9.2f}{vs50:>+7.2f}%{off_hi:>+7.2f}%{atr / px * 100:>6.2f}%"
              f"{stop:>9.2f}{stop_frac * 100:>6.1f}%{size:>7.0f}{shares:>4}"
              f"{notional / EQUITY * 100:>5.1f}%  {','.join(trig)}")
        out.append(dict(sym=sym, px=px, rs=rs_sym, p90=p90, pivot=pivot, to_piv=to_piv,
                        sma50=sma50, vs50=vs50, off_hi=off_hi, atr=atr, stop=stop,
                        stop_frac=stop_frac, shares=shares, notional=notional,
                        swing_low=swing_low, base_span=base_span,
                        trigger=",".join(trig)))
    return out


if __name__ == "__main__":
    main()
