#!/usr/bin/env python3
"""Dual-momentum core sleeve: SPY vs VEU vs BIL, blended 6/9/12-month lookbacks.

momentum-trend.md §2 (GEM) with the Newfound/ReSolve robustness fix: average the
signal across three lookbacks instead of betting the sleeve on a single 12-month
parameter ("timing luck", failure mode #3). Risk-off asset is BIL, never duration
(failure mode #8).

Total returns, no skip-month: the skip-month convention (Jegadeesh 1990 reversal)
belongs to *cross-sectional stock* ranking, not time-series/dual momentum on
indices. Antonacci's absolute-momentum signal is the plain trailing total return.

Decision:
  absolute leg  -> best equity asset must beat BIL over the blend, else risk-off
  relative leg  -> hold whichever of SPY / VEU has the higher blended return

Usage:  python tools/sleeve.py [--json]
"""
import json
import sys
from datetime import datetime, timedelta, timezone

from alpaca.data.enums import Adjustment
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

from common import get_env_keys

EQUITY_ASSETS = ["SPY", "VEU"]
CASH_ASSET = "BIL"
# trading sessions per lookback (21/month)
LOOKBACKS = {"6m": 126, "9m": 189, "12m": 252}


def main() -> None:
    as_json = "--json" in sys.argv
    key, secret = get_env_keys()
    data = StockHistoricalDataClient(key, secret)
    symbols = EQUITY_ASSETS + [CASH_ASSET]
    start = datetime.now(timezone.utc) - timedelta(days=500)
    bars = data.get_stock_bars(
        StockBarsRequest(symbol_or_symbols=symbols, timeframe=TimeFrame.Day,
                         start=start, adjustment=Adjustment.ALL)
    )

    closes, asof = {}, {}
    for sym in symbols:
        b = list(bars[sym])
        if len(b) < 253:
            sys.exit(f"error: {sym} has only {len(b)} bars; need 253 for a 12m lookback")
        closes[sym] = [float(x.close) for x in b]
        asof[sym] = b[-1].timestamp.date().isoformat()

    rets = {}
    for sym in symbols:
        c = closes[sym]
        r = {name: (c[-1] / c[-(n + 1)] - 1) * 100 for name, n in LOOKBACKS.items()}
        r["blend"] = sum(r.values()) / len(LOOKBACKS)
        rets[sym] = r

    winner = max(EQUITY_ASSETS, key=lambda s: rets[s]["blend"])
    risk_on = rets[winner]["blend"] > rets[CASH_ASSET]["blend"]
    hold = winner if risk_on else CASH_ASSET

    out = {
        "asof": asof["SPY"],
        "returns": rets,
        "relative_winner": winner,
        "absolute_pass": risk_on,
        "hold": hold,
        "margin_vs_bil_pts": round(rets[winner]["blend"] - rets[CASH_ASSET]["blend"], 2),
        "margin_vs_runnerup_pts": round(
            abs(rets["SPY"]["blend"] - rets["VEU"]["blend"]), 2),
    }
    if as_json:
        print(json.dumps(out, indent=2))
        return

    print(f"dual-momentum sleeve — bars through {out['asof']}")
    print(f"{'sym':6}{'6m':>9}{'9m':>9}{'12m':>9}{'blend':>10}")
    for sym in symbols:
        r = rets[sym]
        print(f"{sym:6}{r['6m']:>+8.2f}%{r['9m']:>+8.2f}%{r['12m']:>+8.2f}%{r['blend']:>+9.2f}%")
    print()
    print(f"  relative leg : {winner} (by {out['margin_vs_runnerup_pts']} pts over runner-up)")
    print(f"  absolute leg : {'PASS' if risk_on else 'FAIL'} "
          f"({winner} blend vs {CASH_ASSET}: {out['margin_vs_bil_pts']:+.2f} pts)")
    print(f"  -> HOLD {hold}")


if __name__ == "__main__":
    main()
