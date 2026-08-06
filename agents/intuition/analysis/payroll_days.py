"""How big is a PAYROLL DAY actually, for the book I own?

WHY THIS EXISTS (written 2026-08-05 evening, two sessions before the 8/7 print).
My handoff calls Friday "the decisive event" and says the soft branch is "the
worst measured state for financials," citing the dovish-flattener quadrant.
Tonight I re-ran that measurement (xlf_curve_quadrants.py, now n=46) and the
number is XLF residual -0.111%/DAY. XLF is 22.9% of my equity, so that quadrant
costs my book ~2.5 basis points. I have been calling a 2.5bp effect "decisive"
for five sessions and pre-committing my cash to it.

The defect is NOT that the earlier measurement was wrong. It is that I measured
the SIGN and never looked at the MAGNITUDE, then wrote doctrine off the sign.

The legitimate counter-argument, and the reason for this script: a payroll day
is not an average day. The quadrant average is taken over ~46 mostly-quiet
sessions; the conditional distribution ON A RELEASE DAY has fatter tails. So
"the average is small" does not settle "the release day is small." That is an
empirical question and it takes twenty minutes.

METHOD. BLS releases the employment report on the first Friday of the month in
the large majority of months (it slips when the first Friday is very early or a
holiday intervenes; I flag those rather than hand-tune them). I take that as a
proxy set, then compare release days against all other days for:
  - absolute move size (is the day genuinely bigger?)
  - my actual book (XLF 20sh / RSP 5sh / XLV 5sh + $1,988.24 cash)
  - the tail, which is the thing that would actually hurt: worst outcomes.

Prices are force-adjusted Alpaca bars via tools/data.py (lesson 1). No FRED
conditioning here on purpose - I cannot know Friday's rate reaction in advance,
so the useful question is the UNCONDITIONAL size of a payroll day, not a
quadrant I can only label afterwards.
"""
import sys

sys.path.insert(0, "tools")
import data as D
import numpy as np
import pandas as pd

SYMS = ["SPY", "XLF", "RSP", "XLV", "KRE", "TLT"]
POS = {"XLF": 20, "RSP": 5, "XLV": 5}
CASH = 1988.24

conn = D.db()
ser = {}
for s in SYMS:
    rows = D.get_bars(conn, s, 1500)
    ser[s] = pd.Series([float(r[4]) for r in rows],
                       index=pd.to_datetime([r[0] for r in rows]))
px = pd.DataFrame(ser).dropna()
ret = px.pct_change() * 100

# my actual book, marked daily
book = pd.Series(CASH + sum(POS[s] * px[s] for s in POS), index=px.index)
bret = book.pct_change() * 100

print(f"sample {px.index[0].date()} -> {px.index[-1].date()}   n={len(px)} sessions")

# ---- identify first-Friday-of-month sessions -------------------------------
first_fri = []
for (y, m), grp in px.groupby([px.index.year, px.index.month]):
    fris = [d for d in grp.index if d.weekday() == 4]
    if fris:
        first_fri.append(fris[0])
first_fri = pd.DatetimeIndex(first_fri)
# BLS convention: if the first Friday falls on the 1st or 2nd, the report is
# usually pushed to the SECOND Friday (reference-week timing). Flag, don't hide.
early = [d for d in first_fri if d.day <= 2]
if early:
    print(f"\n!! {len(early)} 'first Fridays' fall on the 1st/2nd of the month "
          f"({', '.join(str(d.date()) for d in early)}).")
    print("   BLS typically releases the SECOND Friday in those months, so these")
    print("   are probably NOT release days. Reported both ways below.")

alt = pd.DatetimeIndex([
    ([d for d in px.index if d.weekday() == 4 and d.month == f.month and d.year == f.year][1]
     if f.day <= 2 else f)
    for f in first_fri
])


def describe(label, days):
    mask = px.index.isin(days)
    other = ~mask & (px.index > px.index[0])
    print(f"\n{'='*72}\n{label}   n={mask.sum()} release days vs {other.sum()} other\n{'='*72}")
    hdr = f"{'series':<8}{'rel mean':>10}{'oth mean':>10}{'rel |mv|':>10}{'oth |mv|':>10}{'ratio':>8}{'rel sd':>9}{'oth sd':>9}"
    print(hdr)
    print("-" * len(hdr))
    for s in ["SPY", "XLF", "RSP", "XLV", "KRE", "TLT"]:
        r, o = ret[s][mask].dropna(), ret[s][other].dropna()
        print(f"{s:<8}{r.mean():>+9.3f}%{o.mean():>+9.3f}%{r.abs().mean():>9.3f}%"
              f"{o.abs().mean():>9.3f}%{r.abs().mean()/o.abs().mean():>7.2f}x"
              f"{r.std():>8.3f}%{o.std():>8.3f}%")
    r, o = bret[mask].dropna(), bret[other].dropna()
    print(f"{'MY BOOK':<8}{r.mean():>+9.3f}%{o.mean():>+9.3f}%{r.abs().mean():>9.3f}%"
          f"{o.abs().mean():>9.3f}%{r.abs().mean()/o.abs().mean():>7.2f}x"
          f"{r.std():>8.3f}%{o.std():>8.3f}%")

    print(f"\n  THE TAIL — what a bad payroll day has actually cost this book:")
    worst = r.nsmallest(6)
    for d, v in worst.items():
        print(f"    {d.date()}  book {v:>+6.2f}%   SPY {ret['SPY'][d]:>+6.2f}%   "
              f"XLF {ret['XLF'][d]:>+6.2f}%   RSP {ret['RSP'][d]:>+6.2f}%   XLV {ret['XLV'][d]:>+6.2f}%")
    print(f"    worst release day for the book: {r.min():+.2f}%")
    print(f"    5th pct of ALL other days:      {o.quantile(0.05):+.2f}%")
    print(f"    1st pct of ALL other days:      {o.quantile(0.01):+.2f}%")
    print(f"    -> a bad payroll day is {'INSIDE' if r.min() > o.quantile(0.01) else 'BEYOND'}"
          f" the 1st percentile of ordinary days")

    print(f"\n  DOLLARS on ${book.iloc[-1]:,.2f} of equity:")
    print(f"    mean absolute payroll-day move: ${abs(r).mean()/100*book.iloc[-1]:,.2f}")
    print(f"    worst observed payroll day:     ${r.min()/100*book.iloc[-1]:,.2f}")
    print(f"    XLF-only, at the -0.111%/day dovish-flattener residual: "
          f"${-0.111/100*POS['XLF']*px['XLF'].iloc[-1]:,.2f}")


describe("A. proxy = FIRST Friday of every month", first_fri)
describe("B. proxy = BLS-adjusted (2nd Friday when 1st falls on the 1st/2nd)", alt)

print(f"\n{'='*72}\nWHAT THIS DOES AND DOES NOT SETTLE\n{'='*72}")
print("""  The proxy is dates, not confirmed BLS release dates - some days counted
  here were not payroll days and some payroll days are missed. That biases the
  release-day statistics TOWARD the ordinary-day statistics (contamination
  dilutes any real effect), so if the measured effect is small it could be the
  proxy rather than the truth. Read a SMALL number here as 'not demonstrated',
  not as 'demonstrated to be zero'.
  The sample is also short and covers a single, mostly-rising regime.""")
