#!/usr/bin/env python3
"""Sunday regime checklist — mechanical score per strategies/regime-rotation.md.

Pulls Alpaca daily bars (SPY, RSP, 11 SPDR sectors, defensives) + FRED
(HY OAS, VIX, VIX3M) and prints every leg of the 0-10 score so the number
can be audited, not trusted.

Usage:  python tools/regime.py
"""
import csv
import io
import json
import sys
import urllib.request
from datetime import datetime, timedelta, timezone

from alpaca.data.enums import Adjustment
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

from common import get_env_keys

SECTORS = ["XLK", "XLY", "XLC", "XLF", "XLI", "XLB", "XLE", "XLV", "XLP", "XLU", "XLRE"]
EXTRA = ["SPY", "RSP", "GLD", "SGOV", "BIL", "IWM", "QQQ", "EFA", "AGG"]


def fred(series: str) -> list[tuple[str, float]]:
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}"
    with urllib.request.urlopen(url, timeout=30) as r:
        rows = list(csv.reader(io.StringIO(r.read().decode())))
    out = []
    for date, val in rows[1:]:
        try:
            out.append((date, float(val)))
        except ValueError:
            continue  # FRED writes "." for holidays
    return out


def closes(key: str, secret: str, symbols: list[str], days: int = 500) -> dict[str, list]:
    """Split/dividend-ADJUSTED closes. Raw bars silently corrupt every MA:
    XLK/XLY/XLU all split ~2:1 in the past year."""
    data = StockHistoricalDataClient(key, secret)
    start = datetime.now(timezone.utc) - timedelta(days=days)
    bars = data.get_stock_bars(
        StockBarsRequest(symbol_or_symbols=symbols, timeframe=TimeFrame.Day,
                         start=start, adjustment=Adjustment.ALL)
    )
    out = {}
    for sym in symbols:
        series = [(b.timestamp.date().isoformat(), float(b.close)) for b in bars[sym]]
        out[sym] = series
    return out


def sma(series: list, n: int, offset: int = 0) -> float:
    """SMA of the last n closes, ending `offset` bars back."""
    vals = [c for _, c in series]
    end = len(vals) - offset
    return sum(vals[end - n:end]) / n


def pct(a: float, b: float) -> float:
    return (a / b - 1) * 100


