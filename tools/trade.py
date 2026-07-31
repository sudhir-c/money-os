#!/usr/bin/env python3
"""Execute trades on the Alpaca PAPER account, with hard guardrails.

Usage:
  python tools/trade.py buy  SYMBOL --notional 500            # market buy in $
  python tools/trade.py buy  SYMBOL --qty 3 --limit 187.50    # limit buy
  python tools/trade.py sell SYMBOL --qty 3                   # market sell
  python tools/trade.py sell SYMBOL --all                     # close position
  python tools/trade.py buy  SYMBOL --notional 500 \
         --take-profit 210 --stop-loss 180                    # bracket order
  python tools/trade.py buy  SYMBOL --qty 5 --take-profit 210 \
         --stop-loss 180 --tif gtc                            # bracket that survives the close
  python tools/trade.py sell SYMBOL --qty 5 --stop 165.01 --tif gtc
                                                              # protective GTC stop, no target
                                                              # (Rulebook rule 8: momentum entries
                                                              #  get a stop and NO profit target)

Guardrails (enforced here, not just in the prompt):
  - paper account only (paper=True hardwired)
  - long-only: sells limited to existing position size; no shorting
  - max 25% of current equity in any one position at purchase time
  - max 8 orders per session (MONEYOS_SESSION env, set by run-trader.sh)
  - symbol must be an active, tradable US equity/ETF on Alpaca
"""
import argparse
import os
import sys
from datetime import datetime, timezone

from alpaca.trading.client import TradingClient
from alpaca.trading.enums import AssetClass, OrderSide, QueryOrderStatus, TimeInForce
from alpaca.trading.requests import (
    GetOrdersRequest,
    LimitOrderRequest,
    MarketOrderRequest,
    StopLossRequest,
    StopOrderRequest,
    TakeProfitRequest,
)

from common import get_env_keys

MAX_POSITION_PCT = 0.25
MAX_ORDERS_PER_SESSION = 8


def die(msg: str) -> None:
    sys.exit(f"REJECTED: {msg}")


def session_prefix() -> str:
    agent = os.environ.get("MONEYOS_AGENT", "scholar")
    session = os.environ.get("MONEYOS_SESSION", "manual")
    today = datetime.now(timezone.utc).astimezone().date().isoformat()
    return f"{agent}-{session}-{today}"


def next_order_id(client: TradingClient) -> str:
    """Build client_order_id '<session>-<date>-<n>' and enforce the per-session cap."""
    prefix = session_prefix()
    start_of_day = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    orders = client.get_orders(
        GetOrdersRequest(status=QueryOrderStatus.ALL, after=start_of_day, limit=500)
    )
    count = sum(1 for o in orders if (o.client_order_id or "").startswith(prefix))
    if count >= MAX_ORDERS_PER_SESSION:
        die(f"session order cap reached ({MAX_ORDERS_PER_SESSION} orders for {prefix}). HOLD instead.")
    return f"{prefix}-{count + 1}"


def check_symbol(client: TradingClient, symbol: str) -> None:
    try:
        asset = client.get_asset(symbol)
    except Exception:
        die(f"unknown symbol {symbol!r}")
    if asset.asset_class != AssetClass.US_EQUITY:
        die(f"{symbol} is not a US equity/ETF (class={asset.asset_class.value})")
    if not asset.tradable:
        die(f"{symbol} is not tradable on Alpaca")


def check_buy_size(client: TradingClient, symbol: str, order_value: float) -> None:
    acct = client.get_account()
    equity = float(acct.equity)
    cash = float(acct.cash)
    if order_value > cash:
        die(f"insufficient cash: order ${order_value:,.2f} > cash ${cash:,.2f} (no margin)")
    existing = 0.0
    for p in client.get_all_positions():
        if p.symbol == symbol:
            existing = float(p.market_value)
    limit = MAX_POSITION_PCT * equity
    if existing + order_value > limit:
        die(
            f"position cap: {symbol} would be ${existing + order_value:,.2f}, "
            f"max is ${limit:,.2f} ({MAX_POSITION_PCT:.0%} of ${equity:,.2f} equity)"
        )


