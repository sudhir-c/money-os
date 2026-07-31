#!/usr/bin/env python3
"""Leaderboard: every agent's account side by side, vs SPY buy-and-hold.

Reads each agent's keys from ~/.config/money-os/<agent>.env and baseline from
agents/<agent>/journal/experiment.json. Safe to run any time; read-only.

Usage:  python tools/leaderboard.py
"""
import json
import os
import sys
from pathlib import Path

from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestTradeRequest
from alpaca.trading.client import TradingClient

from common import REPO

CONFIG_DIR = Path.home() / ".config" / "money-os"


def parse_env_file(path: Path) -> dict[str, str]:
    env: dict[str, str] = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def main() -> None:
    agents_dir = REPO / "agents"
    agents = sorted(p.name for p in agents_dir.iterdir() if p.is_dir())
    if not agents:
        sys.exit("no agents found")

    spy_now = None
    rows = []
    for name in agents:
        home = agents_dir / name
        disabled = (home / "DISABLED").exists()
        env_file = CONFIG_DIR / f"{name}.env"
        row = {"agent": name, "state": "DISABLED" if disabled else "enabled"}

        if not env_file.exists():
            row["note"] = "no keys"
            rows.append(row)
            continue
        env = parse_env_file(env_file)
        key, secret = env.get("ALPACA_API_KEY", ""), env.get("ALPACA_SECRET_KEY", "")
        if not key or not secret:
            row["note"] = "keys empty"
            rows.append(row)
            continue

        try:
            acct = TradingClient(key, secret, paper=True).get_account()
            row["equity"] = float(acct.equity)
            if spy_now is None:
                data = StockHistoricalDataClient(key, secret)
                spy_now = float(
                    data.get_stock_latest_trade(
                        StockLatestTradeRequest(symbol_or_symbols="SPY")
                    )["SPY"].price
                )
        except Exception as e:  # keep the board printable if one account errors
            row["note"] = f"api error: {e}"
            rows.append(row)
            continue

        baseline_file = home / "journal" / "experiment.json"
        if baseline_file.exists():
            base = json.loads(baseline_file.read_text())
            row["start"] = base["start_equity"]
            row["ret"] = (row["equity"] / base["start_equity"] - 1) * 100
            row["spy_ret"] = (spy_now / base["spy_start_price"] - 1) * 100
            row["vs_spy"] = row["ret"] - row["spy_ret"]
            row["since"] = base["start_date"]
        else:
            row["note"] = "no baseline"
        rows.append(row)

    print(f"{'agent':<12}{'state':<10}{'equity':>12}{'return':>9}{'SPY':>9}{'vs SPY':>9}  since")
    print("-" * 68)
    for r in rows:
        if "equity" not in r:
            print(f"{r['agent']:<12}{r['state']:<10}{'—':>12}  ({r.get('note', '')})")
            continue
        if "ret" in r:
            print(
                f"{r['agent']:<12}{r['state']:<10}{r['equity']:>12,.2f}"
                f"{r['ret']:>+8.2f}%{r['spy_ret']:>+8.2f}%{r['vs_spy']:>+8.2f}p  {r['since']}"
            )
        else:
            print(f"{r['agent']:<12}{r['state']:<10}{r['equity']:>12,.2f}  ({r.get('note', '')})")


if __name__ == "__main__":
    main()
