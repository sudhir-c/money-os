#!/usr/bin/env python3
"""Transaction-cost analysis + trade attribution from data/trades.db.

Round trips are reconstructed FIFO per symbol from filled orders. Every stat prints
its sample size — small-n numbers are labels, not conclusions.

Usage:
  python tools/tca.py report [--agent NAME]     # syncs fills first, then reports
"""
import argparse
import sqlite3
from collections import defaultdict

import trades_db
from common import get_env_keys


def report(agent: str | None) -> None:
    # sync fills for the current account (whoever's keys are loaded)
    from alpaca.trading.client import TradingClient
    key, secret = get_env_keys()
    trades_db.sync(TradingClient(key, secret, paper=True))

    conn = trades_db.db()
    where, params = "", []
    if agent:
        where, params = "WHERE agent=?", [agent]
    rows = conn.execute(
        f"SELECT agent, session, symbol, side, otype, filled_qty, filled_avg_price, "
        f"filled_at, slippage_bps, reason FROM orders {where} AND status='filled' ORDER BY filled_at"
        if where else
        "SELECT agent, session, symbol, side, otype, filled_qty, filled_avg_price, "
        "filled_at, slippage_bps, reason FROM orders WHERE status='filled' ORDER BY filled_at",
        params).fetchall()

    if not rows:
        print("no filled orders recorded yet — TCA starts working once trades flow through trade.py v2")
        return

    # --- slippage ---
    slips = [r[8] for r in rows if r[8] is not None]
    print(f"== execution quality  (n={len(slips)} fills with quote-at-submit)")
    if slips:
        avg = sum(slips) / len(slips)
        print(f"   avg slippage {avg:+.1f}bps  worst {max(slips):+.1f}bps  best {min(slips):+.1f}bps")
    else:
        print("   (no slippage samples yet)")

    # --- round trips, FIFO per (agent, symbol) ---
    lots: dict[tuple, list] = defaultdict(list)
    trips = []
    for agent_, session, sym, side, otype, qty, px, at, _slip, reason in rows:
        if not qty or not px:
            continue
        k = (agent_, sym)
        if side == "buy":
            lots[k].append([qty, px, at, reason])
        else:
            remaining = qty
            while remaining > 1e-9 and lots[k]:
                lot = lots[k][0]
                take = min(remaining, lot[0])
                trips.append({
                    "agent": agent_, "symbol": sym, "qty": take,
                    "entry_px": lot[1], "exit_px": px,
                    "entry_at": lot[2], "exit_at": at,
                    "reason": lot[3],
                    "pnl": (px - lot[1]) * take,
                    "ret_pct": (px / lot[1] - 1) * 100,
                })
                lot[0] -= take
                remaining -= take
                if lot[0] <= 1e-9:
                    lots[k].pop(0)

    print(f"\n== round trips  (n={len(trips)} closed)")
    if trips:
        wins = [t for t in trips if t["pnl"] > 0]
        losses = [t for t in trips if t["pnl"] <= 0]
        aw = sum(t["ret_pct"] for t in wins) / len(wins) if wins else 0
        al = sum(t["ret_pct"] for t in losses) / len(losses) if losses else 0
        print(f"   win rate {len(wins)}/{len(trips)}  avg win {aw:+.2f}%  avg loss {al:+.2f}%"
              + (f"  W/L ratio {abs(aw / al):.2f}" if al else ""))
        expectancy = sum(t["ret_pct"] for t in trips) / len(trips)
        print(f"   expectancy {expectancy:+.2f}%/trade  total P&L ${sum(t['pnl'] for t in trips):+,.2f}")
        if len(trips) < 30:
            print(f"   NOTE: n={len(trips)} < 30 — treat every number above as noise, not signal")

        print("\n== per-rule attribution")
        by_rule = defaultdict(list)
        for t in trips:
            by_rule[t["reason"] or "(untagged)"].append(t)
        for rule, ts in sorted(by_rule.items(), key=lambda kv: -sum(t["pnl"] for t in kv[1])):
            pnl = sum(t["pnl"] for t in ts)
            print(f"   {rule:<45} n={len(ts):<3} P&L ${pnl:+,.2f}")
    else:
        print("   (no closed round trips yet)")

    # open lots
    open_lots = [(k, lot) for k, lst in lots.items() for lot in lst]
    if open_lots:
        print(f"\n== open lots (n={len(open_lots)})")
        for (agent_, sym), lot in open_lots:
            print(f"   {agent_:<10}{sym:<6}{lot[0]:g} @ {lot[1]:.2f}  [{lot[3] or 'untagged'}]")


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("report")
    p.add_argument("--agent")
    args = ap.parse_args()
    report(args.agent)


if __name__ == "__main__":
    main()
