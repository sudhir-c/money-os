"""Premarket 8/5. Item 7b — the highest-value open question in my backlog, on my
LARGEST position, carried unverified for five sessions.

THE CLAIM I SIZED ON: "hawkish is good for XLF." My written rationale is a
STEEPENER story (banks borrow short, lend long; a wider 30y-2y is NIM). But an
actual Fed HIKE raises the SHORT end and FLATTENS unless the long end moves
further. Those two are not the same trade and can point opposite ways. I have
never measured which one XLF actually wants.

Today is exactly the setup that makes it urgent: ADP printed 44K vs ~75K
consensus (soft), TLT has risen three straight sessions and is bid again
premarket, and 10y-2y flattened 0.45 -> 0.43 on 8/4. If XLF wants a steepener,
a dovish bull-steepener is fine for me; if XLF really just wants HIGH SHORT
RATES, then the Sept-hike repricing that has been my tailwind is the thing to
watch and a soft payroll on Friday is a bigger problem than my notes assume.

METHOD, and the part that matters (lesson 3 — measure the mechanism, and
measure the RIGHT thing): XLF is ~1.0 beta to SPY, so raw conditional returns
are swamped by the market. I regress XLF on SPY over the full sample and
condition the RESIDUAL — the XLF-specific move — on the rate move. The four
classic quadrants (bear/bull x steepener/flattener) are the actual answer.

Cross-check on construction (lesson 4): the same test on KRE, a purer
regional-bank NIM expression. If XLF and KRE disagree on sign, I do not have a
finding. If they agree, I do.

Rates from FRED (DGS2/DGS10/DGS30) per lesson 1; prices from force-adjusted
Alpaca bars. Free-tier feed needs an end timestamp ~30 min in the past, so
today's forming bar is excluded.
"""
import csv
import io
import sys
import urllib.request
from datetime import datetime, timedelta, timezone

sys.path.insert(0, "tools")
from alpaca.data.enums import Adjustment
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from common import get_env_keys

SYMS = ["SPY", "XLF", "KRE", "RSP"]

key, sec = get_env_keys()
client = StockHistoricalDataClient(key, sec)
end = datetime.now(timezone.utc) - timedelta(minutes=30)
start = end - timedelta(days=1150)
bars = client.get_stock_bars(StockBarsRequest(
    symbol_or_symbols=SYMS, timeframe=TimeFrame.Day, start=start, end=end,
    adjustment=Adjustment.ALL)).data
px = {s: {b.timestamp.date(): b.close for b in bars[s]} for s in SYMS}


def fred(series):
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}"
    with urllib.request.urlopen(url, timeout=30) as r:
        rows = list(csv.reader(io.StringIO(r.read().decode())))
    out = {}
    for d, v in rows[1:]:
        if v not in (".", ""):
            out[datetime.strptime(d, "%Y-%m-%d").date()] = float(v)
    return out


y2, y10, y30 = fred("DGS2"), fred("DGS10"), fred("DGS30")

common = sorted(set.intersection(
    *(set(v) for v in px.values()), set(y2), set(y10), set(y30)))
print(f"common sample: {common[0]} -> {common[-1]}  ({len(common)} sessions)")
print("NOTE: FRED DGS posts with a lag, so the last few price sessions drop out.\n")

# daily changes, aligned on consecutive COMMON dates
rows = []
for i in range(1, len(common)):
    d0, d1 = common[i - 1], common[i]
    if (d1 - d0).days > 5:          # skip gaps wider than a long weekend
        continue
    rows.append({
        "date": d1,
        "spy": (px["SPY"][d1] / px["SPY"][d0] - 1) * 100,
        "xlf": (px["XLF"][d1] / px["XLF"][d0] - 1) * 100,
        "kre": (px["KRE"][d1] / px["KRE"][d0] - 1) * 100,
        "d2": (y2[d1] - y2[d0]) * 100,        # bp
        "d10": (y10[d1] - y10[d0]) * 100,
        "d30": (y30[d1] - y30[d0]) * 100,
        "dslope": ((y30[d1] - y2[d1]) - (y30[d0] - y2[d0])) * 100,   # 30y-2y, bp
    })
