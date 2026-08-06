"""GLD shock days: how rare, and what follows for MY book?
Splits by whether TLT rose or fell that day - the exact discriminator my
`gold-regime-change` trigger note claims to use ("gold up WHILE long yields RISE").
Written 2026-08-05 morning session, the day the trigger fired on GLD +4.34%.
"""
import sys; sys.path.insert(0, 'tools')
import data as D
import numpy as np, pandas as pd

SYMS = ['GLD','SPY','XLF','RSP','XLV','TLT','KRE']
conn = D.db()
ser = {}
for s in SYMS:
    rows = D.get_bars(conn, s, 1500)
    idx = pd.to_datetime([r[0] for r in rows])
    ser[s] = pd.Series([float(r[4]) for r in rows], index=idx)
px = pd.DataFrame(ser).dropna()
ret = px.pct_change()*100
print(f"sample {px.index[0].date()} -> {px.index[-1].date()}  n={len(px)}")

g = ret['GLD'].dropna()
print(f"\nGLD daily move distribution (n={len(g)}):")
for p in [50,90,95,99,99.5]:
    print(f"  p{p:<5} {np.percentile(g,p):+.2f}%")
print(f"  max   {g.max():+.2f}%")
today = 4.34
print(f"  TODAY {today:+.2f}%  -> percentile {(g<today).mean()*100:.2f};  "
      f"{(g>=today).sum()} of {len(g)} days were this big or bigger")

shock = ret[ret['GLD']>=3.0].copy()
print(f"\n=== GLD >= +3.0% days: n={len(shock)} ===")
print("same-day co-moves (mean %):")
print(shock[SYMS].mean().round(3).to_string())

up = shock[shock['TLT']>0]; dn = shock[shock['TLT']<=0]
print(f"\nSPLIT by TLT: TLT UP/yields DOWN n={len(up)} (TODAY's case) | TLT DOWN/yields UP n={len(dn)}")

fwd = {h: (px.shift(-h)/px - 1)*100 for h in [1,3,5,10]}
cols = ['SPY','XLF','RSP','XLV','KRE']
for label, idx in [('ALL GLD>=3%', shock.index),
                   ('  yields DOWN (TODAY\'s configuration)', up.index),
                   ('  yields UP (my written regime signal)', dn.index)]:
    print(f"\n{label}  n={len(idx)}")
    print(f"  {'h':<4}" + "".join(f"{s:>9}" for s in cols))
    for h in [1,3,5,10]:
        row = fwd[h].loc[fwd[h].index.intersection(idx)]
        print(f"  {h:<4}" + "".join(f"{row[s].mean():>+9.2f}" for s in cols))

print(f"\nUNCONDITIONAL control (all days)")
print(f"  {'h':<4}" + "".join(f"{s:>9}" for s in cols))
for h in [1,3,5,10]:
    print(f"  {h:<4}" + "".join(f"{fwd[h][s].mean():>+9.2f}" for s in cols))
