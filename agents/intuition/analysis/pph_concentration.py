"""Is the '7/28 -> 8/4 pharma de-rate' a SECTOR event or a CONCENTRATION event?

Written 2026-08-04 evening. For four sessions I have recorded "cause of the pharma
de-rate NOT established" while using PPH as "the pure expression of the pharma story."
Tonight I verified PPH's holdings (stockanalysis.com, as of 2026-07-30): LLY is
19.71% of the fund and the top ten are 72.64%. That is not a sector read, it is a
megacap concentration bet -- lesson 4's defect, on the instrument I built a
pre-committed SELL trigger on.

This script decomposes PPH's window return into (a) the LLY contribution,
(b) the rest of the top ten, and compares against XPH (S&P equal-weight pharma)
and IHE (cap-weighted US pharma) over the identical window on adjusted closes.

Run from repo root:  .venv/bin/python agents/intuition/analysis/pph_concentration.py
"""

import sqlite3
import os

DB = os.path.join(os.path.dirname(__file__), "..", "..", "..", "data", "market.db")

START = "2026-07-28"   # PPH's peak close
END = "2026-08-04"

# PPH top-ten weights, stockanalysis.com holdings page, AS OF 2026-07-30.
# Secondhand aggregator, but DATED and inside the window, and corroborated in
# order and magnitude by two other summaries (LLY 19.93% / 22.34%). Per lesson 4
# the constructions disagree on the decimal but agree on sign and order of
# magnitude, so the finding is usable; the decimal is not.
WEIGHTS = {
    "LLY": 19.71,
    "NVS": 10.40,   # Novartis ADR
    "MRK": 9.65,
    "NVO": 5.58,
    "BMY": 4.73,
    "MCK": 4.68,
    "ABBV": 4.62,
    "PFE": 4.55,
    "JNJ": 4.40,
    "GSK": 4.33,
}


def close_on_or_before(cur, sym, day):
    cur.execute(
        "SELECT date, close FROM bars WHERE symbol=? AND date<=? ORDER BY date DESC LIMIT 1",
        (sym, day),
    )
    return cur.fetchone()


def ret(cur, sym, start, end):
    a = close_on_or_before(cur, sym, start)
    b = close_on_or_before(cur, sym, end)
    if not a or not b:
        return None
    return (b[1] / a[1] - 1.0) * 100.0, a[1], b[1]


