#!/bin/bash
# money-os multi-agent run harness — invoked by launchd (or manually).
# Usage: run-trader.sh <morning|afternoon|weekly> [agent]
#   With no agent argument, runs every enabled agent sequentially.
#   An agent is enabled when agents/<name>/ exists, has no DISABLED flag file,
#   and ~/.config/money-os/<name>.env holds its keys.
set -u

SESSION="${1:-}"
ONLY_AGENT="${2:-}"
case "$SESSION" in
  morning|afternoon|weekly) ;;
  *) echo "usage: run-trader.sh <morning|afternoon|weekly> [agent]" >&2; exit 2 ;;
esac

REPO="$(cd "$(dirname "$0")/.." && pwd)"
CONFIG_DIR="$HOME/.config/money-os"
TIMEOUT_SECS=1200  # 20 min per agent; 3 agents fit inside a trading window

# launchd provides a minimal PATH; claude + uv live in ~/.local/bin
export PATH="$HOME/.local/bin:/usr/local/bin:/opt/homebrew/bin:/usr/bin:/bin"

mkdir -p "$REPO/logs"
cd "$REPO"
PY="$REPO/.venv/bin/python"

run_agent() {
  local NAME="$1"
  local LOG="$REPO/logs/$(date +%F)-$SESSION-$NAME.log"
  local ENV_FILE="$CONFIG_DIR/$NAME.env"

  {
    echo "=== run-trader $SESSION agent=$NAME $(date -u +%FT%TZ) ==="

    if [ -f "$REPO/agents/$NAME/DISABLED" ]; then
      echo "skipped: agent disabled"
      return 0
    fi
    if [ ! -f "$ENV_FILE" ]; then
      echo "skipped: $ENV_FILE missing (no keys)"
      return 0
    fi
    # shellcheck disable=SC1090
    source "$ENV_FILE"
    if [ -z "${ALPACA_API_KEY:-}" ] || [ -z "${ALPACA_SECRET_KEY:-}" ]; then
      echo "skipped: keys empty in $ENV_FILE"
      return 0
    fi
    export ALPACA_API_KEY ALPACA_SECRET_KEY
    export MONEYOS_AGENT="$NAME"
    export MONEYOS_SESSION="$SESSION"

    # Market-hours gate (weekly runs while the market is closed by design).
    if [ "$SESSION" != "weekly" ]; then
      if ! "$PY" tools/market_clock.py --require-open; then
        echo "market closed — skipping $SESSION session"
        return 0
      fi
    fi

    caffeinate -i claude -p "$(cat "agents/$NAME/prompts/$SESSION.md")" \
      --model opus \
      --dangerously-skip-permissions &
    local CMD_PID=$!
    ( sleep "$TIMEOUT_SECS" && kill -TERM "$CMD_PID" 2>/dev/null \
        && echo "watchdog: killed $NAME run after ${TIMEOUT_SECS}s" ) &
    local WATCHDOG_PID=$!
    wait "$CMD_PID"
    local STATUS=$?
    kill "$WATCHDOG_PID" 2>/dev/null
    echo "=== done agent=$NAME (exit $STATUS) $(date -u +%FT%TZ) ==="
    return "$STATUS"
  } >>"$LOG" 2>&1
}

if [ -n "$ONLY_AGENT" ]; then
  AGENTS=("$ONLY_AGENT")
else
  AGENTS=()
  for d in "$REPO"/agents/*/; do
    AGENTS+=("$(basename "$d")")
  done
fi

OVERALL=0
for NAME in "${AGENTS[@]}"; do
  if [ ! -d "$REPO/agents/$NAME" ]; then
    echo "no such agent: $NAME" >&2
    OVERALL=1
    continue
  fi
  run_agent "$NAME" || OVERALL=1
done
exit "$OVERALL"
