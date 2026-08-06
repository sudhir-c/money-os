#!/usr/bin/env python3
"""Twice-daily phone reports. Compact — sized for a text, not a terminal.

Usage:
  python tools/daily_report.py --brief    # morning: state + plans + plug-in nag
  python tools/daily_report.py --close    # evening: day P&L, fills, sessions, vs SPY
  add --no-text to print only
"""
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from alpaca.trading.client import TradingClient
from alpaca.trading.enums import QueryOrderStatus
from alpaca.trading.requests import GetOrdersRequest

from common import REPO
from notify import send_text

CONFIG_DIR = Path.home() / ".config" / "money-os"


def parse_env(path: Path) -> dict:
    env = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def agents_clients() -> dict[str, TradingClient]:
    out = {}
    for f in sorted(CONFIG_DIR.glob("*.env")):
        if not (REPO / "agents" / f.stem).is_dir():
            continue
        e = parse_env(f)
        if e.get("ALPACA_API_KEY"):
            out[f.stem] = TradingClient(e["ALPACA_API_KEY"], e["ALPACA_SECRET_KEY"], paper=True)
    return out


def on_battery() -> bool:
    try:
        r = subprocess.run(["pmset", "-g", "batt"], capture_output=True, text=True, timeout=10)
        return "Battery Power" in r.stdout
    except Exception:
        return False


def brief() -> str:
    lines = ["money-os morning brief"]
    if on_battery():
        lines.append("⚠ ON BATTERY — plug in + lid open or sessions will be missed")
    for agent, c in agents_clients().items():
        acct = c.get_account()
        pos = c.get_all_positions()
        orders = c.get_orders(GetOrdersRequest(status=QueryOrderStatus.OPEN, limit=50))
        trig_file = REPO / "agents" / agent / "memory" / "triggers.json"
        ntrig = 0
        if trig_file.exists():
            try:
                ntrig = len(json.loads(trig_file.read_text()))
            except Exception:
                pass
        lines.append(f"{agent}: ${float(acct.equity):,.0f} · {len(pos)} pos · "
                     f"{len(orders)} orders · {ntrig} triggers")
    lines.append("windows: 9:45a + 3:30p · sentinel on watch")
    return "\n".join(lines)


def close() -> str:
    today = datetime.now(timezone.utc).astimezone().date().isoformat()
    lines = [f"money-os close report {today}"]
    spy_ret = None
    for agent, c in agents_clients().items():
        acct = c.get_account()
        eq, last = float(acct.equity), float(acct.last_equity)
        day = (eq / last - 1) * 100 if last else 0.0
        # inception vs SPY
        base_f = REPO / "agents" / agent / "journal" / "experiment.json"
        vs = ""
        if base_f.exists():
            base = json.loads(base_f.read_text())
            ret = (eq / base["start_equity"] - 1) * 100
            if spy_ret is None:
                try:
                    from alpaca.data.historical import StockHistoricalDataClient
                    from alpaca.data.requests import StockLatestTradeRequest
                    e = parse_env(CONFIG_DIR / f"{agent}.env")
                    d = StockHistoricalDataClient(e["ALPACA_API_KEY"], e["ALPACA_SECRET_KEY"])
                    spy_px = float(d.get_stock_latest_trade(
                        StockLatestTradeRequest(symbol_or_symbols="SPY"))["SPY"].price)
                    spy_ret = (spy_px / base["spy_start_price"] - 1) * 100
                except Exception:
                    pass
            if spy_ret is not None:
                vs = f" · {ret - spy_ret:+.1f}p vs SPY"
        since = datetime.now(timezone.utc) - timedelta(hours=18)
        fills = [o for o in c.get_orders(GetOrdersRequest(
            status=QueryOrderStatus.CLOSED, after=since, limit=50))
            if o.status.value == "filled"]
        fl = "; ".join(f"{o.side.value} {o.symbol}@{float(o.filled_avg_price):.2f}" for o in fills) or "no fills"
        lines.append(f"{agent}: ${eq:,.0f} ({day:+.2f}% day){vs}\n  {fl}")

    # sessions today
    ran = sorted({p.name.split("-", 4)[3] for p in (REPO / "logs").glob(f"{today}-*-*.log")})
    lines.append(f"sessions ran: {', '.join(ran) if ran else 'NONE'}")
    ev = REPO / "logs" / "sentinel-events.jsonl"
    if ev.exists():
        bad = [json.loads(l) for l in ev.read_text().splitlines()
               if f'"date": "{today}"' in l and "unrecoverable" in l]
        if bad:
            lines.append(f"⚠ lost sessions: {', '.join(sorted({b['session'] for b in bad}))}")
    return "\n".join(lines)


def main() -> None:
    if "--brief" in sys.argv:
        msg = brief()
    elif "--close" in sys.argv:
        msg = close()
    else:
        sys.exit("usage: daily_report.py --brief|--close [--no-text]")
    print(msg)
    if "--no-text" not in sys.argv:
        ok = send_text(msg)
        print(f"[text {'sent' if ok else 'NOT sent — check notify.conf'}]")


if __name__ == "__main__":
    main()
