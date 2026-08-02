#!/usr/bin/env python3
"""Daily-bar backtest engine over the local cache. Turns Saturday arguments into numbers.

Design principles (momentum lesson L4 as infrastructure):
- Mandatory train/validate split: results are ALWAYS reported separately for the two
  periods; a strategy tuned on the train window must survive the validate window.
- Costs are charged on every trade (spread model by liquidity tier).
- Same report format every run, with sample-size warnings printed inline.

Usage:
  python tools/backtest.py run --strategy dual_momentum --start 2024-08-01
  python tools/backtest.py run --strategy ma_filter --params '{"symbol":"SPY","ma":200}'
  python tools/backtest.py run --strategy rsi2 --params '{"symbol":"QQQ"}'
  python tools/backtest.py run --strategy custom --file agents/<a>/analysis/mystrat.py
  python tools/backtest.py list

Custom strategy file contract: define `def strategy(ctx)` returning target weights
{symbol: weight} for ctx.date, using ONLY ctx.history(sym, n) (bars strictly before
ctx.date — lookahead is structurally impossible).
"""
import argparse
import importlib.util
import json
import sqlite3
import sys
from datetime import date, datetime, timedelta

from common import REPO

DB = REPO / "data" / "market.db"
COST_BPS = {"etf_mega": 1, "large": 5, "mid": 15}  # per side, execution.md tiers
DEFAULT_COST = 5
MEGA_ETFS = {"SPY", "QQQ", "IWM", "VEU", "VXUS", "BND", "AGG", "BIL", "SGOV", "RSP", "GLD", "EFA", "IEFA", "DBC"}


class Ctx:
    """Point-in-time data access. history() never returns bars >= current date."""

    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.date: str = ""
        self._cache: dict[str, list[tuple[str, float]]] = {}

    def _closes(self, sym: str) -> list[tuple[str, float]]:
        if sym not in self._cache:
            self._cache[sym] = self.conn.execute(
                "SELECT date, close FROM bars WHERE symbol=? ORDER BY date", (sym,)).fetchall()
        return self._cache[sym]

    def history(self, sym: str, n: int) -> list[float]:
        rows = self._closes(sym)
        past = [c for d, c in rows if d < self.date]
        return past[-n:]

    def price(self, sym: str) -> float | None:
        rows = self._closes(sym)
        for d, c in rows:
            if d == self.date:
                return c
        return None


# ---------- built-in strategies ----------

def dual_momentum(ctx: Ctx) -> dict[str, float]:
    """GEM-style: SPY vs VEU vs BIL on blended 6/9/12-month returns, monthly."""
    def blend(sym):
        h = ctx.history(sym, 253)
        if len(h) < 253:
            return None
        r = lambda n: h[-22] / h[-n] - 1  # skip most recent month
        return (r(127) + r(190) + r(253)) / 3
    scores = {s: blend(s) for s in ("SPY", "VEU", "BIL")}
    if any(v is None for v in scores.values()):
        return {}
    if max(scores["SPY"], scores["VEU"]) <= scores["BIL"]:
        return {"BIL": 1.0}
    return {"SPY": 1.0} if scores["SPY"] >= scores["VEU"] else {"VEU": 1.0}


def ma_filter(ctx: Ctx, symbol="SPY", ma=200) -> dict[str, float]:
    h = ctx.history(symbol, ma)
    if len(h) < ma:
        return {}
    return {symbol: 1.0} if h[-1] > sum(h) / len(h) else {"BIL": 1.0}


def rsi2(ctx: Ctx, symbol="SPY") -> dict[str, float]:
    h = ctx.history(symbol, 250)
    if len(h) < 210:
        return {}
    sma200 = sum(h[-200:]) / 200
    if h[-1] <= sma200:
        return {}
    gains = losses = 0.0
    for a, b in zip(h[-3:-1], h[-2:]):
        d = b - a
        gains += max(d, 0); losses += max(-d, 0)
    rs = gains / losses if losses else 99
    r = 100 - 100 / (1 + rs)
    sma5 = sum(h[-5:]) / 5
    if r < 10:
        return {symbol: 1.0}
    if h[-1] > sma5:
        return {}
    return None  # None = keep yesterday's book (hold through the trade)


BUILTINS = {"dual_momentum": dual_momentum, "ma_filter": ma_filter, "rsi2": rsi2}


# ---------- engine ----------

def cost_bps(sym: str) -> float:
    return COST_BPS["etf_mega"] if sym in MEGA_ETFS else DEFAULT_COST


