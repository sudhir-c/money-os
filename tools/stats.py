#!/usr/bin/env python3
"""Leaderboard v2: risk-adjusted stats per agent, honest about sample sizes.

Equity history accumulates in data/equity.jsonl — one snapshot per agent per run of
this tool (the sentinel and sessions call it over time, building the curve).

Usage:  python tools/stats.py [--snapshot-only]
"""
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

from alpaca.trading.client import TradingClient

from common import REPO

CONFIG_DIR = Path.home() / ".config" / "money-os"
EQUITY_LOG = REPO / "data" / "equity.jsonl"


def parse_env(path: Path) -> dict:
    env = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def snapshot() -> dict[str, float]:
    """Record today's equity per agent (idempotent per day)."""
    today = datetime.now(timezone.utc).date().isoformat()
    existing = set()
    if EQUITY_LOG.exists():
        for line in EQUITY_LOG.read_text().splitlines():
            r = json.loads(line)
            existing.add((r["agent"], r["date"]))
    out = {}
    with EQUITY_LOG.open("a") as f:
        for envf in sorted(CONFIG_DIR.glob("*.env")):
            agent = envf.stem
            if not (REPO / "agents" / agent).is_dir():
                continue
            e = parse_env(envf)
            if not e.get("ALPACA_API_KEY"):
                continue
            try:
                acct = TradingClient(e["ALPACA_API_KEY"], e["ALPACA_SECRET_KEY"], paper=True).get_account()
            except Exception:
                continue
            eq = float(acct.equity)
            out[agent] = eq
            if (agent, today) not in existing:
                f.write(json.dumps({"agent": agent, "date": today, "equity": eq}) + "\n")
    return out


def curves() -> dict[str, list[tuple[str, float]]]:
    out: dict[str, list] = {}
    if EQUITY_LOG.exists():
        for line in EQUITY_LOG.read_text().splitlines():
            r = json.loads(line)
            out.setdefault(r["agent"], []).append((r["date"], r["equity"]))
    for v in out.values():
        v.sort()
    return out


def main() -> None:
    live = snapshot()
    if "--snapshot-only" in sys.argv:
        print(f"snapshotted {len(live)} agents")
        return
    print(f"{'agent':<12}{'equity':>10}{'ret%':>8}{'sharpe':>8}{'maxDD%':>8}{'days':>6}   note")
    print("-" * 62)
    for agent, curve in sorted(curves().items()):
        eq = live.get(agent, curve[-1][1])
        base = curve[0][1]
        ret = (eq / base - 1) * 100
        rets = [(b / a - 1) for (_, a), (_, b) in zip(curve, curve[1:])]
        n = len(rets)
        note = ""
        sharpe = mdd = None
        if n >= 5:
            mean = sum(rets) / n
            var = sum((r - mean) ** 2 for r in rets) / n
            sharpe = mean / math.sqrt(var) * math.sqrt(252) if var else 0
            peak, mdd = 0, 0
            for _, e in curve:
                peak = max(peak, e)
                mdd = min(mdd, e / peak - 1)
            mdd *= 100
            if n < 30:
                note = f"n={n} — noise, not signal"
        else:
            note = f"n={n} — too early for risk stats"
        print(f"{agent:<12}{eq:>10,.2f}{ret:>+7.2f}%"
              f"{(f'{sharpe:8.2f}' if sharpe is not None else '       —')}"
              f"{(f'{mdd:8.2f}' if mdd is not None else '       —')}{n:>6}   {note}")


if __name__ == "__main__":
    main()
