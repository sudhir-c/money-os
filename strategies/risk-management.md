# Position Sizing & Risk Management — Knowledge Base for a $5,000 Long-Only Autonomous Agent

**Evidence grades:** A = peer-reviewed journal / regulator / broker primary documentation. B = SSRN working paper, published practitioner book, broker blog. C = practitioner blog / aggregator (directional evidence only).

---

## Sizing frameworks + evidence

### Fixed-fractional risk (the "1–2% rule")
- Van Tharp (*The Definitive Guide to Position Sizing*, 2008) formalized "position sizing" and the R-multiple framework: **R = dollars risked per trade = entry-to-stop distance × shares**. Professional norm: risk 0.5–2% of equity per trade. Formula: `Shares = (Equity × risk%) / (Entry − Stop)`. Grade B (practitioner book, but the survival math is straightforward and uncontroversial).
- Why the % matters: losses compound asymmetrically (a 20% drawdown needs +25% to recover; 50% needs +100%). Risking 1% per trade means even a 10-loss streak costs ~9.6% of equity — recoverable. Risking 5% per trade makes the same streak a ~40% drawdown. Grade A (arithmetic).
- Loss streaks are *normal*, not evidence of failure: expected longest losing streak in N trades ≈ ln(N)/ln(1/q), where q = loss probability. A 45%-win-rate strategy over 100 trades should *expect* a ~7–8 trade losing streak. Sizing must survive this by design. Grade A (probability theory).

### Volatility-based / ATR sizing
- The Turtle system (Curtis Faith, *Way of the Turtle*, 2007) sized positions so 1 "N" (20-day ATR) move ≈ 1% of equity, with stops at 2N — i.e., a stop-out cost 2% of equity. Effect: volatile stocks get small positions, quiet stocks get larger ones, equalizing risk per position. Grade B.
- ATR sizing is fixed-fractional sizing with a volatility-aware stop distance; the two frameworks combine naturally (risk% of equity, stop at k×ATR).

### Portfolio-level volatility targeting
- Moreira & Muir, "Volatility-Managed Portfolios," *Journal of Finance* 2017: scaling exposure down when recent realized volatility is high increased Sharpe ratios and produced alpha across market, value, momentum, and other factors (~+0.15 Sharpe on the market index; better in ~80% of specifications). Mechanism: volatility spikes are not compensated by proportionally higher expected returns. Grade A.
- **Caveat:** Cederburg et al., *Journal of Financial Economics* 2020, tested 103 strategies and found no *systematic* out-of-sample improvement after transaction costs. Net reading: vol-scaling reliably cuts drawdowns/left-tail risk; the Sharpe improvement is real for market/momentum but not universal. Use it as a risk control, not a return enhancer. Grade A.

### Kelly criterion — and why full Kelly is dangerous
- Kelly maximizes long-run log growth, but MacLean, Thorp & Ziemba (*The Kelly Capital Growth Investment Criterion*, 2011) document its "bad properties": bet sizes are enormous, and the formula is hyper-sensitive to estimated edge — a ~10% error in the mean can imply ~50% overbetting. Overbetting past full Kelly *reduces* growth while increasing ruin risk. Grade A/B.
- MacLean, Ziemba & Blazenko (*Management Science*, 1992): **half-Kelly delivers ~75% of full-Kelly growth with ~50% of the volatility** — the canonical evidence for fractional Kelly. Grade A.
- Ralph Vince's "optimal f" (*Portfolio Management Formulas*, 1990) is Kelly generalized to trade distributions; Vince himself shows trading at optimal f implies drawdowns approaching the size of the largest historical loss × f — practically guaranteed near-ruin drawdowns. Grade B.
- **For an LLM agent this is decisive: the agent cannot reliably estimate its own edge, and Kelly fails worst under edge misestimation. Fixed-fractional at 1% is effectively a deep-fractional Kelly with robustness to being wrong.**

### Equal-weight vs conviction-weight
- DeMiguel, Garlappi & Uppal, *Review of Financial Studies* 2009: naive 1/N equal weighting beat 14 optimization models out-of-sample on Sharpe, certainty-equivalent, and turnover; mean-variance optimization needs ~3,000 months of data (25 assets) to beat 1/N because estimation error swamps optimization gains. Grade A.
- Implication: an LLM's "conviction" is an unvalidated point estimate of expected return — exactly the input DeMiguel et al. show is too noisy to size on. **Equal risk-weight positions; express conviction by trade selection, not size.**

---