def run(strategy, start: str, end: str, rebalance_days: int) -> dict:
    conn = sqlite3.connect(DB)
    ctx = Ctx(conn)
    days = [r[0] for r in conn.execute(
        "SELECT DISTINCT date FROM bars WHERE symbol='SPY' AND date>=? AND date<=? ORDER BY date",
        (start, end))]
    if len(days) < 40:
        sys.exit(f"only {len(days)} trading days cached in [{start}..{end}] — refresh more history")

    equity, book = 1.0, {}
    curve, trades = [], 0
    for i, d in enumerate(days):
        ctx.date = d
        # mark book
        if book:
            ret = 0.0
            for sym, w in book.items():
                h = ctx.history(sym, 2)
                px = ctx.price(sym)
                if px and h:
                    ret += w * (px / h[-1] - 1)
            equity *= 1 + ret
        if i % rebalance_days == 0:
            target = strategy(ctx)
            if target is not None and target != book:
                turnover = sum(abs(target.get(s, 0) - book.get(s, 0))
                               for s in set(target) | set(book))
                for s in set(target) | set(book):
                    dw = abs(target.get(s, 0) - book.get(s, 0))
                    equity *= 1 - dw * cost_bps(s) / 10000
                if turnover > 0:
                    trades += 1
                book = target
        curve.append((d, equity))

    rets = [(b / a - 1) for (_, a), (_, b) in zip(curve, curve[1:])]
    n = len(rets)
    years = n / 252
    cagr = (curve[-1][1] ** (1 / years) - 1) * 100 if years > 0.2 else None
    mean = sum(rets) / n if n else 0
    var = sum((r - mean) ** 2 for r in rets) / n if n else 0
    sharpe = (mean / var ** 0.5 * 252 ** 0.5) if var else 0
    peak, maxdd = 0, 0
    for _, e in curve:
        peak = max(peak, e)
        maxdd = min(maxdd, e / peak - 1)
    return {"start": curve[0][0], "end": curve[-1][0], "days": n,
            "total_return_pct": (curve[-1][1] - 1) * 100,
            "cagr_pct": cagr, "sharpe": sharpe, "max_dd_pct": maxdd * 100,
            "rebalances": trades}


def report(name: str, strategy, start: str, end: str, rebalance_days: int) -> None:
    split = (datetime.fromisoformat(start).date()
             + (datetime.fromisoformat(end).date() - datetime.fromisoformat(start).date()) * 2 // 3)
    print(f"strategy: {name}   period {start} → {end}   rebalance every {rebalance_days}d")
    print(f"split: train {start} → {split}, validate {split} → {end} (out-of-sample)\n")
    for label, s, e in (("TRAIN", start, split.isoformat()), ("VALIDATE", split.isoformat(), end)):
        r = run(strategy, s, e, rebalance_days)
        cagr = f"{r['cagr_pct']:.1f}%" if r["cagr_pct"] is not None else "n/a(short)"
        print(f"{label:<9} ret {r['total_return_pct']:+7.2f}%  cagr {cagr:>10}  "
              f"sharpe {r['sharpe']:5.2f}  maxDD {r['max_dd_pct']:6.2f}%  "
              f"rebalances {r['rebalances']} over {r['days']}d")
        if r["rebalances"] < 10:
            print(f"          NOTE: only {r['rebalances']} rebalances — treat as anecdote, not statistics")
    print("\nRule: a strategy is PROPOSABLE only if VALIDATE holds up. "
          "If TRAIN shines and VALIDATE doesn't, you fitted noise.")
    print("Cache depth limits history (~600d); for longer studies, refresh with more days first.")


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list")
    p = sub.add_parser("run")
    p.add_argument("--strategy", required=True)
    p.add_argument("--file", help="path to custom strategy .py (with --strategy custom)")
    p.add_argument("--params", default="{}")
    p.add_argument("--start", default=(date.today() - timedelta(days=580)).isoformat())
    p.add_argument("--end", default=date.today().isoformat())
    p.add_argument("--rebalance-days", type=int, default=21)
    args = ap.parse_args()

    if args.cmd == "list":
        for k in BUILTINS:
            print(k)
        return

    params = json.loads(args.params)
    if args.strategy == "custom":
        if not args.file:
            sys.exit("custom needs --file")
        spec = importlib.util.spec_from_file_location("strat", args.file)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        fn = mod.strategy
        name = args.file
    else:
        base = BUILTINS.get(args.strategy)
        if not base:
            sys.exit(f"unknown strategy; builtin options: {', '.join(BUILTINS)}")
        fn = (lambda ctx: base(ctx, **params)) if params else base
        name = args.strategy
    report(name, fn, args.start, args.end, args.rebalance_days)


if __name__ == "__main__":
    main()
