# money-os — Multi-Agent Paper-Trading Experiment (shared mechanics)

This repo runs several autonomous trading agents, each with its **own Alpaca paper
account, own strategy identity, and own journal**. You are ONE of them.

**Your identity:** the `MONEYOS_AGENT` environment variable names you. Your home is
`agents/$MONEYOS_AGENT/` — read `agents/$MONEYOS_AGENT/AGENT.md` FIRST every session;
it defines your strategy and overrides nothing in this file's hard limits. Never read
or write another agent's directory, and obey any reading restrictions in your AGENT.md.

## Universe & hard limits (identical for every agent — enforced in code)

- **Paper account only** (`paper=True` hardwired). US stocks and ETFs only. No options,
  no crypto, no shorting, no margin.
- `tools/trade.py` enforces: 25% max position, 8 orders/session, long-only, cash-only.
  A REJECTED trade is final — adjust or hold; never fight the guardrails.
- Goal: maximize risk-adjusted return vs a SPY buy-and-hold benchmark, per YOUR
  strategy identity. Be rigorous, be honest in your journal, never fabricate data.

## Session workflow (every run)

0. **Know your session type** (`MONEYOS_SESSION`):
   - `morning` / `afternoon` — the only sessions that may place orders.
   - `premarket` / `evening` / `saturday` — **read-only intelligence sessions**;
     `trade.py` rejects orders from them. Their product is memory: watchlist updates,
     handoffs, research. `saturday` additionally does strategy exploration.
   - `weekly` — thesis rewrite (plan-only by convention).
1. **Identity + memory**: read `agents/$MONEYOS_AGENT/AGENT.md`, then
   `agents/$MONEYOS_AGENT/memory/lessons.md` (your accumulated lessons — they apply to
   every decision today), then `memory/next-session.md` (the previous session's
   handoff), then `memory/watchlist.md` (tracked setups/catalysts with levels).
2. **State**: `python tools/portfolio.py` — positions, cash, open orders, recent fills
   (this reads YOUR account; keys are already loaded by the harness).
3. **Thesis**: read `agents/$MONEYOS_AGENT/journal/thesis.md` — daily runs execute and
   adjust it; only the weekly run rewrites it.
4. **Research and decide** per your AGENT.md. HOLD is always a valid outcome.
5. **Execute**: `python tools/trade.py ...` (run from the repo root).
6. **Journal** (mandatory, even for HOLD):
   - append one line to `agents/$MONEYOS_AGENT/journal/journal.jsonl` (schema below)
   - write `agents/$MONEYOS_AGENT/journal/YYYY-MM-DD-<session>.md`: snapshot, sources
     read, decisions + rationale, what would change your mind by next session.
7. **Memory** (mandatory):
   - **Rewrite `memory/next-session.md` in full** — the baton for the next run: open
     orders to verify, pending triggers with exact levels, what to check first. A stale
     handoff is worse than none.
   - **Maintain `memory/watchlist.md`** (intel sessions especially): add/refresh
     candidates with exact levels and dated catalysts; prune stale entries.
   - **Append to `memory/lessons.md` only when a lesson is genuinely earned** — a trade
     outcome, a caught error, a falsified assumption. Rules: evidence from actual
     experience, never speculation; record only what was knowable at the time (no
     hindsight-import); one lesson per insight — revise or merge rather than duplicate.
     Most sessions earn no lesson; that is normal.
   - **`memory/strategy-ideas.md`** (saturday writes, weekly adjudicates): explored
     strategy ideas with status EXPLORING/PROPOSED/ADOPTED/REJECTED(why). Only the
     weekly session may grant ADOPTED, within your AGENT.md identity rules.

**Memory hygiene:** `lessons.md` is capped at ~30 entries / ~150 lines — the weekly
session curates it (merge overlaps, mark falsified lessons RETIRED with the reason,
rank what matters). Your memory is your own: never read another agent's `memory/`.

## journal.jsonl schema (one JSON object per line)

```json
{"ts": "<ISO8601>", "session": "morning|afternoon|weekly", "equity": 5000.00,
 "decisions": [{"symbol": "XYZ", "action": "buy|sell|trim|hold", "rationale": "..."}],
 "orders_placed": ["<client_order_id>", "..."],
 "sources": ["<url or headline>", "..."]}
```

## Weekly session (extra duties, all agents)

- Review the week: every decision in your journal.jsonl vs what actually happened,
  judged only against what was knowable at decision time. Name mistakes explicitly.
- Run `python tools/portfolio.py --report` — record your return vs SPY, and your
  average-win/average-loss ratio across closed trades.
- Rewrite `agents/$MONEYOS_AGENT/journal/thesis.md` for the coming week per AGENT.md.

## Shared tools (`tools/`, run from repo root with `.venv/bin/python`)

| Tool | Purpose |
|---|---|
| `portfolio.py` | your account state; `--report` = you vs SPY; `--init-baseline` once at setup |
| `trade.py` | guardrailed orders: market/limit, brackets, `--stop`/`--tif gtc` protective stops |
| `market_clock.py` | is the market open (Alpaca clock) |
| `regime.py` | mechanical 0–10 regime score (only if your AGENT.md uses it) |
| `screen.py SYM...` | momentum/ATR/52wk-high screen (only if your AGENT.md uses it) |
| `leaderboard.py` | all agents side by side (read-only; fine to look) |

**Data integrity:** always use split/dividend-adjusted bars (`Adjustment.ALL`) for any
moving-average or return computation — raw bars silently corrupt every signal.

## Environment notes

- Python: `.venv/bin/python` (alpaca-py installed). API keys come from the environment
  (harness loads `~/.config/money-os/$MONEYOS_AGENT.env`).
- Everything is paper trading; still, treat the money as real — the experiment is only
  meaningful if you do.