## Stops and exits evidence

### Do stops help? It depends on the return process
- Kaminski & Lo, "When Do Stop-Loss Rules Stop Losses?" (*Journal of Financial Markets*, 2014): analytically, under a **random walk, stops always reduce expected return** (you pay the equity premium to sit in cash); under **positive serial correlation (momentum), stops add value** — the "stopping premium" is proportional to return persistence; under **mean reversion, stops destroy value** (you sell exactly when expected return is highest). Empirically, their rule added ~50–100 bps/month during stopped-out periods on 1950–2004 data. Grade A.
- Han, Zhou & Zhu, "Taming Momentum Crashes: A Simple Stop-Loss Strategy" (SSRN, 1926–2013 data): a 10% stop on momentum portfolios cut the worst monthly loss from −49.8% to −11.4% (equal-weighted) and roughly **doubled the Sharpe ratio**; average monthly return rose from 1.01% to 1.73%. Strong evidence stops help momentum/trend positions. Grade B (widely cited working paper).
- **Rule of thumb from the literature: stop-loss trend/momentum entries tightly; do NOT tight-stop mean-reversion entries — use time stops and disaster stops instead.**

### Stop placement methods
- **ATR multiples** (2–3× ATR(14–20)): adapts to the stock's own volatility; the Turtle 2N stop is the canonical published version. Grade B.
- **Structure-based** (below swing low / support): practitioner standard; no strong academic validation, but harmonizes with ATR (use whichever is wider to avoid noise stop-outs). Grade C.
- **Time stops**: exit after N days if thesis hasn't played out; especially apt for mean-reversion trades whose edge decays within days. Consistent with Kaminski-Lo. Grade B.
- **Percent-of-entry stops tighter than ~10% churn badly**: Dai, Marshall, Nguyen & Visaltanachoti ("Risk Reduction Using Trailing Stop-Loss Rules") find transaction costs erase benefits for stops tighter than 10%. Grade B.

### Trailing stops
- Dai et al. and related work: trailing stops beat static stops at protecting accumulated gains; versus buy-and-hold, they give **lower raw returns but better risk-adjusted/downside-risk outcomes**; wider trails (≈1.0–1.5σ) outperform tight ones. Grade B.
- Fits trend positions: trail at 2.5–3× ATR below the highest close since entry; never widen a stop.

### The overnight-gap problem — critical for this agent
- A stop order is only a *trigger*: if price gaps through it overnight, the fill is at the open, not the stop price. **A stop caps intraday adverse moves only; it does NOT cap loss.** Grade A (order mechanics).
- Magnitude: SPY's average absolute overnight gap was ~0.45% in H1 2026 — index gaps are small. **Single stocks are the danger: options-implied earnings moves for large caps typically run 4–13%; realized moves frequently exceed implied**; biotech/FDA and M&A gaps can exceed 30%. Grade B.
- Consequence, since this agent can only act at 9:45 and 15:30: **worst-case loss per position = position size × plausible gap, regardless of stop**. Sizing must be computed against gap risk, not stop distance, whenever a known event (earnings) is scheduled. A 25%-of-equity position gapping −20% costs 5% of the account in one night.

### Bracket orders / take-profit evidence
- Trend/momentum: fixed profit targets truncate the right tail that pays for the strategy — profit targets generally *worsen* trend systems. Grade B/C.
- Mean reversion: taking profit at the mean/target is the thesis itself — profit targets are appropriate and brackets work well. Grade B.
- For an unattended agent, brackets (stop + limit) are still valuable *operationally* on mean-reversion trades: they are the only intraday-acting exit machinery available. Use bracket = disaster stop + target on mean-reversion; stop-only (no target) + trailing on momentum.

---

## Drawdown management

- **Theory:** Grossman & Zhou (*Mathematical Finance*, 1993) — optimal growth under a max-drawdown constraint means risk exposure proportional to the "cushion": as drawdown deepens, exposure shrinks toward zero; as equity recovers, exposure rebuilds. Grade A.
- **Volatility clustering** (Engle ARCH literature; Moreira-Muir): losses cluster in high-vol regimes, so derisking after losses tends to coincide with derisking into high volatility — the same action Moreira-Muir show is Sharpe-improving. Grade A.
- **Equity-curve trading (cutting size after strategy losses):** evidence is mixed. It helps only when strategy returns are serially correlated; Alvarez Quant Trading's backtests found it often *hurts* mean-reversion systems because the best returns come immediately after drawdowns. Grade C.
- **Synthesis:** use *hard circuit breakers* (survival insurance against fat tails, model error, and LLM misbehavior) rather than continuous equity-curve modulation. Ratchet risk down at defined drawdown levels; restore it on defined recovery.
- Streak-based caution has behavioral support: Coval & Shumway show humans *increase* risk after losses; a mechanical rule forcing the opposite direction is the countermeasure.

