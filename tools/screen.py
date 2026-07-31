#!/usr/bin/env python3
"""Candidate screen: 12-1 momentum, 52-wk-high proximity, ATR(14), trend filter.

Columns map directly onto library rules:
  ret_12_1  -> momentum-trend.md §1 (12-1 convention, skips last 21 sessions)
  ret_6_1   -> momentum-trend.md §1 (blended lookback, reduces specification risk)
  pct_52wh  -> momentum-trend.md §4 (George & Hwang 52-week-high)
  updays    -> momentum-trend.md §1 "frog in the pan" path-smoothness tiebreaker
  atr14/atr%-> risk-management.md Rules 2, 8 (2xATR stop, 1% risk sizing)
  size_1pct -> Rulebook Rule 2 position $ at a 2xATR stop, capped at Rule 3 (25%)

Usage:  python tools/screen.py SYM [SYM ...]
"""
import sys
from datetime import datetime, timedelta, timezone

from alpaca.data.enums import Adjustment
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

from common import get_env_keys

EQUITY = 5000.0
RISK_UNIT = 0.01
MAX_POS_PCT = 0.25


def trend_template(px, c, h, lo, rs_pct):
    """Minervini's 8 trend-template criteria. Returns (list[bool], detail dict).

    RS (criterion 8) is a percentile *within the screened universe*, not IBD's
    all-stock rating — screen a broad liquid list or the number flatters itself.
    """
    sma50 = sum(c[-50:]) / 50
    sma150 = sum(c[-150:]) / 150
    sma200 = sum(c[-200:]) / 200
    sma200_1mo_ago = sum(c[-222:-22]) / 200
    hi52, lo52 = max(h[-253:]), min(lo[-253:])
    checks = [
        px > sma150 and px > sma200,        # 1 price above 150d and 200d
        sma150 > sma200,                    # 2 150d above 200d
        sma200 > sma200_1mo_ago,            # 3 200d rising for >=1 month
        sma50 > sma150 and sma50 > sma200,  # 4 50d above both
        px > sma50,                         # 5 price above 50d
        px >= lo52 * 1.30,                  # 6 >=30% above 52-week low
        px >= hi52 * 0.75,                  # 7 within 25% of 52-week high
        rs_pct >= 70,                       # 8 relative strength in top 30%
    ]
    return checks, {"sma50": sma50, "sma150": sma150, "sma200": sma200,
                    "hi52": hi52, "lo52": lo52,
                    "pct_above_low": (px / lo52 - 1) * 100}


def main() -> None:
    argv = sys.argv[1:]
    template_mode = "--template" in argv
    symbols = [s.upper() for s in argv if not s.startswith("--")]
    if not symbols:
        sys.exit("usage: screen.py [--template] SYM [SYM ...]")
    key, secret = get_env_keys()
    data = StockHistoricalDataClient(key, secret)
    start = datetime.now(timezone.utc) - timedelta(days=500)
    bars = data.get_stock_bars(
        StockBarsRequest(symbol_or_symbols=symbols, timeframe=TimeFrame.Day,
                         start=start, adjustment=Adjustment.ALL)
    )

    rows = []
    for sym in symbols:
        b = list(bars.data.get(sym, []))
        if len(b) < 253:
            print(f"{sym:6}  insufficient history ({len(b)} bars)")
            continue
        c = [float(x.close) for x in b]
        h = [float(x.high) for x in b]
        lo = [float(x.low) for x in b]
        px = c[-1]

        # 12-1 and 6-1 momentum: skip the most recent 21 sessions (Jegadeesh 1990 reversal)
        r12_1 = (c[-22] / c[-253] - 1) * 100
        r6_1 = (c[-22] / c[-148] - 1) * 100

        hi52 = max(h[-253:])
        pct_52wh = px / hi52 * 100

        # frog-in-the-pan: share of up days over the 12-1 window
        window = c[-253:-21]
        updays = sum(1 for i in range(1, len(window)) if window[i] > window[i - 1]) / (len(window) - 1) * 100

        # ATR(14), Wilder true range
        trs = []
        for i in range(len(b) - 14, len(b)):
            trs.append(max(h[i] - lo[i], abs(h[i] - c[i - 1]), abs(lo[i] - c[i - 1])))
        atr = sum(trs) / 14

        sma200 = sum(c[-200:]) / 200
        vs200 = (px / sma200 - 1) * 100

        stop = px - 2 * atr
        stop_frac = (px - stop) / px
        size = min(EQUITY * RISK_UNIT / stop_frac, EQUITY * MAX_POS_PCT)

        rows.append(dict(sym=sym, px=px, c=c, h=h, lo=lo, r12_1=r12_1, r6_1=r6_1,
                         pct_52wh=pct_52wh, updays=updays, atr=atr, vs200=vs200,
                         stop=stop, size=size))

    if not rows:
        return

    # RS percentile within the screened universe (criterion 8 input)
    ranked = sorted(rows, key=lambda r: r["r12_1"])
    for i, r in enumerate(ranked):
        r["rs"] = (i / (len(ranked) - 1) * 100) if len(ranked) > 1 else 100.0

    if template_mode:
        print(f"{'sym':6}{'close':>9}{'RS':>6}  {'1 2 3 4 5 6 7 8':16}{'pass':>6}"
              f"{'%52wh':>8}{'%>52wl':>8}{'ATR%':>7}{'stop2atr':>10}{'size1%':>9}")
        for r in rows:
            checks, _ = trend_template(r["px"], r["c"], r["h"], r["lo"], r["rs"])
            marks = " ".join("Y" if x else "." for x in checks)
            print(f"{r['sym']:6}{r['px']:>9.2f}{r['rs']:>6.0f}  {marks:16}"
                  f"{sum(checks):>4}/8{r['pct_52wh']:>7.1f}%"
                  f"{(r['px'] / min(r['lo'][-253:]) - 1) * 100:>7.0f}%"
                  f"{r['atr'] / r['px'] * 100:>6.2f}%{r['stop']:>10.2f}{r['size']:>9.0f}")
        print("\ncriteria: 1 px>150d&200d  2 150d>200d  3 200d rising 1mo  4 50d>150d&200d")
        print("          5 px>50d  6 >=30% above 52wk low  7 within 25% of 52wk high  8 RS>=70")
        return

    print(f"{'sym':6}{'close':>9}{'ret12_1':>9}{'ret6_1':>9}{'%52wh':>8}"
          f"{'updays':>8}{'ATR14':>8}{'ATR%':>7}{'vs200d':>8}{'stop2atr':>10}{'size1%':>9}")
    for r in rows:
        print(f"{r['sym']:6}{r['px']:>9.2f}{r['r12_1']:>+8.2f}%{r['r6_1']:>+8.2f}%"
              f"{r['pct_52wh']:>7.1f}%{r['updays']:>7.1f}%{r['atr']:>8.2f}"
              f"{r['atr'] / r['px'] * 100:>6.2f}%{r['vs200']:>+7.2f}%"
              f"{r['stop']:>10.2f}{r['size']:>9.0f}")


if __name__ == "__main__":
    main()