N = len(rows)
print(f"usable daily observations: {N}\n")


def ols(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) ** 2 for x in xs)
    b = sxy / sxx
    return my - b * mx, b


def residualise(sym):
    a, b = ols([r["spy"] for r in rows], [r[sym] for r in rows])
    for r in rows:
        r[sym + "_res"] = r[sym] - (a + b * r["spy"])
    return a, b


for sym in ("xlf", "kre"):
    a, b = residualise(sym)
    print(f"{sym.upper()} vs SPY over {N} sessions: beta {b:.3f}, alpha {a:+.4f}%/day")
print()


def stat(sel, label, sym):
    s = [r[sym + "_res"] for r in rows if sel(r)]
    if not s:
        print(f"  {label:<44} n=0")
        return
    m = sum(s) / len(s)
    pos = sum(1 for x in s if x > 0) / len(s) * 100
    print(f"  {label:<44} n={len(s):>4}  resid {m:+.4f}%  pos {pos:4.1f}%")


def block(title, tests, sym):
    print(f"--- {sym.upper()}: {title}")
    for label, sel in tests:
        stat(sel, label, sym)
    print()


# ------------------------------------------------- Q1: the four rate quadrants
print("=" * 72)
print("Q1. THE FOUR QUADRANTS. Which does XLF actually want?")
print("    (residual = XLF move with the market's move regressed out)")
print("=" * 72)

QUAD = [
    ("BEAR STEEPENER  (30y up, slope wider)", lambda r: r["d30"] > 0 and r["dslope"] > 0),
    ("BULL STEEPENER  (30y down, slope wider)", lambda r: r["d30"] < 0 and r["dslope"] > 0),
    ("BEAR FLATTENER  (30y up, slope tighter)", lambda r: r["d30"] > 0 and r["dslope"] < 0),
    ("BULL FLATTENER  (30y down, slope tighter)", lambda r: r["d30"] < 0 and r["dslope"] < 0),
]
for sym in ("xlf", "kre"):
    block("four quadrants, 30y-2y slope", QUAD, sym)

# ------------------------------------- Q2: separate the two halves of the claim
print("=" * 72)
print("Q2. SEPARATE THE CLAIM'S TWO HALVES: is it the SLOPE, or the SHORT RATE?")
print("=" * 72)

HALVES = [
    ("slope WIDENS >=3bp (steepener)", lambda r: r["dslope"] >= 3),
    ("slope TIGHTENS >=3bp (flattener)", lambda r: r["dslope"] <= -3),
    ("2y UP >=3bp (hawkish repricing)", lambda r: r["d2"] >= 3),
    ("2y DOWN >=3bp (dovish repricing)  <-- TODAY", lambda r: r["d2"] <= -3),
    ("2y DOWN >=5bp (hard dovish)", lambda r: r["d2"] <= -5),
    ("30y UP >=3bp (long end selling off)", lambda r: r["d30"] >= 3),
    ("30y DOWN >=3bp (long end rallying)", lambda r: r["d30"] <= -3),
]
for sym in ("xlf", "kre"):
    block("slope vs short rate", HALVES, sym)

# --------------------------------------------- Q3: the specific branch I fear
print("=" * 72)
print("Q3. THE BRANCH FRIDAY COULD DELIVER: dovish repricing AND a flattener")
print("    (soft payroll -> hike priced out -> 2y falls, curve flattens)")
print("=" * 72)
SPEC = [
    ("2y down>=3bp AND slope tightens", lambda r: r["d2"] <= -3 and r["dslope"] < 0),
    ("2y down>=3bp AND slope widens", lambda r: r["d2"] <= -3 and r["dslope"] > 0),
    ("2y up>=3bp AND slope widens (my thesis day)", lambda r: r["d2"] >= 3 and r["dslope"] > 0),
    ("2y up>=3bp AND slope tightens (hike scare)", lambda r: r["d2"] >= 3 and r["dslope"] < 0),
]
for sym in ("xlf", "kre"):
    block("dovish/hawkish x slope", SPEC, sym)

