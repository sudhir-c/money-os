#!/usr/bin/env python3
"""Market data platform: local cache + CLI. The single source of price truth.

All bars are split/dividend-adjusted (Adjustment.ALL) — enforced here, centrally.
Never price a decision from an article or a memory; price it from this tool.

Usage:
  python tools/data.py refresh [SYM ...]      # incremental cache update (universe by default)
  python tools/data.py bars SYM [--days 60]   # adjusted OHLCV from cache
  python tools/data.py quote SYM [SYM ...]    # live NBBO: bid/ask/spread bps/last
  python tools/data.py snapshot SYM [SYM ...] # price, day%, vs 50d/200d, ATR14, 12-1/6-1, %52wk-high
  python tools/data.py earnings SYM           # earnings-date registry (with confidence tag)
  python tools/data.py earnings SYM --set 2026-09-02 --source ir --note "IR press release"
  python tools/data.py fred SERIES [--days 90]
"""
import argparse
import csv
import io
import json
import sqlite3
import sys
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

from alpaca.data.enums import Adjustment
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest, StockLatestQuoteRequest, StockLatestTradeRequest
from alpaca.data.timeframe import TimeFrame

from common import REPO, get_env_keys

DATA_DIR = REPO / "data"
DB = DATA_DIR / "market.db"
UNIVERSE = DATA_DIR / "universe.txt"
EARNINGS = DATA_DIR / "earnings.json"
BAR_HISTORY_DAYS = 600  # enough for 12-1 momentum + 200d MA with margin


def db() -> sqlite3.Connection:
    DATA_DIR.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB)
    conn.execute("""CREATE TABLE IF NOT EXISTS bars(
        symbol TEXT, date TEXT, open REAL, high REAL, low REAL, close REAL, volume REAL,
        PRIMARY KEY(symbol, date))""")
    conn.execute("""CREATE TABLE IF NOT EXISTS fred(
        series TEXT, date TEXT, value REAL, PRIMARY KEY(series, date))""")
    conn.execute("""CREATE TABLE IF NOT EXISTS meta(key TEXT PRIMARY KEY, value TEXT)""")
    return conn


def universe() -> list[str]:
    if not UNIVERSE.exists():
        return []
    syms = []
    for line in UNIVERSE.read_text().splitlines():
        line = line.split("#")[0].strip().upper()
        syms.extend(line.split())
    return syms


def data_client() -> StockHistoricalDataClient:
    key, secret = get_env_keys()
    return StockHistoricalDataClient(key, secret)


def refresh(symbols: list[str]) -> None:
    """Incrementally pull adjusted daily bars for symbols (default: universe)."""
    conn = db()
    client = data_client()
    # free-tier data feed rejects very recent end timestamps; stay 30 min behind
    end = datetime.now(timezone.utc) - timedelta(minutes=30)
    updated = 0
    for i in range(0, len(symbols), 50):  # batch requests
        batch = symbols[i:i + 50]
        starts = {}
        for s in batch:
            row = conn.execute("SELECT MAX(date) FROM bars WHERE symbol=?", (s,)).fetchone()
            if row[0]:
                starts[s] = datetime.fromisoformat(row[0]) - timedelta(days=5)  # overlap for adj revisions
            else:
                starts[s] = end - timedelta(days=BAR_HISTORY_DAYS)
        start = min(starts.values())
        req = StockBarsRequest(symbol_or_symbols=batch, timeframe=TimeFrame.Day,
                               start=start, end=end, adjustment=Adjustment.ALL)
        bars = client.get_stock_bars(req)
        for sym, blist in bars.data.items():
            for b in blist:
                conn.execute(
                    "INSERT OR REPLACE INTO bars VALUES (?,?,?,?,?,?,?)",
                    (sym, b.timestamp.date().isoformat(), b.open, b.high, b.low, b.close, b.volume))
                updated += 1
    conn.execute("INSERT OR REPLACE INTO meta VALUES ('last_refresh', ?)",
                 (datetime.now(timezone.utc).isoformat(),))
    conn.commit()
    print(f"refreshed {len(symbols)} symbols, {updated} bar rows upserted")


def get_bars(conn: sqlite3.Connection, sym: str, days: int) -> list[tuple]:
    return conn.execute(
        "SELECT date, open, high, low, close, volume FROM bars WHERE symbol=? "
        "ORDER BY date DESC LIMIT ?", (sym, days)).fetchall()[::-1]


def sma(closes: list[float], n: int) -> float | None:
    return sum(closes[-n:]) / n if len(closes) >= n else None


def atr14(rows: list[tuple]) -> float | None:
    if len(rows) < 15:
        return None
    trs = []
    for prev, cur in zip(rows[-15:-1], rows[-14:]):
        _, _, h, l, c, _ = cur
        pc = prev[4]
        trs.append(max(h - l, abs(h - pc), abs(l - pc)))
    return sum(trs) / len(trs)


