# money-os

An experiment: can autonomous AI agents trade profitably? Three Claude agents, each
with its own **$5,000 Alpaca paper-trading account** and its own strategy doctrine,
trade US stocks/ETFs on a fixed schedule with zero human input — racing each other
and a SPY buy-and-hold benchmark.

> Paper trading only. This is a research experiment, not financial advice, and the
> code hardwires `paper=True` everywhere.

## The competitors

| Agent | Strategy | What it tests |
|---|---|---|
| **scholar** | Evidence-based multi-strategy: dual-momentum core, event-driven satellites, index-ETF mean reversion — gated by a mechanical market-regime score and a 28-rule risk rulebook | The full research-driven system |
| **momentum** | Pure trend-following: buy strength, trail stops, go to cash in downtrends. All other trade types forbidden | One strategy family in isolation |
| **intuition** | No rulebook at all — same code-enforced guardrails, but banned from reading the research library; trades purely on the model's own judgment | Whether the research adds value over raw LLM judgment |

All agents share identical code-enforced limits — paper-only, long-only, max 25% of
equity per position, max 8 orders/session, no margin — so strategy is the only variable.

## How it works

```
launchd → bin/run-trader.sh <session>     # loops over enabled agents, sequentially
  per agent: load its API keys → headless `claude -p` session
    read memory → portfolio state → thesis → research → decide → execute* → journal → write memory
    (*orders only in trade windows — tools/trade.py rejects them from intel sessions)
```

| Session | When | Role | Trades? |
|---|---|---|---|
| premarket | Mon–Fri 7:45 AM | overnight/global sweep; arm the trade window | no |
| morning | Mon–Fri 9:45 AM | trade window (market-gated) | **yes** |
| afternoon | Mon–Fri 3:30 PM | trade window (market-gated) | **yes** |
| evening | Mon–Fri 6:30 PM | day digest, after-hours earnings, watchlist upkeep | no |
| saturday | Sat 10:00 AM | deep research + strategy exploration (scoped per agent identity) | no |
| weekly | Sun 6:00 PM | retrospective, memory curation, thesis rewrite | plan-only |

The trade windows sit where the microstructure research favors (post-open and power
hour). Everything else is intelligence-gathering: research on LLM trading agents
consistently shows more *trading* frequency destroys returns, so the extra sessions
feed memory — watchlists, handoffs, lessons, strategy R&D — while order placement
stays confined to the two market windows, enforced in code.

## Layout

```
CLAUDE.md            shared mechanics every agent loads (workflow, journal schema, hard limits)
agents/<name>/       AGENT.md (strategy identity) + prompts/ (per-session instructions)
                     + memory/ (persistent per-agent memory: lessons.md, watchlist.md,
                     strategy-ideas.md, next-session.md handoff — content stays local)
strategies/          evidence-graded research library (8 reports; see strategies/README.md)
tools/               guardrailed Alpaca access: trade, portfolio, market clock,
                     regime score, momentum screen, dual-momentum sleeve, leaderboard
bin/run-trader.sh    launchd entrypoint: agent loop, market gate, watchdog
bin/agentctl         control panel: status / enable / disable / report / run
launchd/             the three schedule plists
```

Agent runtime output (theses, decision journals, per-run reports) is deliberately
untracked — each agent writes to `agents/<name>/journal/` locally.

## Setup

1. `uv venv && uv pip install alpaca-py`
2. Create Alpaca paper accounts (one per agent), reset each to your starting balance,
   and put keys in `~/.config/money-os/<agent>.env`:
   ```
   ALPACA_API_KEY="PK..."
   ALPACA_SECRET_KEY="..."
   ```
3. Per agent: `MONEYOS_AGENT=<name> .venv/bin/python tools/portfolio.py --init-baseline`
4. `cp launchd/*.plist ~/Library/LaunchAgents/ && launchctl load ~/Library/LaunchAgents/com.moneyos.*.plist` (6 schedules)
5. Requires the [Claude Code](https://claude.com/claude-code) CLI (the agents run as
   headless sessions) and a Mac awake at the scheduled times.

## Operations

```sh
bin/agentctl status              # who's enabled, who has keys
bin/agentctl report              # leaderboard: every agent vs SPY buy-and-hold
bin/agentctl disable <agent>     # freeze an agent (schedule skips it; positions untouched)
bin/agentctl run weekly <agent>  # manual one-off session
```

## Guardrails (enforced in `tools/trade.py`, not just prompts)

- Paper account hardwired; long-only; no options, crypto, shorting, or margin
- Max 25% of equity per position; max 8 orders per session
- Symbol validation, session-tagged order IDs (`<agent>-<session>-<date>-<n>`) for a
  full audit trail, market-hours gate, 20-minute per-agent watchdog
- Position sizing is computed in code — research shows LLMs over-bet when allowed to
  size their own positions, so they never are
