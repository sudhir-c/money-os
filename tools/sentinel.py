#!/usr/bin/env python3
"""Sentinel: the event-driven layer. Runs every 10 minutes via launchd (no LLM cost).

During market hours it checks every agent's pre-committed triggers
(agents/<name>/memory/triggers.json), order fills, and a global -3% day-drawdown
guard. When something fires it logs the event, notifies, and spawns a SCOPED
emergency agent session (max 2 per agent per day).

On weekdays at any hour it also heartbeats: if an expected session log is missing
well after its slot, it alerts — the launchd/sleep failure detector.

triggers.json schema (a JSON list):
  [{"id": "unique-name", "symbol": "XLF", "condition": "price_below", "level": 53.0,
    "note": "thesis stop context", "preauth_buy": false, "expires": "2026-08-15"}]
conditions: price_below | price_above | day_change_pct (level = +/- percent)
Special: {"condition": "order_filled", "client_order_id": "..."} fires on that fill.
"""
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestTradeRequest
from alpaca.trading.client import TradingClient
from alpaca.trading.enums import QueryOrderStatus
from alpaca.trading.requests import GetOrdersRequest

from common import REPO
from notify import notify

CONFIG_DIR = Path.home() / ".config" / "money-os"
STATE_FILE = REPO / "data" / "sentinel-state.json"
EVENTS_LOG = REPO / "logs" / "sentinel-events.jsonl"
MAX_EMERGENCIES_PER_DAY = 2

# Missed-session detection AND recovery. The Mac sleeping through a launchd slot is
# the most common real failure; the sentinel runs every 10 min and is the only job
# reliable enough to fix it. (deadline, recover_until) in local ET.
# Recovery windows respect what the session is FOR: a trade window is worth running
# late only while the market is open; intel sessions are useful any time that day.
HEARTBEAT = {
    "premarket": {"deadline": "08:15", "recover_until": "09:35"},
    "morning":   {"deadline": "10:05", "recover_until": "15:00", "needs_market": True},
    "afternoon": {"deadline": "15:45", "recover_until": "15:58", "needs_market": True},
    "evening":   {"deadline": "19:00", "recover_until": "23:30"},
}


def parse_env(path: Path) -> dict[str, str]:
    env = {}
    for line in path.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env


def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"fired": [], "order_status": {}, "emergencies": {}}


def save_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2) + "\n")


def log_event(event: dict) -> None:
    EVENTS_LOG.parent.mkdir(exist_ok=True)
    event["ts"] = datetime.now(timezone.utc).isoformat()
    with EVENTS_LOG.open("a") as f:
        f.write(json.dumps(event) + "\n")