def cmd_snapshot(symbols: list[str]) -> None:
    conn = db()
    hdr = f"{'sym':<6}{'close':>10}{'day%':>8}{'vs50d':>8}{'vs200d':>8}{'ATR%':>7}{'12-1':>8}{'6-1':>8}{'%52wh':>7}"
    print(hdr)
    print("-" * len(hdr))
    for sym in symbols:
        rows = get_bars(conn, sym, 400)
        if len(rows) < 30:
            print(f"{sym:<6}  (not in cache — run: data.py refresh {sym})")
            continue
        closes = [r[4] for r in rows]
        px = closes[-1]
        day = (px / closes[-2] - 1) * 100
        s50, s200 = sma(closes, 50), sma(closes, 200)
        v50 = f"{(px / s50 - 1) * 100:+.1f}%" if s50 else "—"
        v200 = f"{(px / s200 - 1) * 100:+.1f}%" if s200 else "—"
        a = atr14(rows)
        atrp = f"{a / px * 100:.2f}%" if a else "—"
        r121 = f"{(closes[-22] / closes[-252] - 1) * 100:+.1f}%" if len(closes) >= 252 else "—"
        r61 = f"{(closes[-22] / closes[-147] - 1) * 100:+.1f}%" if len(closes) >= 147 else "—"
        hi52 = max(closes[-252:]) if len(closes) >= 252 else max(closes)
        print(f"{sym:<6}{px:>10.2f}{day:>+7.2f}%{v50:>8}{v200:>8}{atrp:>7}{r121:>8}{r61:>8}{px / hi52 * 100:>6.1f}%")


def cmd_quote(symbols: list[str]) -> None:
    client = data_client()
    quotes = client.get_stock_latest_quote(StockLatestQuoteRequest(symbol_or_symbols=symbols))
    trades = client.get_stock_latest_trade(StockLatestTradeRequest(symbol_or_symbols=symbols))
    print(f"{'sym':<6}{'bid':>10}{'ask':>10}{'spread':>9}{'bps':>7}{'last':>10}")
    for sym in symbols:
        q, t = quotes.get(sym), trades.get(sym)
        if not q or not q.ask_price:
            print(f"{sym:<6}  (no quote — market closed or unknown symbol)")
            continue
        spread = q.ask_price - q.bid_price
        mid = (q.ask_price + q.bid_price) / 2
        bps = spread / mid * 10000 if mid else 0
        print(f"{sym:<6}{q.bid_price:>10.2f}{q.ask_price:>10.2f}{spread:>9.3f}{bps:>7.1f}{t.price if t else 0:>10.2f}")


def cmd_earnings(sym: str, set_date: str | None, source: str | None, note: str | None) -> None:
    reg = json.loads(EARNINGS.read_text()) if EARNINGS.exists() else {}
    if set_date:
        if source not in ("ir", "aggregator"):
            sys.exit("error: --source must be 'ir' or 'aggregator'")
        reg[sym.upper()] = {"date": set_date, "source": source, "note": note or "",
                            "recorded": datetime.now(timezone.utc).date().isoformat()}
        DATA_DIR.mkdir(exist_ok=True)
        EARNINGS.write_text(json.dumps(reg, indent=2, sort_keys=True) + "\n")
        print(f"recorded {sym.upper()} earnings {set_date} [{source}]")
        return
    e = reg.get(sym.upper())
    if not e:
        print(f"{sym.upper()}: no earnings date on record. Find it (company IR preferred) and "
              f"record with --set DATE --source ir|aggregator")
        return
    tag = "IR-VERIFIED" if e["source"] == "ir" else "UNCONFIRMED (aggregator — verify against company IR before relying on it)"
    print(f"{sym.upper()}: {e['date']}  [{tag}]  recorded {e['recorded']}  {e.get('note', '')}")


def cmd_fred(series: str, days: int) -> None:
    conn = db()
    # refresh series if stale (>1 day)
    row = conn.execute("SELECT MAX(date) FROM fred WHERE series=?", (series,)).fetchone()
    today = datetime.now(timezone.utc).date().isoformat()
    if not row[0] or row[0] < (datetime.now(timezone.utc) - timedelta(days=1)).date().isoformat():
        url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series}"
        with urllib.request.urlopen(url, timeout=30) as r:
            reader = csv.reader(io.TextIOWrapper(r, "utf-8"))
            next(reader)
            for date, val in reader:
                try:
                    conn.execute("INSERT OR REPLACE INTO fred VALUES (?,?,?)", (series, date, float(val)))
                except ValueError:
                    continue
        conn.commit()
    rows = conn.execute("SELECT date, value FROM fred WHERE series=? ORDER BY date DESC LIMIT ?",
                        (series, days)).fetchall()
    for date, val in rows[::-1]:
        print(f"{date}  {val}")


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("refresh"); p.add_argument("symbols", nargs="*")
    p = sub.add_parser("bars"); p.add_argument("symbol"); p.add_argument("--days", type=int, default=60)
    p = sub.add_parser("quote"); p.add_argument("symbols", nargs="+")
    p = sub.add_parser("snapshot"); p.add_argument("symbols", nargs="+")
    p = sub.add_parser("earnings"); p.add_argument("symbol")
    p.add_argument("--set", dest="set_date"); p.add_argument("--source"); p.add_argument("--note")
    p = sub.add_parser("fred"); p.add_argument("series"); p.add_argument("--days", type=int, default=30)
    args = ap.parse_args()

    if args.cmd == "refresh":
        syms = [s.upper() for s in args.symbols] or universe()
        if not syms:
            sys.exit("no symbols: pass some or populate data/universe.txt")
        refresh(syms)
    elif args.cmd == "bars":
        conn = db()
        for r in get_bars(conn, args.symbol.upper(), args.days):
            print(f"{r[0]}  o={r[1]:.2f} h={r[2]:.2f} l={r[3]:.2f} c={r[4]:.2f} v={int(r[5])}")
    elif args.cmd == "quote":
        cmd_quote([s.upper() for s in args.symbols])
    elif args.cmd == "snapshot":
        cmd_snapshot([s.upper() for s in args.symbols])
    elif args.cmd == "earnings":
        cmd_earnings(args.symbol, args.set_date, args.source, args.note)
    elif args.cmd == "fred":
        cmd_fred(args.series, args.days)


if __name__ == "__main__":
    main()