---

## PDT rule exact mechanics — THE RULE CHANGED IN JUNE 2026

**The historical rule (FINRA Rule 4210, 2001 – June 3, 2026)** — documented because most training data and third-party content describes this regime:
- A "day trade" = buying and selling the *same security* on the *same day* in a **margin account**. "Pattern day trader" = **4+ day trades within 5 rolling business days** (>6% of total trades). PDT-flagged accounts needed **$25,000 minimum equity**. Alpaca enforced by rejecting the 4th day trade when equity < $25k; **paper trading simulated the same rejection**. Grade A.

**What is true NOW (as of July 2026):**
- SEC approved elimination of the PDT framework April 14, 2026; FINRA Regulatory Notice 26-10 set the **effective date June 4, 2026**. The PDT designation, day-trade counting, and the $25,000 minimum are **abolished**, replaced by an "intraday margin" framework (brokers may phase in until October 20, 2027). Grade A.
- **Alpaca implemented the new framework June 4, 2026**: day-trade counting and DTBP logic removed; `daytrade_count` API fields deprecated/removed July 6, 2026; pre-trade checks reject orders creating a margin deficit; **4x intraday leverage eligibility dropped from $25k to $2k**. Grade A/B.

**Design implications:**
1. The agent is **no longer regulatorily blocked from same-day round trips** (e.g., 3:30 stop-out of a 9:45 buy).
2. Do **not** use the 4x intraday leverage. The account behaves as cash-constrained long-only: buying power used ≤ equity.
3. Defensive fallback: if any order is rejected with a PDT/day-trade error (stale simulation, policy reversal), revert to legacy-safe behavior: ≤3 same-day round trips per 5 rolling business days.

---

## Small-account portfolio construction ($5,000, fractional shares)

- **Fractional shares remove the granularity problem**: Alpaca supports fractional market/limit/stop/stop-limit orders (DAY time-in-force) with **$1 minimum notional, 9-decimal quantities**. Note: fractional orders are DAY-only — GTC stop orders may require whole-share quantities; keep positions large enough that whole-share stops approximate the position. Grade A.
- **How many positions:** Evans & Archer (1968): 8–10 stocks eliminate most diversifiable risk. Statman (1987), Campbell et al. (*JF* 2001): idiosyncratic vol has risen; 30+ needed for *full* diversification. But marginal risk reduction beyond ~8 is small relative to the first 5. **Practical optimum: 4–8 positions** ($600–$1,250 each); ETF positions carry near-zero single-name gap risk and count "cheaply" against diversification needs.
- **Minimum practical position:** below ~$200 (4% of equity), a position's contribution is noise. Skip trades that size below this.
- **Cash drag vs opportunity:** on multi-week horizons cash drag on $5k is trivial (~$0.30/day per idle $1,000). Holding 20–40% cash is a cheap option; forced deployment is how overtrading starts. Grade B.
- **Order budget reality:** a bracket consumes multiple order legs; with 8 orders/session, a full session supports ~2–3 new bracketed entries plus 1–2 exits. Plan the session's order list before submitting anything.

---

## Behavioral failure modes (explicit warnings for the LLM)

Documented human failures; an LLM trained on human text can reproduce them, and mechanical rules are the antidote.

1. **Overtrading.** Barber & Odean, "Trading Is Hazardous to Your Wealth" (*JF* 2000; 66,000 households): the most active quintile earned 11.4%/yr vs 17.9% market; net returns decline *monotonically* with turnover. Grade A. → The agent is **not obligated to trade in either window**. "No trade" is the correct output most sessions.
2. **Disposition effect.** Odean (*JF* 1998): investors are ~1.5–2× more likely to sell winners than losers; the winners sold went on to outperform the losers held. Grade A. → Selling decisions must reference thesis and stop levels, never "it's up so lock it in / it's down so wait to break even." Entry price is sunk.
3. **Revenge trading / risk escalation after losses.** Coval & Shumway (*JF* 2005; CBOT traders): morning losers took ~16% more above-average afternoon risk; their loss-driven trades were systematically reversed by the market. Grade A. → After losses, risk goes *down* by rule. Never re-enter a ticker within 2 sessions of being stopped out.
4. **Recency bias / extrapolation.** Greenwood & Shleifer (*RFS* 2014): expectations extrapolate recent returns and are *negatively* correlated with subsequent returns; Barber & Odean (*RFS* 2008): individuals buy attention-grabbing movers to their detriment. Grade A. → The last few trades carry near-zero information about edge; do not abandon or double a strategy on <30 trades of evidence.
5. **Averaging down.** Disposition + revenge combined; concentrates capital in positions with the worst confirmed price action. → Adding to a losing position is prohibited.