def main():
    con = sqlite3.connect(DB)
    cur = con.cursor()

    print(f"window: {START} close -> {END} close, adjusted bars\n")

    print("=== the three pharma constructions ===")
    etfs = {}
    for sym, label in [
        ("PPH", "VanEck Pharma (26 names, LLY 19.7%, top10 72.6%)"),
        ("IHE", "iShares US Pharma (cap-weighted)"),
        ("XPH", "SPDR S&P Pharma (EQUAL-weighted)"),
    ]:
        r = ret(cur, sym, START, END)
        if r:
            etfs[sym] = r[0]
            print(f"  {sym:4s} {r[1]:9.2f} -> {r[2]:9.2f}  {r[0]:+7.2f}%   {label}")
    if "PPH" in etfs and "XPH" in etfs:
        print(f"\n  SPREAD  XPH minus PPH = {etfs['XPH'] - etfs['PPH']:+.2f} pts")
        print("  -> the AVERAGE pharma stock and the CAP-WEIGHTED pharma stock")
        print("     did not do the same thing. Only one of them is a sector read.")

    print("\n=== PPH top-ten contribution decomposition ===")
    print(f"  {'sym':5s} {'wt%':>6s} {'start':>9s} {'end':>9s} {'ret%':>8s} {'contrib pp':>11s}")
    total_contrib = 0.0
    total_wt = 0.0
    lly_contrib = 0.0
    missing = []
    for sym, wt in WEIGHTS.items():
        r = ret(cur, sym, START, END)
        if not r:
            missing.append(sym)
            continue
        contrib = wt / 100.0 * r[0]
        total_contrib += contrib
        total_wt += wt
        if sym == "LLY":
            lly_contrib = contrib
        print(f"  {sym:5s} {wt:6.2f} {r[1]:9.2f} {r[2]:9.2f} {r[0]:+8.2f} {contrib:+11.2f}")
    if missing:
        print(f"  [no bars for: {', '.join(missing)} -- excluded, so top-ten total is partial]")
    print(f"  {'':5s} {total_wt:6.2f} {'':9s} {'':9s} {'':8s} {total_contrib:+11.2f}  (top-ten total)")

    pph = etfs.get("PPH")
    if pph is not None:
        print(f"\n  PPH actual                     {pph:+.2f}%")
        print(f"  explained by top ten           {total_contrib:+.2f} pp"
              f"  ({total_contrib / pph * 100:5.1f}% of the move)")
        print(f"  of which LLY alone             {lly_contrib:+.2f} pp"
              f"  ({lly_contrib / pph * 100:5.1f}% of the move)")
        # PPH stripped of LLY, renormalised
        w_lly = WEIGHTS["LLY"] / 100.0
        ex_lly = (pph - lly_contrib) / (1 - w_lly)
        print(f"  PPH EX-LLY (renormalised)      {ex_lly:+.2f}%")
        if "XPH" in etfs:
            print(f"  XPH (equal-weight)             {etfs['XPH']:+.2f}%")
            print(f"  -> removing LLY closes {abs(lly_contrib / (pph - etfs['XPH'])) * 100:.0f}% of"
                  f" the PPH-vs-XPH gap; the rest is the OTHER megacaps.")

    print("\n=== single-session check: 2026-08-04 ===")
    for sym in ("PPH", "XPH", "IHE", "XLV", "SPY"):
        cur.execute(
            "SELECT date, close FROM bars WHERE symbol=? AND date<=? ORDER BY date DESC LIMIT 2",
            (sym, END),
        )
        rows = cur.fetchall()
        if len(rows) == 2:
            d = (rows[0][1] / rows[1][1] - 1.0) * 100.0
            print(f"  {sym:4s} {rows[1][1]:9.2f} -> {rows[0][1]:9.2f}  {d:+7.2f}%")

    print("\n=== how much LLY moves PPH tomorrow (LLY reports pre-open 8/5) ===")
    p = close_on_or_before(cur, "PPH", END)
    if p:
        px = p[1]
        w = WEIGHTS["LLY"] / 100.0
        print(f"  PPH close {px:.2f}; pharma-story-break level 105.50 = {(105.50/px-1)*100:+.2f}%")
        print(f"  LLY weight {w*100:.2f}% -> PPH impact of an LLY move, all else flat:")
        for m in (-5, -8, -10, -12, -15, -20):
            newp = px * (1 + w * m / 100.0)
            flag = "  <-- THROUGH THE TRIGGER" if newp < 105.50 else ""
            print(f"    LLY {m:+3d}%  ->  PPH {newp:7.2f}  ({(newp/px-1)*100:+5.2f}%){flag}")
        breach = (105.50 / px - 1) / w * 100
        print(f"\n  LLY alone breaches 105.50 at {breach:+.1f}% -- with every other")
        print("  PPH holding UNCHANGED. That is a single-stock earnings reaction, not")
        print("  'the pharma story broke.'")

    # ---- the position I actually own -------------------------------------
    # XLV top-ten weights, stockanalysis.com, AS OF 2026-07-30 (inside the window).
    # LLY 15.47% corroborated at 15.81% by a second source: same sign, same order
    # of magnitude, so usable (lesson 4); the decimal is not.
    XLV_W = {
        "LLY": 15.47, "JNJ": 10.43, "ABBV": 7.70, "UNH": 6.48, "MRK": 5.43,
        "TMO": 3.63, "AMGN": 3.54, "ABT": 3.11, "GILD": 2.76, "PFE": 2.40,
    }
    print("\n=== XLV: is MY position's loss idiosyncratic, or is it its top ten? ===")
    print("  (weekly item #11 asked this and three sessions answered 'cause unknown')")
    print(f"  {'sym':5s} {'wt%':>6s} {'ret%':>8s} {'contrib pp':>11s}")
    xt, xw, missing = 0.0, 0.0, []
    contribs = {}
    for sym, wt in XLV_W.items():
        r = ret(cur, sym, START, END)
        if not r:
            missing.append(sym)
            continue
        c = wt / 100.0 * r[0]
        contribs[sym] = c
        xt += c
        xw += wt
        print(f"  {sym:5s} {wt:6.2f} {r[0]:+8.2f} {c:+11.2f}")
    if missing:
        print(f"  [no bars for: {', '.join(missing)} -- excluded]")
    xlv = ret(cur, "XLV", START, END)
    print(f"  {'':5s} {xw:6.2f} {'':8s} {xt:+11.2f}  (top ten, measured)")
    if xlv:
        print(f"\n  XLV actual                 {xlv[0]:+.2f}%")
        print(f"  explained by its top ten   {xt:+.2f} pp  ({xt / xlv[0] * 100:.0f}% of the move)")
        print(f"  of which LLY alone         {contribs.get('LLY', 0):+.2f} pp"
              f"  ({contribs.get('LLY', 0) / xlv[0] * 100:.0f}%)")
        px = close_on_or_before(cur, "XLV", END)[1]
        w = XLV_W["LLY"] / 100.0
        print(f"\n  XLV close {px:.2f}; xlv-trend-break 156.50 = {(156.50/px-1)*100:+.2f}%")
        print(f"  LLY alone breaches 156.50 at {((156.50/px-1)/w)*100:+.1f}%"
              " -- i.e. it effectively cannot.")
        print("  So the POSITION trigger is robust to a single-name print and the")
        print("  SIGNAL trigger (PPH, -12.4%) is not. That is backwards from intent.")

    con.close()


if __name__ == "__main__":
    main()
