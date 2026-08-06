import sqlite3
conn = sqlite3.connect("data/market.db")

def bars(s, n=420):
    return conn.execute("SELECT date,open,high,low,close FROM bars WHERE symbol=? ORDER BY date DESC LIMIT ?", (s, n)).fetchall()[::-1]

def wilder_atr(rows, n=14):
    trs = []
    for prev, cur in zip(rows[:-1], rows[1:]):
        h, l, c = cur[1+1], cur[2+1], cur[4-1]  # placeholder
    return None

def wilder(rows, n=14):
    # rows: (date, open, high, low, close)
    trs = []
    for prev, cur in zip(rows[:-1], rows[1:]):
        h, l = cur[2], cur[3]
        pc = prev[4]
        trs.append(max(h-l, abs(h-pc), abs(l-pc)))
    if len(trs) < n: return None
    atr = sum(trs[:n]) / n
    for tr in trs[n:]:
        atr = (atr*(n-1) + tr) / n
    return atr

syms = ["SPY","RSP","VEU","XLI","XLE","XLK","QQQ","IWM","XLF","SOXX","SGOV","BIL"]
print(f"{'sym':<6}{'close':>10}{'200d':>10}{'vs200':>8}{'ATRw14':>9}{'ATR%':>7}")
data = {}
for s in syms:
    r = bars(s)
    c = [x[4] for x in r]
    sma200 = sum(c[-200:])/200 if len(c) >= 200 else None
    a = wilder(r)
    data[s] = (c, r, sma200, a)
    print(f"{s:<6}{c[-1]:>10.2f}{(sma200 or 0):>10.2f}{(c[-1]/sma200-1)*100:>+7.2f}%{a:>9.4f}{a/c[-1]*100:>6.2f}%")

print()
print("Momentum, library convention c[-22]/c[-(21N+1)] on 2026-08-05 closes")
print(f"{'sym':<6}{'6-1':>9}{'9-1':>9}{'12-1':>9}{'blend':>9}{'vsSPY':>9}")
def leg(c, N):
    return (c[-22]/c[-(21*N+1)] - 1)*100
rows = {}
for s in syms:
    c = data[s][0]
    l6, l9, l12 = leg(c,6), leg(c,9), leg(c,12)
    rows[s] = (l6,l9,l12,(l6+l9+l12)/3)
spyb = rows["SPY"][3]
for s in syms:
    l6,l9,l12,b = rows[s]
    print(f"{s:<6}{l6:>+9.2f}{l9:>+9.2f}{l12:>+9.2f}{b:>+9.2f}{b-spyb:>+9.2f}")
print(f"\nSPY 6-1 leg = {rows['SPY'][0]:+.2f}")
for s in ["RSP","VEU","XLE","XLI"]:
    print(f"  {s} 6-1 {rows[s][0]:+.2f} vs SPY {rows['SPY'][0]:+.2f} -> {rows[s][0]-rows['SPY'][0]:+.2f}pp")

print()
print("Today's bar vs resting stops")
stops = {"VEU":81.48,"RSP":214.40,"XLI":167.00,"SGOV":99.50}
for s,st in stops.items():
    r = data[s][1][-1]
    print(f"  {s}: low {r[3]:.2f} close {r[4]:.2f} stop {st:.2f} -> low is {(r[3]/st-1)*100:+.2f}% above stop")

print()
print("Rule 8 trail state (trails on CLOSES)")
entries = {"VEU":(82.89,"2026-08-03"),"RSP":(216.44,"2026-08-03"),"XLI":(184.95,"2026-08-04")}
for s,(e,d) in entries.items():
    c,r,_,a = data[s]
    since = [x for x in r if x[0] >= d]
    hc = max(x[4] for x in since)
    hcd = [x[0] for x in since if x[4]==hc][0]
    arm = e + a
    print(f"  {s}: entry {e:.2f} ATRw {a:.4f} arm@{arm:.2f} | highest close since {d} = {hc:.2f} ({hcd}) "
          f"| armed={hc>=arm} | trail = {hc-2.5*a:.2f} | resting {stops[s]:.2f}")
