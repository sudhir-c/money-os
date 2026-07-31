# strategies/ — The Agent's Strategy Library

Eight deep-research reports, compiled July 2026, cross-checked against academic literature, verified practitioner records, broker documentation, and the 2023–2026 LLM-trading research. **The weekly thesis must select from and cite this library — freeform strategy invention is prohibited.**

## The library

| File | Covers | Best-evidence takeaway |
|---|---|---|
| [momentum-trend.md](momentum-trend.md) | 12-1 cross-sectional momentum, dual momentum (GEM), MA filters, 52-wk-high, ETF rotation | Momentum is the academic anomaly best suited to this cadence; dual-momentum ETF core is the best structural fit |
| [mean-reversion.md](mean-reversion.md) | Connors RSI(2)/TPS, IBS, Turnaround Tuesday, VIX-stretch, gap fades | Index ETFs only, never single stocks; enter at 3:30; **never tight-stop a mean-reversion entry** |
| [event-driven.md](event-driven.md) | PEAD, earnings discipline, analyst revisions, insider clusters, guidance, news drift, FOMC/CPI | The agent's best-fit family (reading breadth is the real edge); PEAD alive only in small/mid caps; index-inclusion effect is DEAD |
| [regime-rotation.md](regime-rotation.md) | The Sunday regime checklist (0–10 score → posture), VIX term structure, credit spreads, breadth, seasonality | Regimes size risk, they don't chase return; exit fast, re-enter slow |
| [risk-management.md](risk-management.md) | Sizing, stops evidence, drawdown circuit breakers, PDT retirement (June 2026), behavioral guards | **The Risk Rulebook (28 numbered rules) — binding on every session** |
| [legendary-traders.md](legendary-traders.md) | Livermore → Qullamaggie, verified records vs myth, consensus rules | 10 profiles, zero dissent on: cut losses fast, never average down, ride winners, regime filter |
| [llm-trader-evidence.md](llm-trader-evidence.md) | StockBench, live arenas, failure modes, what measurably helps LLM traders | Realistic expectation: market ±2pp with better drawdowns; the only proven LLM edge is discipline + loss avoidance |
| [execution.md](execution.md) | Order-type policy, spreads by time of day, Alpaca mechanics, paper-vs-live, gap risk, v2 appendix | Marketable limits by default; 3:30 is the better window; stops don't work overnight — size for gaps |

## The unified doctrine (what every report independently converged on)

1. **HOLD is the default.** Daily churn is the single best-documented LLM-trader failure (weekly Sharpe 1.03 > daily 0.89; Barber-Odean's monotonic turnover-returns decline). Big decisions live in the Sunday session; daily sessions are monitoring-first.
2. **Cut losses fast; never average down; ride winners.** Unanimous across 10 legendary traders, the academic stop literature (for momentum), and the LLM evidence. Stops per strategy type: 7–8%/2-ATR on momentum entries; wide disaster stops + time stops (never tight stops) on mean-reversion entries.
3. **Regime filter before stock selection.** Compute the Sunday regime score (regime-rotation.md) mechanically FIRST; it caps equity exposure. The score may never be overridden by narrative — narrative override is the historically fatal failure mode (Livermore, Druckenmiller 2000, LLM sycophancy research).
4. **Sizing is code, not judgment.** Elm Wealth: every frontier model over-leveraged when allowed to size freely. 1% risk units, 25% position cap, equal risk weight; conviction picks *which* trades, never *how big*.
5. **Overnight gaps, not stops, are the real tail risk.** Stops only work 9:30–4:00. Never hold single names through scheduled earnings/binary events (check calendar every 3:30 session); size single stocks assuming a 20% overnight gap.
6. **The edge is discipline + reading breadth at multi-day horizons, not speed.** News in large caps is priced in minutes — never trade it. The exploitable residue: PEAD/guidance drift in small/mid caps, insider clusters, complex slow-diffusion news, no-news dip reversals — all multi-day-to-multi-month horizons where twice-daily latency is irrelevant.
7. **Anomalies decay.** Assume half the published edge for everything; re-verify decay status yearly. Dead: index-inclusion effect, large-cap PEAD, unconditional pre-FOMC drift, Double 7s.
8. **Benchmark honestly.** Weekly: portfolio vs SPY buy-and-hold since inception. The realistic goal is market-matching returns with smaller drawdowns plus modest event-driven alpha — an agent chasing more than that is the one that blows up.

## Default portfolio template (starting point; Sunday session tunes within it)

- **Core (50–75%):** dual-momentum ETF sleeve (GEM-style: SPY/VEU/BND via blended 6-12-month lookbacks, BIL as risk-off) — momentum-trend.md §2. Exposure scaled by the regime score.
- **Satellite A (0–35%):** event-driven positions (PEAD, guidance raises, insider clusters, news drift) per event-driven.md rules — small/mid caps, 10–25% each, always with exit triggers and the earnings-calendar discipline.
- **Satellite B (0–25%):** ≤2 concurrent index-ETF mean-reversion positions (RSI(2)/IBS composite at 3:30) per mean-reversion.md — Neutral-regime workhorse.
- **Cash (SGOV/BIL):** whatever the regime score demands. Cash is a position.

## Conflicts between reports (resolved)

- **Stops:** help momentum (Han/Zhou/Zhu), hurt mean reversion (Connors/Alvarez/Kaminski-Lo). Resolution: stop policy is strategy-typed (Risk Rulebook rules 8–9). Both reports agree on this split.
- **PDT:** risk-management.md documents the rule's retirement (June 4, 2026, FINRA 26-10, Alpaca implemented) at grade A; mean-reversion.md urges empirical verification. Resolution: same-day round trips are permitted, but Rulebook rule 22's fallback (revert to ≤3/5-day legacy mode on any PDT-style rejection) stays active, and rule 23's voluntary churn cap applies regardless.
- **9:45 vs 3:30:** execution.md and mean-reversion.md agree 3:30 is the better window for most entries (tighter spreads, close-basis signals); 9:45 is for gap/EP reactions, next-open executions of prior-close signals, and overnight-news exits.
