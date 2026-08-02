#!/usr/bin/env python3
"""Portfolio risk engine: exposure report + the drawdown circuit-breaker state machine.

The circuit breaker (Risk Rulebook rules 16-19) lives HERE, in code:
- tracks each agent's high-water mark in data/state.json (updated on every run)
- current tier is computed from drawdown vs HWM:
    NORMAL (dd > -5%) | REDUCED (-5..-10%: half risk, 1 entry/session)
    | ETF_ONLY (-10..-15%) | HALT (<= -15%: no new entries)
- trade.py consults check_entry_allowed() before any BUY.

Usage:
  python tools/risk.py report      # exposure, correlations, gap budget, breaker tier
"""
import json
import math
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from common import REPO, get_env_keys
import os

STATE = REPO / "data" / "state.json"
SECTOR = {  # coarse static map: ETFs + agents' typical holdings; unknown -> 'other'
    "XLK": "tech", "XLY": "cons-disc", "XLC": "comms", "XLF": "financials", "XLI": "industrials",
    "XLB": "materials", "XLE": "energy", "XLV": "health", "XLP": "staples", "XLU": "utilities",
    "XLRE": "real-estate", "SPY": "broad", "QQQ": "broad-tech", "IWM": "broad-small", "RSP": "broad",
    "VEU": "intl", "VXUS": "intl", "IEFA": "intl", "EFA": "intl", "BND": "bonds", "AGG": "bonds",
    "BIL": "cash-like", "SGOV": "cash-like", "GLD": "gold", "DBC": "commodities", "XRT": "cons-disc",
}
GAP_ASSUMPTION = {"single": 0.20, "etf": 0.05}  # Rulebook rule 11


def load_state() -> dict:
    return json.loads(STATE.read_text()) if STATE.exists() else {}


def save_state(s: dict) -> None:
    STATE.parent.mkdir(exist_ok=True)
    STATE.write_text(json.dumps(s, indent=2) + "\n")


def breaker_tier(agent: str, equity: float) -> tuple[str, float]:
    """Update HWM, return (tier, drawdown_pct). Called by report and by trade.py."""
    s = load_state()
    a = s.setdefault(agent, {})
    hwm = max(a.get("hwm", 0.0), equity)
    a["hwm"] = hwm
    a["equity"] = equity
    a["updated"] = datetime.now(timezone.utc).isoformat()
    save_state(s)
    dd = (equity / hwm - 1) * 100 if hwm else 0.0
    if dd <= -15:
        return "HALT", dd
    if dd <= -10:
        return "ETF_ONLY", dd
    if dd <= -5:
        return "REDUCED", dd
    return "NORMAL", dd


def check_entry_allowed(agent: str, equity: float, symbol: str) -> tuple[bool, str]:
    """Used by trade.py before any buy. Returns (allowed, message)."""
    tier, dd = breaker_tier(agent, equity)
    is_etf = symbol in SECTOR and SECTOR[symbol] not in (
        "tech", "cons-disc", "comms", "financials", "industrials", "materials",
        "energy", "health", "staples", "utilities", "real-estate") or symbol in SECTOR
    # ETFs = anything in our known-ETF map; single names are everything else
    is_known_etf = symbol in SECTOR
    if tier == "HALT":
        return False, f"circuit breaker HALT: drawdown {dd:.1f}% from HWM — no new entries (rule 18)"
    if tier == "ETF_ONLY" and not is_known_etf:
        return False, f"circuit breaker ETF_ONLY: drawdown {dd:.1f}% — broad ETFs only (rule 17)"
    if tier == "REDUCED":
        return True, f"circuit breaker REDUCED: drawdown {dd:.1f}% — halve risk, max 1 entry/session (rule 16)"
    return True, ""


def correlation(conn, a: str, b: str, days: int = 120) -> float | None:
    rows_a = dict(conn.execute("SELECT date, close FROM bars WHERE symbol=? ORDER BY date DESC LIMIT ?",
                               (a, days + 1)).fetchall())
    rows_b = dict(conn.execute("SELECT date, close FROM bars WHERE symbol=? ORDER BY date DESC LIMIT ?",
                               (b, days + 1)).fetchall())
    common_dates = sorted(set(rows_a) & set(rows_b))
    if len(common_dates) < 40:
        return None
    ra, rb = [], []
    for d1, d2 in zip(common_dates, common_dates[1:]):
        ra.append(rows_a[d2] / rows_a[d1] - 1)
        rb.append(rows_b[d2] / rows_b[d1] - 1)
    n = len(ra)
    ma_, mb = sum(ra) / n, sum(rb) / n
    cov = sum((x - ma_) * (y - mb) for x, y in zip(ra, rb)) / n
    sa = math.sqrt(sum((x - ma_) ** 2 for x in ra) / n)
    sb = math.sqrt(sum((y - mb) ** 2 for y in rb) / n)
    return cov / (sa * sb) if sa and sb else None


def report() -> None:
    from alpaca.trading.client import TradingClient
    key, secret = get_env_keys()
    agent = os.environ.get("MONEYOS_AGENT", "scholar")
    client = TradingClient(key, secret, paper=True)
    acct = client.get_account()
    equity = float(acct.equity)
    positions = client.get_all_positions()

    tier, dd = breaker_tier(agent, equity)
    print(f"agent {agent}: equity ${equity:,.2f}  HWM ${load_state()[agent]['hwm']:,.2f}  "
          f"drawdown {dd:+.2f}%  →  circuit breaker: {tier}")

    if not positions:
        print("no positions — nothing else to report")
        return

    print("\n== exposure")
    by_sector: dict[str, float] = {}
    gap_budget = 0.0
    for p in positions:
        mv = float(p.market_value)
        sec = SECTOR.get(p.symbol, "single-stock")
        by_sector[sec] = by_sector.get(sec, 0) + mv
        gap = GAP_ASSUMPTION["etf" if p.symbol in SECTOR else "single"]
        gap_budget += mv * gap
        print(f"  {p.symbol:<6}{sec:<14}${mv:>10,.2f}  {mv / equity * 100:5.1f}% of equity")
    print("  --")
    for sec, mv in sorted(by_sector.items(), key=lambda kv: -kv[1]):
        print(f"  {sec:<20}${mv:>10,.2f}  {mv / equity * 100:5.1f}%")
    print(f"\n== gap-risk budget (rule 11): worst-case overnight ${gap_budget:,.2f} "
          f"= {gap_budget / equity * 100:.1f}% of equity (ceiling 15%)"
          + ("  ⚠ OVER" if gap_budget / equity > 0.15 else "  ok"))

    syms = [p.symbol for p in positions]
    if len(syms) > 1:
        print("\n== pairwise correlations (120d daily)")
        conn = sqlite3.connect(REPO / "data" / "market.db")
        for i, a in enumerate(syms):
            for b in syms[i + 1:]:
                c = correlation(conn, a, b)
                flag = "  ⚠ same-trade (rule 14: counts as one slot)" if c is not None and c > 0.8 else ""
                print(f"  {a}-{b}: {c:+.2f}{flag}" if c is not None else f"  {a}-{b}: insufficient data")


if __name__ == "__main__":
    report()