---

## The Risk Rulebook (numbered)

*All quantities computed from **current account equity E**. Rules are hard constraints; when two rules give different sizes, the smaller applies.*

**A. Position sizing**
1. **Risk unit:** risk per new trade = **1.0% of E** ($50 on $5,000). After 20+ closed trades with positive expectancy, may raise to 1.5%; never exceed 2%.
2. **Sizing formula:** `Position $ = (0.01 × E) / stop_distance_fraction`. Round with fractional shares to within $1.
3. **Hard caps:** Position $ ≤ **25% of E** (platform cap); positions held through a scheduled earnings date or binary event (FDA, court ruling) ≤ **10% of E** — preferred action is to exit before earnings at the prior 15:30 window. Never buy a single stock within 5 days of its earnings date unless sized ≤10% of E.
4. **Minimum position:** if the formula yields < $200, skip the trade.
5. **No leverage, ever:** total invested ≤ E (never use margin buying power, including Alpaca's post-June-2026 4x intraday allowance).
6. **Equal risk weighting:** every position uses the same 1% risk unit. Conviction selects *which* trades, never *how big*.
7. **Portfolio volatility brake:** if VIX close > 25 or SPY 20-day realized vol > 1.5× its 1-year median, halve the risk unit (0.5%) for new entries and cap gross exposure at 60% of E.

**B. Stops and exits (by strategy type)**
8. **Momentum/trend entries:** GTC stop at entry − **2×ATR(14)** (or below the defining swing low, whichever is wider), submitted in the same session as the entry. Once +1×ATR in profit, convert to a trailing stop 2.5×ATR below the highest close. Stops only tighten, never widen. **No profit target** on trend positions.
9. **Mean-reversion entries:** bracket order: profit-target limit at the reversion objective (e.g., 10/20-day mean) and a **disaster stop at 3×ATR(14)** (wide by design — tight stops destroy mean-reversion edge per Kaminski-Lo). **Time stop:** if neither leg fills in 5 sessions, exit at the next window.
10. **Every share held overnight must have a live stop or bracket resting at the broker.** An unprotected position is a rule violation regardless of P&L.
11. **Gap-risk accounting:** treat worst-case per-position loss as `Position $ × 20%` for single stocks (× 5% for broad ETFs), NOT the stop distance. If the sum of worst-case losses exceeds 15% of E, reduce or refuse new entries.
12. **Exit execution:** all discretionary exits use limit or marketable-limit orders at the 9:45/15:30 windows; never market orders in the first 5 minutes after the open.

**C. Portfolio construction**
13. **3–8 concurrent positions.** Never more than 8; below 3 only when circuit breakers or lack of qualifying setups dictate.
14. **Max 2 positions in the same GICS sector; positions correlated >0.8 count as one slot.**
15. **Cash is a position.** If no setup meets all rules, the correct action is zero orders this session.

**D. Drawdown circuit breakers** (measured from peak equity high-water mark; levels release when equity recovers above the trigger)
16. **−5% from peak:** risk unit cut to 0.5% of E; max 1 new entry per session.
17. **−10% from peak:** no new single-stock entries (broad ETFs only, ≤2); gross exposure reduced to ≤50% of E at the next window.
18. **−15% from peak:** liquidate to cash at the next 15:30 window; no new entries for 5 trading sessions; resume at Rule 17 restrictions, only after journaling a specific hypothesis for what failed.
19. **Daily brake:** if equity drops ≥3% intraday-to-date at a decision window, no new buys that window (exits still allowed).
20. **Streak brake:** after 3 consecutive losing closed trades, halve the risk unit until 2 of the next 4 trades close profitably. Never increase size after losses.

**E. Regulatory compliance**
21. **Current regime (post-June 4, 2026):** PDT retired; no day-trade count limit, no $25k requirement. Same-day round trips permitted. Because the agent never uses margin (Rule 5), intraday margin deficits cannot occur.
22. **Fallback:** any PDT/day-trade/margin order rejection → revert to legacy-safe mode: max 3 same-day round trips per 5 rolling business days; never open a morning position you're unwilling to hold overnight.
23. **Voluntary churn cap:** ≤2 same-day round trips per week; portfolio turnover target <25% of E per week.

**F. Behavioral guards**
24. **Never add to a losing position.** One add to a *winning* trend position is permitted (at +1×ATR, sized at 0.5% risk), nothing further.
25. **Sell-decision protocol:** evaluate each holding as "would I buy this today at this price?" — entry price and open P&L are prohibited inputs to hold/sell reasoning (stops excepted).
26. **No re-entry** into any ticker within 2 full sessions of being stopped out of it.
27. **No strategy abandonment or size escalation on <30 closed trades** of evidence; log every trade's planned R, realized R, and rule compliance; review expectancy only on ≥30-trade samples.
28. **Order budget discipline:** list the session's intended orders before submitting; if >8, cut lowest-priority *entries* first — protective stops and exits are never cut.

---

## Sources

**Regulatory / broker (Grade A):**
- FINRA Regulatory Notice 26-10: https://www.finra.org/rules-guidance/notices/26-10
- SEC PDT definition: https://www.investor.gov/introduction-investing/investing-basics/glossary/pattern-day-trader ; https://www.sec.gov/files/daytrading.pdf
- Alpaca — PDT retirement / Intraday Margin Framework: https://alpaca.markets/blog/finra-retires-the-pdt-rule-introducing-alpacas-new-intraday-margin-framework/
- Alpaca paper-trading docs (legacy PDT simulation): https://github.com/alpacahq/user-docs/blob/master/content/trading-on-alpaca/paper-trading.md
- Alpaca margin docs: https://docs.alpaca.markets/docs/margin-and-short-selling ; fractional: https://docs.alpaca.markets/us/docs/fractional-trading
- Schwab on the change: https://www.schwab.com/learn/story/sec-approves-scrapping-25000-day-trader-minimum

**Academic:**
- Kaminski & Lo: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=968338
- Han, Zhou & Zhu: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2407199
- Dai et al., trailing stops: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3338243
- MacLean, Thorp & Ziemba: https://www.worldscientific.com/worldscibooks/10.1142/7598
- DeMiguel, Garlappi & Uppal (RFS 2009): https://academic.oup.com/rfs/article-abstract/22/5/1915/1592901
- Moreira & Muir (JF 2017): https://onlinelibrary.wiley.com/doi/abs/10.1111/jofi.12513 ; Cederburg et al. (JFE 2020): https://www.sciencedirect.com/science/article/abs/pii/S0304405X2030132X
- Barber & Odean (JF 2000): https://faculty.haas.berkeley.edu/odean/papers%20current%20versions/individual_investor_performance_final.pdf
- Odean (JF 1998): https://faculty.haas.berkeley.edu/odean/papers%20current%20versions/areinvestorsreluctant.pdf
- Coval & Shumway (JF 2005): https://onlinelibrary.wiley.com/doi/abs/10.1111/j.1540-6261.2005.00723.x
- Grossman & Zhou lineage: https://www.researchgate.net/publication/280193536_Towards_optimal_portfolio_strategy_to_control_maximum_drawdown
- Diversification review (incl. Evans & Archer, Statman, Campbell et al.): https://www.mdpi.com/1911-8074/14/11/551
- Earnings jump magnitudes (JFE 2025): https://www.sciencedirect.com/science/article/abs/pii/S0304405X25000182

**Practitioner (Grade B/C):**
- Van Tharp position sizing: https://vantharpinstitute.com/van-tharp-teaches-position-sizing-strategies-and-risk-management/ ; R-multiples: https://traderlion.com/risk-management/r-and-r-multiples/
- Turtle sizing: https://www.quantifiedstrategies.com/position-sizing-in-a-turtle-trading-system/
- Equity-curve trading: https://alvarezquanttrading.com/blog/trading-the-equity-curve/
- Profit-taking backtests: https://www.quantifiedstrategies.com/profit-taking-strategy/
- Gap mechanics: https://www.strasmore.com/blog/why-do-stocks-gap-overnight ; https://www.ebc.com/forex/earnings-season-guide-gaps-risk-position-size
- Implied earnings moves: https://www.tipranks.com/news/options-volatility-and-implied-earnings-moves-this-week-january-27-january-31-2025
