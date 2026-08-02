#!/usr/bin/env python3
"""Order management: list, cancel, and — most importantly — reconcile.

`reconcile` enforces Risk Rulebook rule 10 in code: every position held must have a
live protective exit (stop, stop-limit, bracket leg, or trailing stop) resting at the
broker. Run it at every trade window.

Usage:
  python tools/orders.py list
  python tools/orders.py cancel <client_order_id>
  python tools/orders.py cancel --symbol SYM        # all open orders in SYM
  python tools/orders.py reconcile                  # report unprotected positions
"""
import argparse
import sys

from alpaca.trading.client import TradingClient
from alpaca.trading.enums import QueryOrderStatus
from alpaca.trading.requests import GetOrdersRequest

from common import get_env_keys

PROTECTIVE_TYPES = {"stop", "stop_limit", "trailing_stop"}


def open_orders(client):
    return client.get_orders(GetOrdersRequest(status=QueryOrderStatus.OPEN, limit=100))


def cmd_list(client) -> None:
    orders = open_orders(client)
    if not orders:
        print("no open orders")
        return
    for o in orders:
        px = o.limit_price or o.stop_price or ""
        print(f"{o.symbol:<6}{o.side.value:<5}{o.type.value:<14}{o.time_in_force.value:<5}"
              f"qty={o.qty or o.notional:<10} px={px:<10} [{o.client_order_id}]")


def cmd_cancel(client, order_id: str | None, symbol: str | None) -> None:
    orders = open_orders(client)
    victims = [o for o in orders
               if (order_id and o.client_order_id == order_id)
               or (symbol and o.symbol == symbol.upper())]
    if not victims:
        sys.exit("no matching open orders")
    for o in victims:
        client.cancel_order_by_id(o.id)
        print(f"canceled {o.symbol} {o.side.value} {o.type.value} [{o.client_order_id}]")


def cmd_reconcile(client) -> int:
    positions = {p.symbol: float(p.qty) for p in client.get_all_positions()}
    orders = open_orders(client)
    protected: dict[str, float] = {}
    orphans = []
    for o in orders:
        is_protective = (o.side.value == "sell" and o.type.value in PROTECTIVE_TYPES)
        if is_protective:
            protected[o.symbol] = protected.get(o.symbol, 0.0) + float(o.qty or 0)
        if o.symbol not in positions and o.side.value == "sell":
            orphans.append(o)

    problems = 0
    for sym, qty in positions.items():
        cover = protected.get(sym, 0.0)
        if cover <= 0:
            print(f"UNPROTECTED: {sym} {qty} shares — no stop resting. "
                  f"Place one now (trade.py sell {sym} --qty {int(qty)} --stop <px> --tif gtc).")
            problems += 1
        elif cover < qty:
            print(f"PARTIAL: {sym} {qty} held, only {cover} covered by stops — top up.")
            problems += 1
        else:
            print(f"ok: {sym} {qty} held, {cover} covered")
    for o in orphans:
        print(f"ORPHAN: sell {o.symbol} {o.type.value} [{o.client_order_id}] but no position — cancel it "
              f"(orders.py cancel {o.client_order_id}).")
        problems += 1
    if problems == 0:
        print("reconcile clean: every position protected, no orphans")
    return 0 if problems == 0 else 1


def main() -> None:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list")
    p = sub.add_parser("cancel")
    p.add_argument("order_id", nargs="?")
    p.add_argument("--symbol")
    sub.add_parser("reconcile")
    args = ap.parse_args()

    key, secret = get_env_keys()
    client = TradingClient(key, secret, paper=True)

    if args.cmd == "list":
        cmd_list(client)
    elif args.cmd == "cancel":
        if not args.order_id and not args.symbol:
            sys.exit("cancel needs a client_order_id or --symbol")
        cmd_cancel(client, args.order_id, args.symbol)
    elif args.cmd == "reconcile":
        sys.exit(cmd_reconcile(client))


if __name__ == "__main__":
    main()