def spawn_emergency(agent: str, events: list[dict], state: dict) -> None:
    today = datetime.now(timezone.utc).astimezone().date().isoformat()
    count = state["emergencies"].get(f"{agent}:{today}", 0)
    if count >= MAX_EMERGENCIES_PER_DAY:
        log_event({"type": "emergency_suppressed", "agent": agent,
                   "reason": f"cooldown ({count} today)", "events": events})
        notify("money-os sentinel", f"{agent}: trigger fired but emergency cooldown reached")
        return
    state["emergencies"][f"{agent}:{today}"] = count + 1

    scope = ",".join(sorted({e["symbol"] for e in events if e.get("symbol")}))
    buy_ok = any(e.get("preauth_buy") for e in events)
    event_file = REPO / "agents" / agent / "memory" / "emergency-event.json"
    event_file.write_text(json.dumps(events, indent=2) + "\n")

    import os
    env = dict(os.environ)
    env["MONEYOS_EMERGENCY_SCOPE"] = scope
    if buy_ok:
        env["MONEYOS_EMERGENCY_BUY_OK"] = "1"
    subprocess.Popen(
        ["/bin/bash", str(REPO / "bin" / "run-trader.sh"), "emergency", agent],
        env=env, cwd=str(REPO),
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    log_event({"type": "emergency_spawned", "agent": agent, "scope": scope,
               "buy_ok": buy_ok, "events": events})
    notify("money-os sentinel", f"{agent}: emergency session spawned ({scope})")


def check_agent(agent: str, env: dict, data_client, now_open: bool, state: dict) -> None:
    client = TradingClient(env["ALPACA_API_KEY"], env["ALPACA_SECRET_KEY"], paper=True)
    fired_events: list[dict] = []

    # --- global day-drawdown guard ---
    if now_open:
        acct = client.get_account()
        equity, last = float(acct.equity), float(acct.last_equity)
        if last and (equity / last - 1) * 100 <= -3.0:
            fid = f"{agent}:daydd:{datetime.now(timezone.utc).date()}"
            if fid not in state["fired"]:
                state["fired"].append(fid)
                fired_events.append({"symbol": None, "trigger": "portfolio_day_drawdown",
                                     "detail": f"equity {equity:.2f} vs prior close {last:.2f} "
                                               f"({(equity / last - 1) * 100:+.2f}%)"})

    # --- order fills (any state change to filled since last look) ---
    orders = client.get_orders(GetOrdersRequest(status=QueryOrderStatus.ALL, limit=50))
    for o in orders:
        key = f"{agent}:{o.client_order_id}"
        prev = state["order_status"].get(key)
        cur = o.status.value
        state["order_status"][key] = cur
        if prev and prev != cur and cur == "filled" and o.type.value in ("stop", "stop_limit", "trailing_stop"):
            fid = f"{agent}:fill:{o.client_order_id}"
            if fid not in state["fired"]:
                state["fired"].append(fid)
                fired_events.append({"symbol": o.symbol, "trigger": "protective_stop_filled",
                                     "detail": f"{o.symbol} stop filled @ {o.filled_avg_price} "
                                               f"[{o.client_order_id}] — position is now unprotected/closed; "
                                               f"review and decide follow-up"})

    # --- agent-authored triggers ---
    trig_file = REPO / "agents" / agent / "memory" / "triggers.json"
    if trig_file.exists() and now_open:
        try:
            triggers = json.loads(trig_file.read_text())
        except json.JSONDecodeError:
            log_event({"type": "bad_triggers_json", "agent": agent})
            triggers = []
        today = datetime.now(timezone.utc).date().isoformat()
        symbols = sorted({t["symbol"] for t in triggers
                          if t.get("symbol") and t.get("expires", "9999") >= today})
        prices, prevs = {}, {}
        if symbols:
            trades = data_client.get_stock_latest_trade(
                StockLatestTradeRequest(symbol_or_symbols=symbols))
            prices = {s: float(t.price) for s, t in trades.items()}
            # prior closes from the cache for day_change_pct
            import sqlite3
            conn = sqlite3.connect(REPO / "data" / "market.db")
            for s in symbols:
                row = conn.execute("SELECT close FROM bars WHERE symbol=? "
                                   "ORDER BY date DESC LIMIT 1", (s,)).fetchone()
                if row:
                    prevs[s] = row[0]
        for t in triggers:
            tid = f"{agent}:{t.get('id', json.dumps(t, sort_keys=True))}"
            if tid in state["fired"] or t.get("expires", "9999") < today:
                continue
            sym, cond, level = t.get("symbol"), t.get("condition"), t.get("level")
            px = prices.get(sym)
            hit = False
            if cond == "price_below" and px is not None:
                hit = px <= level
            elif cond == "price_above" and px is not None:
                hit = px >= level
            elif cond == "day_change_pct" and px is not None and prevs.get(sym):
                chg = (px / prevs[sym] - 1) * 100
                hit = (chg <= level) if level < 0 else (chg >= level)
            if hit:
                state["fired"].append(tid)
                fired_events.append({"symbol": sym, "trigger": cond, "level": level,
                                     "price": px, "note": t.get("note", ""),
                                     "preauth_buy": bool(t.get("preauth_buy"))})

    if fired_events:
        for e in fired_events:
            log_event({"type": "trigger_fired", "agent": agent, **e})
        spawn_emergency(agent, fired_events, state)


def session_running() -> bool:
    """Is a run-trader.sh session already in flight? Never stack sessions."""
    try:
        out = subprocess.run(["pgrep", "-f", "run-trader.sh"], capture_output=True, text=True)
        return bool(out.stdout.strip())
    except Exception:
        return False


def heartbeat(market_open: bool) -> None:
    """Detect missed sessions and RECOVER them (run them late) when still useful."""
    now = datetime.now(timezone.utc).astimezone()
    if now.weekday() >= 5:
        return
    today = now.date().isoformat()
    hm = now.strftime("%H:%M")
    # who SHOULD have run: enabled agents with keys
    expected = sorted(
        d.name for d in (REPO / "agents").iterdir()
        if d.is_dir() and not (d / "DISABLED").exists()
        and (CONFIG_DIR / f"{d.name}.env").exists())

    for session, cfg in HEARTBEAT.items():
        if hm < cfg["deadline"]:
            continue
        # per-agent: a partial run (one agent logged, others not) must still recover
        missing = [a for a in expected
                   if not (REPO / "logs" / f"{today}-{session}-{a}.log").exists()]
        if not missing:
            continue
        recoverable = hm <= cfg["recover_until"] and (market_open or not cfg.get("needs_market"))
        for agent in missing:
            marker = REPO / "data" / f".hb-{today}-{session}-{agent}"
            if marker.exists():
                continue  # already handled this agent/session today
            if recoverable:
                if session_running():
                    break  # try again next tick; never stack sessions
                marker.touch()
                subprocess.Popen(
                    ["/bin/bash", str(REPO / "bin" / "run-trader.sh"), session, agent],
                    cwd=str(REPO), stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL, start_new_session=True)
                log_event({"type": "session_recovered", "session": session, "agent": agent,
                           "date": today,
                           "detail": f"missed its slot (Mac asleep or launchd failure); "
                                     f"started late at {hm}"})
                notify("money-os", f"recovered missed {session} session for {agent}")
                break  # one at a time; the next tick picks up the rest
            else:
                marker.touch()
                log_event({"type": "heartbeat_miss_unrecoverable", "session": session,
                           "agent": agent, "date": today,
                           "detail": f"past recovery window {cfg['recover_until']}"})
                notify("money-os HEARTBEAT",
                       f"{agent} missed {session} — past recovery window")


def main() -> None:
    # find any working key set for clock + quotes
    envs = {}
    for f in sorted(CONFIG_DIR.glob("*.env")):
        e = parse_env(f)
        if e.get("ALPACA_API_KEY") and e.get("ALPACA_SECRET_KEY"):
            envs[f.stem] = e
    if not envs:
        return
    first = next(iter(envs.values()))
    clock = TradingClient(first["ALPACA_API_KEY"], first["ALPACA_SECRET_KEY"],
                          paper=True).get_clock()
    data_client = StockHistoricalDataClient(first["ALPACA_API_KEY"], first["ALPACA_SECRET_KEY"])

    heartbeat(clock.is_open)

    state = load_state()
    for agent, env in envs.items():
        if (REPO / "agents" / agent / "DISABLED").exists():
            continue
        if not (REPO / "agents" / agent).is_dir():
            continue
        try:
            check_agent(agent, env, data_client, clock.is_open, state)
        except Exception as e:
            log_event({"type": "sentinel_error", "agent": agent, "error": str(e)})
    save_state(state)


if __name__ == "__main__":
    main()