def estimate_value(client: TradingClient, symbol: str, qty: float | None,
                   notional: float | None, limit_price: float | None) -> float:
    if notional is not None:
        return notional
    assert qty is not None
    if limit_price is not None:
        return qty * limit_price
    # market order by qty: estimate with the position/asset latest price via a tiny
    # notional-free path — use last trade from the data API-free trading endpoint
    from alpaca.data.historical import StockHistoricalDataClient
    from alpaca.data.requests import StockLatestTradeRequest
    key, secret = get_env_keys()
    data = StockHistoricalDataClient(key, secret)
    trade = data.get_stock_latest_trade(StockLatestTradeRequest(symbol_or_symbols=symbol))
    return qty * float(trade[symbol].price)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("side", choices=["buy", "sell"])
    ap.add_argument("symbol")
    ap.add_argument("--qty", type=float)
    ap.add_argument("--notional", type=float, help="dollar amount (fractional shares)")
    ap.add_argument("--all", action="store_true", help="sell: close entire position")
    ap.add_argument("--limit", type=float, help="limit price (omit for market order)")
    ap.add_argument("--take-profit", type=float, help="bracket: take-profit limit price")
    ap.add_argument("--stop-loss", type=float, help="bracket: stop-loss trigger price")
    ap.add_argument("--stop", type=float,
                    help="sell: standalone protective stop price (Rulebook rule 8/10)")
    ap.add_argument("--tif", choices=["day", "gtc"], default="day",
                    help="time in force; gtc keeps protective exits alive overnight "
                         "(gtc requires whole-share --qty)")
    args = ap.parse_args()

    symbol = args.symbol.upper()
    key, secret = get_env_keys()
    client = TradingClient(key, secret, paper=True)  # paper hardwired

    check_symbol(client, symbol)

    if args.side == "sell":
        held = 0.0
        for p in client.get_all_positions():
            if p.symbol == symbol:
                held = float(p.qty)
        if held <= 0:
            die(f"no position in {symbol}; shorting is not allowed")
        if args.all:
            order_id = next_order_id(client)  # cap check before closing
            resp = client.close_position(symbol)
            print(f"CLOSED {symbol}: qty={resp.qty} client_order_id~{order_id}")
            return
        if not args.qty:
            die("sell requires --qty or --all")
        if args.qty > held:
            die(f"sell qty {args.qty} > held {held} ({symbol}); shorting is not allowed")
        qty, notional = args.qty, None
    else:
        if bool(args.qty) == bool(args.notional):
            die("buy requires exactly one of --qty or --notional")
        qty, notional = args.qty, args.notional
        value = estimate_value(client, symbol, qty, notional, args.limit)
        check_buy_size(client, symbol, value)

    side = OrderSide.BUY if args.side == "buy" else OrderSide.SELL
    bracket = bool(args.take_profit or args.stop_loss)

    if args.stop is not None:
        if args.side != "sell":
            die("--stop is a protective sell stop; use --stop-loss for a bracket entry")
        if bracket or args.limit:
            die("--stop cannot be combined with --limit or bracket legs "
                "(Alpaca rejects self-crossing exits as wash trades; use one exit order)")
    # Alpaca: brackets and GTC are whole-share only — no fractional/notional legs.
    if args.tif == "gtc" or bracket:
        why = "bracket" if bracket else "gtc"
        if notional is not None:
            die(f"{why} orders cannot use --notional (whole shares only); use --qty")
        if qty is None or float(qty) != int(qty):
            die(f"{why} orders require a whole-share --qty (got {qty})")
        qty = float(int(qty))

    order_id = next_order_id(client)
    tif = TimeInForce.GTC if args.tif == "gtc" else TimeInForce.DAY

    common = dict(
        symbol=symbol,
        side=side,
        client_order_id=order_id,
        time_in_force=tif,
        qty=qty,
        notional=notional,
    )
    if bracket:
        if not (args.take_profit and args.stop_loss):
            die("bracket orders need both --take-profit and --stop-loss")
        common["order_class"] = "bracket"
        common["take_profit"] = TakeProfitRequest(limit_price=args.take_profit)
        common["stop_loss"] = StopLossRequest(stop_price=args.stop_loss)

    if args.stop is not None:
        req = StopOrderRequest(stop_price=args.stop, **common)
    elif args.limit:
        req = LimitOrderRequest(limit_price=args.limit, **common)
    else:
        req = MarketOrderRequest(**common)

    order = client.submit_order(req)
    print(
        f"SUBMITTED {order.side.value} {symbol} "
        f"qty={order.qty} notional={order.notional} type={order.type.value} "
        f"status={order.status.value} client_order_id={order.client_order_id}"
    )


if __name__ == "__main__":
    main()
