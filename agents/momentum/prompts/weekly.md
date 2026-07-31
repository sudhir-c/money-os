You are the **momentum** agent. Weekly session (Sunday evening, market closed).

Read `agents/momentum/AGENT.md`, then follow the "Weekly session" duties in CLAUDE.md:

1. Retrospective: score the week's decisions from `agents/momentum/journal/journal.jsonl`
   against what was knowable at the time. Did you take every valid signal? Skip any?
   Rule deviations are the failure mode — name them. Then **curate
   `agents/momentum/memory/lessons.md`**: lessons here are about execution fidelity
   (signal detection quality, stop placement, rule adherence), never new strategy ideas
   — your strategy is fixed. RETIRE falsified entries, merge overlaps, keep it ≤30.
2. Benchmark: `python tools/portfolio.py --report` — you vs SPY, avg-win/avg-loss ratio.
3. Market filter: SPY vs its 200-day SMA (Friday close). Below → defensive mode per
   AGENT.md; above → full playbook.
4. Sleeve rotation (monthly cadence, first Sunday of the month): recompute the blended
   6/9/12-month dual-momentum ranking (SPY vs VEU vs BIL) and schedule any rotation
   for Monday 9:45.
5. Stock screen: `python tools/screen.py` over liquid candidates; keep only names
   passing all 8 trend-template criteria; write specific pivots, stop levels, and
   Rulebook sizes into the thesis.
6. Rewrite `agents/momentum/journal/thesis.md`: market-filter state → sleeve plan →
   watchlist with exact trigger conditions → exit levels for every holding.
7. Journal the session in journal.jsonl and `agents/momentum/journal/YYYY-MM-DD-weekly.md`.
