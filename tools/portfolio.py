#!/usr/bin/env python3
"""Portfolio state: account, positions, open orders, recent fills → JSON.

Usage:
  python tools/portfolio.py                  # full state dump (agent's step 1)
  python tools/portfolio.py --report         # human report: equity vs baseline vs SPY
  python tools/portfolio.py --init-baseline  # record experiment start (run once at setup)
"""
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestTradeRequest
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import QueryOrderStatus
from alpaca.trading.requests import GetOrdersRequest

from common import agent_home, get_env_keys


def baseline_file() -> Path:
    """Resolved lazily: the plain state dump must work without an agent/baseline."""
    return agent_home() / "journal" / "experiment.json"


def spy_price(key: str, secret: str) -> float:
    data = StockHistoricalDataClient(key, secret)
    trade = data.get_stock_latest_trade(StockLatestTradeRequest(symbol_or_symbols="SPY"))
    return float(trade["SPY"].price)


def state_dump(client: TradingClient) -> dict:
    acct = client.get_account()
    positions = client.get_all_positions()
    open_orders = client.get_orders(
        GetOrdersRequest(status=QueryOrderStatus.OPEN, limit=50)
    )
    since = datetime.now(timezone.utc) - timedelta(days=7)
    recent = client.get_orders(
        GetOrdersRequest(status=QueryOrderStatus.CLOSED, after=since, limit=50)
    )
    return {
        "account": {
            "equity": float(acct.equity),
            "cash": float(acct.cash),
            "buying_power": float(acct.buying_power),
            "portfolio_value": float(acct.portfolio_value),
        },
        "positions": [
            {
                "symbol": p.symbol,
                "qty": float(p.qty),
                "avg_entry_price": float(p.avg_entry_price),
                "current_price": float(p.current_price),
                "market_value": float(p.market_value),
                "unrealized_pl": float(p.unrealized_pl),
                "unrealized_plpc": round(float(p.unrealized_plpc) * 100, 2),
            }
            for p in positions
        ],
        "open_orders": [
            {
                "symbol": o.symbol,
                "side": o.side.value,
                "type": o.type.value,
                "qty": float(o.qty) if o.qty else None,
                "notional": float(o.notional) if o.notional else None,
                "limit_price": float(o.limit_price) if o.limit_price else None,
                "client_order_id": o.client_order_id,
                "submitted_at": o.submitted_at.isoformat(),
            }
            for o in open_orders
        ],
        "recent_closed_orders_7d": [
            {
                "symbol": o.symbol,
                "side": o.side.value,
                "status": o.status.value,
                "filled_qty": float(o.filled_qty) if o.filled_qty else 0.0,
                "filled_avg_price": float(o.filled_avg_price) if o.filled_avg_price else None,
                "client_order_id": o.client_order_id,
                "filled_at": o.filled_at.isoformat() if o.filled_at else None,
            }
            for o in recent
        ],
    }


def init_baseline(client: TradingClient, key: str, secret: str) -> None:
    path = baseline_file()
    if path.exists():
        sys.exit(f"error: {path} already exists; delete it to re-init.")
    path.parent.mkdir(parents=True, exist_ok=True)
    acct = client.get_account()
    baseline = {
        "start_date": datetime.now(timezone.utc).date().isoformat(),
        "start_equity": float(acct.equity),
        "spy_start_price": spy_price(key, secret),
    }
    path.write_text(json.dumps(baseline, indent=2) + "\n")
    print(f"baseline recorded: {json.dumps(baseline)}")


def report(client: TradingClient, key: str, secret: str) -> None:
    path = baseline_file()
    if not path.exists():
        sys.exit("error: no baseline. Run `python tools/portfolio.py --init-baseline` first.")
    base = json.loads(path.read_text())
    acct = client.get_account()
    equity = float(acct.equity)
    spy_now = spy_price(key, secret)

    agent_ret = (equity / base["start_equity"] - 1) * 100
    spy_ret = (spy_now / base["spy_start_price"] - 1) * 100
    days = (datetime.now(timezone.utc).date() - datetime.fromisoformat(base["start_date"]).date()).days

    print(f"money-os report — day {days} (since {base['start_date']})")
    print(f"  equity:        ${equity:,.2f}  (started ${base['start_equity']:,.2f})")
    print(f"  agent return:  {agent_ret:+.2f}%")
    print(f"  SPY buy&hold:  {spy_ret:+.2f}%  (the honest benchmark)")
    print(f"  vs benchmark:  {agent_ret - spy_ret:+.2f} pts")


def main() -> None:
    key, secret = get_env_keys()
    client = TradingClient(key, secret, paper=True)
    if "--init-baseline" in sys.argv:
        init_baseline(client, key, secret)
    elif "--report" in sys.argv:
        report(client, key, secret)
    else:
        print(json.dumps(state_dump(client), indent=2))


if __name__ == "__main__":
    main()
