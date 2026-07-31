"""Shared helpers for money-os tools."""
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def agent_home() -> Path:
    """This agent's home directory, `agents/$MONEYOS_AGENT/`.

    Falls back to the sole agent when MONEYOS_AGENT is unset (manual runs); once
    there is more than one agent, an unset variable is ambiguous and must fail loudly
    rather than silently report another agent's numbers.
    """
    name = os.environ.get("MONEYOS_AGENT", "").strip()
    agents_dir = REPO / "agents"
    if not name:
        found = sorted(p.name for p in agents_dir.iterdir() if p.is_dir()) if agents_dir.is_dir() else []
        if len(found) != 1:
            sys.exit(
                f"error: MONEYOS_AGENT not set and {len(found)} agents found in {agents_dir} "
                f"({', '.join(found) or 'none'}). Set MONEYOS_AGENT to pick one."
            )
        name = found[0]
    home = agents_dir / name
    if not home.is_dir():
        sys.exit(f"error: no such agent {name!r} (expected {home})")
    return home


def get_env_keys() -> tuple[str, str]:
    """Read Alpaca paper API keys from the environment; fail loudly if missing."""
    key = os.environ.get("ALPACA_API_KEY", "")
    secret = os.environ.get("ALPACA_SECRET_KEY", "")
    if not key or not secret:
        sys.exit(
            "error: ALPACA_API_KEY / ALPACA_SECRET_KEY not set. "
            "Source ~/.config/money-os/env first."
        )
    return key, secret
