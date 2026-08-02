#!/usr/bin/env python3
"""Trade database: every order, its context, and its outcome. Feeds tca.py.

Written to automatically by trade.py at submit time; fills are synced lazily by
`python tools/trades_db.py sync` (run by tca.py and the weekly session).
"""
import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

from common import REPO

DB_PATH = REPO / "data" / "trades.db"


def db() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""CREATE TABLE IF NOT EXISTS orders(
        client_order_id TEXT PRIMARY KEY,
        agent TEXT, session TEXT, submitted_at TEXT,
        symbol TEXT, side TEXT, otype TEXT, tif TEXT,
        qty REAL, notional REAL, limit_price REAL, stop_price REAL,
        reason TEXT,
        bid_at_submit REAL, ask_at_submit REAL,
        status TEXT, filled_qty REAL, filled_avg_price REAL, filled_at TEXT,
        slippage_bps REAL)""")
    return conn


def record_order(order, agent: str, session: str, reason: str,
                 bid: float | None, ask: float | None) -> None:
    conn = db()
    conn.execute(
        """INSERT OR REPLACE INTO orders
           (client_order_id, agent, session, submitted_at, symbol, side, otype, tif,
            qty, notional, limit_price, stop_price, reason, bid_at_submit, ask_at_submit, status)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (order.client_order_id, agent, session,
         datetime.now(timezone.utc).isoformat(),
         order.symbol, order.side.value, order.type.value, order.time_in_force.value,
         float(order.qty) if order.qty else None,
         float(order.notional) if order.notional else None,
         float(order.limit_price) if getattr(order, "limit_price", None) else None,
         float(order.stop_price) if getattr(order, "stop_price", None) else None,
         reason, bid, ask, order.status.value))
    conn.commit()


def sync(client) -> int:
    """Pull current status/fills for all non-terminal recorded orders of this account."""
    from alpaca.trading.enums import QueryOrderStatus
    from alpaca.trading.requests import GetOrdersRequest
    conn = db()
    known = {r[0] for r in conn.execute(
        "SELECT client_order_id FROM orders WHERE status NOT IN ('filled','canceled','expired','rejected')")}
    if not known:
        return 0
    updated = 0
    orders = client.get_orders(GetOrdersRequest(status=QueryOrderStatus.ALL, limit=500))
    for o in orders:
        if o.client_order_id not in known:
            continue
        slip = None
        if o.filled_avg_price:
            row = conn.execute("SELECT side, bid_at_submit, ask_at_submit FROM orders "
                               "WHERE client_order_id=?", (o.client_order_id,)).fetchone()
            if row:
                side, bid, ask = row
                ref = ask if side == "buy" else bid  # expected fill vs quote at submit
                if ref:
                    sign = 1 if side == "buy" else -1
                    slip = sign * (float(o.filled_avg_price) - ref) / ref * 10000
        conn.execute(
            """UPDATE orders SET status=?, filled_qty=?, filled_avg_price=?, filled_at=?, slippage_bps=?
               WHERE client_order_id=?""",
            (o.status.value,
             float(o.filled_qty) if o.filled_qty else None,
             float(o.filled_avg_price) if o.filled_avg_price else None,
             o.filled_at.isoformat() if o.filled_at else None,
             slip, o.client_order_id))
        updated += 1
    conn.commit()
    return updated


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "sync":
        from alpaca.trading.client import TradingClient
        from common import get_env_keys
        key, secret = get_env_keys()
        n = sync(TradingClient(key, secret, paper=True))
        print(f"synced {n} orders")
    else:
        conn = db()
        for r in conn.execute(
                "SELECT submitted_at, agent, session, side, symbol, otype, status, "
                "filled_avg_price, slippage_bps, reason FROM orders ORDER BY submitted_at DESC LIMIT 25"):
            fp = f"@{r[7]:.2f}" if r[7] else ""
            sl = f"{r[8]:+.1f}bps" if r[8] is not None else ""
            print(f"{r[0][:16]} {r[1]:<10}{r[2]:<10}{r[3]:<5}{r[4]:<6}{r[5]:<8}{r[6]:<10}{fp:<10}{sl:<10}{r[9] or ''}")


if __name__ == "__main__":
    main()
