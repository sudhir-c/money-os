#!/usr/bin/env python3
"""Market clock: is the market open? Uses Alpaca's /v2/clock (authoritative for
holidays and half-days).

Usage:
  python tools/market_clock.py                 # print clock state as JSON
  python tools/market_clock.py --require-open  # exit 0 if open, 1 if closed
"""
import json
import sys

from alpaca.trading.client import TradingClient

from common import get_env_keys


def main() -> int:
    key, secret = get_env_keys()
    client = TradingClient(key, secret, paper=True)
    clock = client.get_clock()
    state = {
        "is_open": clock.is_open,
        "timestamp": clock.timestamp.isoformat(),
        "next_open": clock.next_open.isoformat(),
        "next_close": clock.next_close.isoformat(),
    }
    print(json.dumps(state, indent=2))
    if "--require-open" in sys.argv:
        return 0 if clock.is_open else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