def main() -> None:
    key, secret = get_env_keys()
    px = closes(key, secret, SECTORS + EXTRA)
    spy = px["SPY"]
    asof = spy[-1][0]
    print(f"=== Sunday regime checklist — bars through {asof} ===\n")

    score = 0
    legs = {}

    # 1. SPY trend vs 200d
    spy_c = spy[-1][1]
    spy_200 = sma(spy, 200)
    d = pct(spy_c, spy_200)
    p = 2 if d > 1 else (1 if d >= -1 else 0)
    score += p
    legs["1_spy_trend"] = {"close": spy_c, "sma200": round(spy_200, 2), "pct_vs_sma": round(d, 2), "pts": p}
    print(f"[1] SPY {spy_c:.2f} vs 200d {spy_200:.2f} = {d:+.2f}%  -> +{p}")

    # 2. Trend quality: 200d SMA now vs 20 sessions ago
    spy_200_prior = sma(spy, 200, offset=20)
    slope = pct(spy_200, spy_200_prior)
    p = 1 if slope > 0 else 0
    score += p
    legs["2_slope"] = {"sma200_now": round(spy_200, 2), "sma200_20d_ago": round(spy_200_prior, 2),
                       "pct_change": round(slope, 2), "pts": p}
    print(f"[2] 200d slope over 20 sessions: {spy_200_prior:.2f} -> {spy_200:.2f} ({slope:+.2f}%)  -> +{p}")

    # 3. Breadth: sectors above own 200d
    above, below = [], []
    for s in SECTORS:
        (above if px[s][-1][1] > sma(px[s], 200) else below).append(s)
    n = len(above)
    p = 2 if n >= 8 else (1 if n >= 4 else 0)
    score += p
    legs["3_breadth"] = {"above_200d": above, "below_200d": below, "count": n, "pts": p}
    print(f"[3] Sectors above 200d: {n}/11  above={above}  below={below}  -> +{p}")

    # 4. RSP equal-weight confirm
    rsp_c, rsp_200 = px["RSP"][-1][1], sma(px["RSP"], 200)
    p = 1 if rsp_c > rsp_200 else 0
    score += p
    legs["4_rsp"] = {"close": rsp_c, "sma200": round(rsp_200, 2), "pct_vs_sma": round(pct(rsp_c, rsp_200), 2), "pts": p}
    print(f"[4] RSP {rsp_c:.2f} vs 200d {rsp_200:.2f} = {pct(rsp_c, rsp_200):+.2f}%  -> +{p}")

    # 5. Volatility: VIX level + VIX/VIX3M
    vix, vix3m = fred("VIXCLS"), fred("VXVCLS")
    vl, v3 = vix[-1][1], vix3m[-1][1]
    ratio = vl / v3
    if vl < 20 and ratio < 0.95:
        p = 2
    elif vl > 30 or ratio > 1.0:
        p = 0
    else:
        p = 1
    score += p
    legs["5_vol"] = {"vix": vl, "vix_date": vix[-1][0], "vix3m": v3, "ratio": round(ratio, 3),
                     "vix_5d": [v for _, v in vix[-5:]], "pts": p}
    print(f"[5] VIX {vl:.2f} ({vix[-1][0]}), VIX3M {v3:.2f}, ratio {ratio:.3f}  "
          f"| VIX 5d: {[v for _, v in vix[-5:]]}  -> +{p}")

    # 6. Credit: HY OAS level + 4-week change
    oas = fred("BAMLH0A0HYM2")
    now_bp = oas[-1][1] * 100
    prior = [v for d_, v in oas if d_ <= (datetime.fromisoformat(oas[-1][0]) - timedelta(days=28)).date().isoformat()]
    prior_bp = prior[-1] * 100
    chg = now_bp - prior_bp
    if now_bp < 400 and chg < 75:
        p = 2
    elif now_bp > 500:
        p = 0
    else:
        p = 1
    score += p
    legs["6_credit"] = {"oas_bp": round(now_bp, 1), "date": oas[-1][0], "oas_4wk_ago_bp": round(prior_bp, 1),
                        "chg_4wk_bp": round(chg, 1), "pts": p}
    print(f"[6] HY OAS {now_bp:.0f}bp ({oas[-1][0]}), 4wk ago {prior_bp:.0f}bp, change {chg:+.0f}bp  -> +{p}")

    # 7. Defensive leadership (tiebreaker, can subtract)
    def ret_3mo(sym: str) -> float:
        s = px[sym]
        return pct(s[-1][1], s[-64][1])
    defensive = (ret_3mo("XLP") + ret_3mo("XLU")) / 2
    spy_3mo = ret_3mo("SPY")
    lead = defensive - spy_3mo
    p = -1 if lead > 3 else 0
    score += p
    legs["7_defensive"] = {"xlp_3mo": round(ret_3mo("XLP"), 2), "xlu_3mo": round(ret_3mo("XLU"), 2),
                           "defensive_avg": round(defensive, 2), "spy_3mo": round(spy_3mo, 2),
                           "excess": round(lead, 2), "pts": p}
    print(f"[7] 3mo: XLP {ret_3mo('XLP'):+.2f}%, XLU {ret_3mo('XLU'):+.2f}% (avg {defensive:+.2f}%) "
          f"vs SPY {spy_3mo:+.2f}% -> excess {lead:+.2f}%  -> {p}")

    if score >= 8:
        tier, exposure = "Aggressive (risk-on trend)", "85-100%"
    elif score >= 5:
        tier, exposure = "Neutral (mixed/chop)", "50-70%"
    elif score >= 3:
        tier, exposure = "Defensive (deteriorating)", "25-45%"
    else:
        tier, exposure = "Cash-heavy (risk-off)", "0-25%"

    print(f"\n=== SCORE: {score}/10 -> {tier} | equity exposure {exposure} ===")

    # context: trailing returns for candidate screening
    print("\n--- trailing returns (for momentum/relative-strength screening) ---")
    print(f"{'sym':6}{'1mo':>9}{'3mo':>9}{'6mo':>9}{'12mo':>9}{'vs200d':>9}")
    for s in ["SPY", "RSP", "QQQ", "IWM", "EFA", "AGG", "GLD"] + SECTORS:
        ser = px[s]
        r1 = pct(ser[-1][1], ser[-22][1])
        r3 = pct(ser[-1][1], ser[-64][1])
        r6 = pct(ser[-1][1], ser[-127][1])
        r12 = pct(ser[-1][1], ser[-253][1]) if len(ser) >= 253 else float("nan")
        v200 = pct(ser[-1][1], sma(ser, 200))
        print(f"{s:6}{r1:>+8.2f}%{r3:>+8.2f}%{r6:>+8.2f}%{r12:>+8.2f}%{v200:>+8.2f}%")

    print(json.dumps({"asof": asof, "score": score, "tier": tier, "exposure": exposure, "legs": legs}, indent=2),
          file=sys.stderr)


if __name__ == "__main__":
    main()