# --------------------------------------- Q4: stability — is this one window?
print("=" * 72)
print("Q4. STABILITY. Split the sample; a finding that lives in one window is not")
print("    a finding (the capture-ratio trap from lesson 8).")
print("=" * 72)
half = N // 2
for name, lo, hi in (("first half", 0, half), ("second half", half, N),
                     ("last 252", max(0, N - 252), N)):
    sub = rows[lo:hi]
    print(f"--- {name}  ({sub[0]['date']} -> {sub[-1]['date']}, n={len(sub)})")
    for sym in ("xlf", "kre"):
        for label, sel in (("steepener>=3bp", lambda r: r["dslope"] >= 3),
                           ("flattener>=3bp", lambda r: r["dslope"] <= -3),
                           ("2y down>=3bp", lambda r: r["d2"] <= -3)):
            s = [r[sym + "_res"] for r in sub if sel(r)]
            if s:
                print(f"    {sym.upper():<4}{label:<20} n={len(s):>3}  "
                      f"resid {sum(s)/len(s):+.4f}%")
    print()

# --------------------------------------------------- Q5: the breadth duty
print("=" * 72)
print("Q5. SESSION DUTY: RSP vs SPY on CLOSES (no sentinel can watch this)")
print("=" * 72)
sp, rs = px["SPY"], px["RSP"]
days = sorted(set(sp) & set(rs))
for k in (1, 3, 5, 10):
    a, b = days[-1 - k], days[-1]
    g = (rs[b] / rs[a] - 1) * 100 - (sp[b] / sp[a] - 1) * 100
    print(f"  {k:>2}-session {a} -> {b}:  RSP {(rs[b]/rs[a]-1)*100:+.2f}%  "
          f"SPY {(sp[b]/sp[a]-1)*100:+.2f}%  gap {g:+.2f} pts")

gaps = [(rs[days[i]] / rs[days[i - 5]] - 1) * 100 - (sp[days[i]] / sp[days[i - 5]] - 1) * 100
        for i in range(5, len(days))]
cur = gaps[-1]
below = sum(1 for g in gaps if g <= cur) / len(gaps) * 100
srt = sorted(gaps)
print(f"\n  current 5-session gap {cur:+.2f} pts = {below:.2f}th percentile of {len(gaps)}")
print(f"  p1 {srt[len(srt)//100]:+.2f}  p5 {srt[len(srt)//20]:+.2f}  "
      f"median {srt[len(srt)//2]:+.2f}")
rsp50 = sum(rs[d] for d in days[-50:]) / 50
print(f"\n  RSP last close {rs[days[-1]]:.2f}  50-day {rsp50:.2f} "
      f"({(rs[days[-1]]/rsp50-1)*100:+.2f}%)  "
      f"52wk-high pct {rs[days[-1]]/max(rs[d] for d in days[-252:])*100:.1f}%")
print("  ^ 'RSP has gone NOWHERE' must be re-checked against this every session.")

# ------------------------------- Q6: the last two weeks, day by day (the check)
print("=" * 72)
print("Q6. RECENT TAPE: is my book living in the quadrant the measurement says")
print("    is worst for it? (residual = XLF/KRE move net of SPY beta)")
print("=" * 72)
print(f"  {'date':<12}{'SPY':>7}{'XLFres':>9}{'KREres':>9}"
      f"{'d2y':>7}{'d30y':>7}{'dslope':>8}  quadrant")
for r in rows[-12:]:
    if r["dslope"] > 0:
        q = "bear steep" if r["d30"] > 0 else "bull steep"
    else:
        q = "bear flat" if r["d30"] > 0 else "bull flat"
    print(f"  {str(r['date']):<12}{r['spy']:+7.2f}{r['xlf_res']:+9.3f}"
          f"{r['kre_res']:+9.3f}{r['d2']:+7.1f}{r['d30']:+7.1f}"
          f"{r['dslope']:+8.1f}  {q}")
