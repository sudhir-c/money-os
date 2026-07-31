# Short-Term Mean Reversion Strategies — Knowledge Base
*Scope: US stocks/ETFs, long-only, $5k Alpaca paper account, decisions at 9:45 AM and 3:30 PM ET only. Evidence grades: A = peer-reviewed/replicated academic; B = credible practitioner with published backtests; C = lore/small-sample.*

---

## 1. Connors RSI(2) Pullback Family (core index-ETF workhorse)

**Origin:** Larry Connors & Cesar Alvarez, *Short Term Trading Strategies That Work* (2008) and related Connors Research publications. The most replicated retail mean-reversion rule set in existence.

### 1a. Classic RSI(2) — Grade: B (highest-confidence practitioner strategy; partially corroborated by academic index-autocorrelation evidence)

**Rules (canonical, on SPY/QQQ daily bars):**
- IF close > 200-day SMA (trend filter)
- AND 2-period RSI of closes < 10 (stricter variant: < 5 — lower thresholds improve avg per-trade)
- THEN buy at the close.
- EXIT when close > 5-day SMA (alternatives: RSI(2) > 65–70, or first close above prior day's high).
- No stop-loss (deliberate — see §Failure Modes). Typical hold: 2–5 days. Optional time stop ~5–10 days.

**Documented performance (SPY 1993–2024, QuantifiedStrategies replication):** without trend filter: ~9% CAGR, ~0.9% avg gain/trade, 34% max DD, invested only 28% of time; with the 200-day filter: avg gain/trade ~0.95%, max DD 31%, CAGR 6.8% (exposure 18%). Win rate ~75–76%; average hold ~2–4 days. Time-invested-adjusted returns are far better than buy-and-hold; absolute returns are not.

**Out of sample:** survived 17+ years since book publication with slight decay; independent replications agree the edge persists on index ETFs, with degradation concentrated in prolonged bear phases (2008, March 2020 — win rates fell below 60% as dips kept dipping). McLean–Pontiff: published anomalies lose roughly half their Sharpe post-publication — RSI(2) has held up better than typical but expect ~half of book-era per-trade edge.

### 1b. Cumulative RSI(2) — Grade: B

Sum of the last 2 days' RSI(2) values; filters for *persistent* oversold.
- IF close > 200-day SMA AND [RSI(2) today + RSI(2) yesterday] < 35 THEN buy at close. EXIT when RSI(2) > 65.
- Replications: ~26% annual return, 1.18 Sharpe, 37% max DD over 24 years (aggressive sizing); conservative SPY replications ~9% CAGR at 28% exposure with ~80%+ win rate. Practitioners increasingly prefer this over raw RSI(2) as the raw version got crowded.

### 1c. RSI 25/75 and TPS scale-in (from *High Probability ETF Trading*, 2009) — Grade: B

**RSI 25:** IF ETF > 200-day SMA AND RSI(4) < 25 THEN buy at close; EXIT when RSI(4) > 55.

**TPS (Time-Price-Scale-in)** — the best structural fit for a twice-daily agent because scaling replaces intraday reaction:
- IF ETF > 200-day SMA AND RSI(2) < 25 for 2 consecutive days THEN buy 10% of intended position at close.
- IF price closes lower than your last entry price, add 20%; lower again, add 30%; lower again, add 40% (total 100% across up to 4 closes).
- EXIT everything when RSI(2) > 70.
- Win rates ~90%+ (inflated by scale-in accounting; per-position risk is the real constraint). With the 25% position cap, the full ladder = 2.5% / 5% / 7.5% / 10% of the $5k account — implementable with fractional shares, ≤1 order per session.

### 1d. ConnorsRSI composite — Grade: B/C
CRSI(3,2,100) = average of RSI(3), RSI(2)-of-streak, and 100-day PercentRank of 1-day return. Buy pullbacks in uptrends when CRSI < 10–20, exit CRSI > 70–90. Fewer independent replications than plain RSI(2). Use as a confirmer, not standalone.

**Execution at the agent's windows:** All are close-entry strategies. Compute indicators at 3:30 PM using the 3:30 price as a close proxy and enter before the bell — this matches the backtests almost exactly (when in doubt require RSI(2)<5 at 3:30 for margin of safety). Exits likewise at 3:30. Entering next morning at 9:45 is the documented-inferior variant: most of the mean-reversion payoff is the overnight session (§6), so prefer 3:30 entries.

---

## 2. Double 7s and N-day-low Pullback Family

### 2a. Double 7s — Grade: B for concept, C for current edge
**Rules:** IF close > 200-day SMA AND close = lowest close of last 7 days THEN buy at close. EXIT when close = highest close of last 7 days. No stop.
**Performance:** 1,189 trades on SPY, avg +0.63%/trade, high win rate. **However** Cesar Alvarez's own 2008–2015 re-test (he co-created it) found post-publication CARs fell below buy-and-hold; one catastrophic 2008 trade dominated; he concluded "little to no edge anymore." The clearest documented post-publication decay in the Connors canon. Alvarez tested execution at **next open** — directly compatible with the 9:45 window — but treat Double 7s as a confirming signal, not a standalone allocation.

### 2b. Consecutive-down-days / down-week variants — Grade: B
- IF SPY down 4 consecutive closes THEN buy at close; EXIT on first close above prior close (~32 occurrences 2005–2023; positive expectancy, low frequency).
- Down-week variant: buy after a down week, hold one week: avg +0.44%/trade, ~9.3% annualized, 36% max DD. Works only post-~1988 (see §Regime).

### 2c. Turnaround Tuesday — Grade: B (31-year sample, multiple independent replications)
**Base rules (Quantitativo, SPY):** IF today is Monday AND Monday close < Friday close AND Friday close < Thursday close THEN buy (tested at Tuesday open; Monday 3:30–close is the near-equivalent and captures the overnight bounce). EXIT on first close above previous day's high. Sharpe 1.77, 6.2% CAGR, 18% max DD, 11% exposure over 31 years. Improved QQQ version (any 2-down-day sequence entering Tue/Wed): Sharpe 1.52, 11.4% CAGR, 70% win rate. Profitable in 2008, 2002, and 2022 bear years — unusual among long-only MR setups.
**Execution:** signal fully known at Monday 3:30 check; enter then or Tuesday 9:45.

---

## 3. Band / Deviation-from-MA Reversion (Bollinger, IBS, lower-band)

### 3a. Internal Bar Strength (IBS) — Grade: B (two decades of practitioner evidence: Alvarez, Kinlay, QuantifiedStrategies)
IBS = (Close − Low) / (High − Low). On index ETFs: IBS < 0.2 → next-day avg return ≈ +0.35%; IBS > 0.8 → ≈ −0.13%.
**Rules:** IF SPY/QQQ IBS < 0.2 (optionally > 200-day SMA) THEN buy at close; EXIT when IBS > 0.8 or close > prior high. Works notably well combined with RSI(2) (require both). IBS at 3:30 PM is a good proxy for the daily bar ~95% of days.

### 3b. Quantitativo lower-band + IBS ("2.11 Sharpe" strategy) — Grade: B
**Rules (QQQ):** lower band = 10-day rolling high − 2.5 × 25-day rolling mean of (High−Low). IF close < lower band AND IBS < 0.3 THEN buy at close. EXIT when close > yesterday's high, OR close < 300-day SMA (regime stop). Backtest 1993–2024: Sharpe 2.11, 13.0% CAGR, −20.3% max DD, ~20% exposure. Parameter-insensitive; instrument mattered (QQQ ≫ SPY).

### 3c. Classic Bollinger reversion — Grade: C→B
ETFs closing below the lower 20-day 2σ band (especially 2 consecutive closes) in bull regimes revert upward; in bear regimes the bounce fades within ~2 weeks. Mostly redundant with IBS/RSI(2). Rule if used: IF close > 200-day SMA AND close < lower BB(20,2) THEN buy at close; EXIT at middle band (20-day SMA).

---

## 4. VIX-Spike / Panic Entries into Index ETFs

### 4a. Connors VIX Stretch — Grade: B/C (logic sound; published sample small)
**Rules:** IF SPY > 200-day SMA AND VIX ≥ 5% above its 10-day SMA for 3+ consecutive days THEN buy SPY at close. EXIT when RSI(2) of SPY > 65. Backtest: 33 trades, 84.8% win rate, avg hold < 5 days. Small N — treat as a conviction-sizing input layered on RSI(2) signals.

### 4b. CVR3 (Connors VIX Reversal III) — Grade: C
IF VIX daily low > its 10-day SMA AND VIX close ≥ 10% above 10-day SMA AND VIX close < VIX open THEN buy the index at close; exit on mirror conditions or after 2–4 days. Infrequent; flagged as needing verification.

**Key panic-regime caveat:** the 200-day filter means true crash bottoms (2008, COVID) are *excluded* — a feature (caps the left tail), but these are "buy normal fear in bull markets" systems, not crash-bottom catchers. All inputs observable at 3:30 PM.

---

## 5. Gap-Down Reversion — the sharpest instrument distinction in this report

**Index ETFs (SPY/QQQ): fade small gaps. Individual stocks: do NOT fade large gaps.**

- SPY gap-downs between −0.15% and −0.6% show intraday mean reversion; gaps below −0.6% show much weaker reversion. SPY 1%+ gap-downs average +0.21% open-to-close, but day-of-week matters: Tue–Thu gap-downs revert most reliably (Thursday gap-fill ~82%); **Monday gap-downs bounce least** (~65% fill) — don't buy scary Monday opens.
- QuantRocket (1-minute data, 2014–2020, top-decile dollar-volume stocks): **individual stocks with large down-gaps continue falling** — short-continuation earned Sharpe 1.30; only *small* gaps in intact uptrends reverted. Entry 5–10 minutes after the open beat entry at the open — *exactly* the 9:45 window.
- Grade: B (consistent across 3+ independent sources).

**Rules for the agent (9:45 AM window only):** IF SPY/QQQ gapped down 0.15–0.6% AND it's Tue–Fri AND price > 200-day SMA THEN buy at 9:45; EXIT at 3:30 same day if gap filled, else next 3:30 or on close > prior high. Never apply this to single stocks.

---

## 6. Overnight Mean Reversion (noted for completeness — poor cadence fit)

Cross-sectional overnight-reversal effect (buy weak-overnight assets at open, exit at close): Sharpe ~2+ on equity futures/sector ETFs 2007–2025 (QuantReturns). Requires execution *at* open and close daily plus daily round trips — skip as a system. Keep the insight: **most index MR payoff accrues overnight**, which is why 3:30 PM entries dominate 9:45 AM entries for close-signal strategies.

---

## Regime and Instrument Suitability — where reversion is actually exploitable

1. **The index regime flip is real and well documented.** S&P 500 daily-return autocorrelation was strongly *positive* ~1940 to mid-1990s (daily momentum era), then flipped *negative* in the late 1990s. Everything in §1–§4 monetizes this negative autocorrelation. It is a regime, not a law: documented weakening since ~2013, and daily follow-through could return. Grade A for the historical fact; future persistence is assumption.
2. **Individual liquid stocks are the wrong place for short-term reversion.** Medhat & Schmeling, "Short-Term Momentum," *RFS* 2022 (Grade A): short-term **reversal is concentrated in low-turnover, illiquid stocks** (largely compensation for liquidity provision; dies after costs), while **high-turnover, large, liquid stocks exhibit short-term *momentum*** that survives costs, across 22 developed markets. Naive STR fails after costs.
3. **Practical translation:** run reversion on **index/sector ETFs (SPY, QQQ, IWM, sector SPDRs)** where post-2000 negative daily autocorrelation is the documented anomaly and spreads are ~1bp. Avoid dip-buying individual small caps and avoid *fading* liquid single-name momentum. Single-stock MR at $5k cannot be diversified adequately — stick to ETFs.
4. **Bull/bear conditioning:** long-only MR win rates deteriorate in bear regimes. The 200-day (or 300-day) filter is the single most consistently validated conditioning variable across every source reviewed. Turnaround Tuesday is the notable exception that worked in bear years.

---

## Failure Modes and Risk Profile

**Negative skew is structural.** Long-only MR = selling insurance: ~70–85% small wins, occasional −10–30% single-trade losses when a dip becomes a trend break. Alvarez's stock-MR baseline: worst 50 trades averaged −17.2% each. Portfolio max DDs of 30%+ appear in nearly every honest multi-decade backtest. **All these signals fire simultaneously in a crash** (RSI(2), IBS, band, VIX-stretch are one trade wearing four hats). Cap total MR exposure (≤2 concurrent index-ETF MR positions = 50% of equity) and treat multiple simultaneous signals as one signal.

**The stop-loss paradox — strong, replicated evidence (Grade B, 3+ independent sources).** Connors/Alvarez: stop-losses generally *reduce* short-term MR performance. Alvarez's dedicated study (2005–2015, Russell 1000 MR system): no stop = best CAR (14.1%, 20.7% DD); 3% stop cut DD only to 17.2% while cutting returns; tight ATR stops badly hurt; only very wide stops (~2.5–3× ATR, or 30%+) approached no-stop results. Mechanism: MR entries are *designed* to buy amid adverse movement; a tight stop ejects you at maximum stretch, right before the reversion pays. Evidence-backed substitutes: (1) **time stops** (exit after 5–10 bars), (2) **regime filter** (200/300-day SMA — where drawdown protection actually comes from), (3) **position sizing / scale-in** (TPS), (4) at most a **disaster stop** 30–50% below entry. An autonomous agent should encode: *never attach a 2–5% stop to a mean-reversion entry.*

**Other failure modes:** post-publication decay (Double 7s is the documented casualty; assume half the printed per-trade edge for everything); low exposure (~20–30%) means a few bad trades dominate annual results; earnings/news gaps in single names (another reason for ETFs); bear-market clustering of losses; regime death — if daily autocorrelation reverts to pre-1990s positive, this entire family stops working. The weekly Sunday session should track the rolling 1-year hit rate of a benchmark rule (e.g., paper-RSI(2)) as a kill switch.

---

## What Fits the 2-Checks-Per-Day Cadence Best

The cadence is barely a constraint — this strategy class is daily-bar based. Ranked fit:

1. **RSI(2)/cumulative-RSI/IBS composite on SPY+QQQ, entered at 3:30 PM** — best evidence, best window match. Holds 2–5 days → no day trades.
2. **TPS scale-in (SPY or QQQ), 3:30 PM** — one order per day max, mechanical pre-committed ladder; ideally suited to an agent that cannot monitor intraday and must not improvise adds.
3. **Turnaround Tuesday (SPY/QQQ)** — signal known at Monday 3:30; enter Monday close or Tuesday 9:45; exit within 1–3 days. High Sharpe per unit of exposure; worked in bear years.
4. **VIX-stretch conviction overlay, 3:30 PM** — use to upsize an RSI(2) entry toward the 25% cap, not as a separate position.
5. **Index-ETF small-gap fade, 9:45 AM** — the only setup where 9:45 is *optimal*. Same-day 3:30 exit; use sparingly.
6. **Avoid:** overnight open-to-close systems (wrong windows), single-stock gap fades (evidence says continuation), single-stock dip buying at this account size.

**Detection asymmetry:** everything detectable at 3:30 PM (RSI, IBS, N-day lows, VIX stretch, down-day counts, band breaches) should be *entered* at 3:30. Signals conditional on the daily *close* itself carry ~30 min of slippage risk; require a margin (RSI(2) < 5 rather than < 10, IBS < 0.15 rather than < 0.2) so marginal-signal flips are immaterial. The 9:45 window is for: next-open executions of prior-close signals, gap-fade entries, and exit management after overnight moves.

**PDT note:** FINRA's $25k PDT minimum was eliminated effective June 4, 2026, but broker implementation varies (phase-in until Oct 2027) — verify Alpaca's enforcement empirically before relying on same-day round trips; multi-day holds (every top-ranked strategy above) sidestep the issue entirely. Max 8 orders/session is never binding (worst case ~2–4 orders). Fractional shares make the 25% cap exactly implementable.

---

## Sources

**Connors family:** [QuantifiedStrategies — RSI 2](https://www.quantifiedstrategies.com/rsi-2-strategy/) · [QS Substack — RSI 2 stats](https://quantifiedstrategies.substack.com/p/rsi-2-strategy-explained-larry-connors) · [StockCharts — RSI(2)](https://chartschool.stockcharts.com/table-of-contents/trading-strategies-and-models/trading-strategies/rsi-2) · [QS — Double Seven](https://www.quantifiedstrategies.com/larry-connors-double-seven-strategy-does-it-still-work/) · [Alvarez — Double 7's decay](https://alvarezquanttrading.com/blog/double-7s-strategy/) · [QS — Cumulative RSI](https://www.quantifiedstrategies.com/cumulative-rsi-indicator/) · [StatOasis — Cumulative RSI](https://statoasis.com/post/cumulative-rsi-strategy-a-smarter-twist-on-rsi(2)-for-s-p-500) · [Elite Trader — Cum RSI sensitivity](https://www.elitetrader.com/et/threads/larry-connors-cumulative-rsi-26-annual-return-now-with-sensitivity-analysis.379982/) · [QS — TPS](https://www.quantifiedstrategies.com/tps-trading-strategy/) · [QS — RSI 25/75](https://www.quantifiedstrategies.com/larry-connors-rsi-25-rsi-75/) · [QS — ConnorsRSI](https://www.quantifiedstrategies.com/connors-rsi/) · [Setup4Alpha — book replication](https://setup4alpha.substack.com/p/short-term-trading-strategies-that-work-realtest)

**Stops research:** [Alvarez — Maximum Loss Stops](https://alvarezquanttrading.com/blog/maximum-loss-stops-do-you-really-need-them/) · [Alvarez — Adding Stops to MR](http://alvarezquanttrading.com/2016/03/16/adding-stops-and-scaling-out-to-a-mean-reversion-strategy/) · [Better System Trader ep. 037](https://bettersystemtrader.com/037-cesar-alvarez-studies-stop-losses/)

**Band/IBS:** [QS — IBS strategies](https://www.quantifiedstrategies.com/ibs-internal-bar-strength-indicator-strategies/) · [Alvarez — IBS for MR](https://alvarezquanttrading.com/blog/internal-bar-strength-for-mean-reversion/) · [Kinlay — IBS](https://jonathankinlay.com/2019/07/the-internal-bar-strength-indicator/) · [Quantitativo — 2.11 Sharpe MR](https://www.quantitativo.com/p/a-mean-reversion-strategy-with-211) · [Quantitativo — robustness](https://www.quantitativo.com/p/robustness-of-the-211-sharpe-mean) · [Atlantis Press — Bollinger analysis](https://www.atlantis-press.com/article/125991306.pdf)

**VIX:** [TradingMarkets — Trading the VIX](https://tradingmarkets.com/recent/trading_the_vix_short_term_strategies_for_high_probability_traders-680225) · [StockCharts — CVR3](https://chartschool.stockcharts.com/table-of-contents/trading-strategies-and-models/trading-strategies/cvr3-vix-market-timing)

**Gaps/overnight/day-of-week:** [QuantRocket — Buy or Sell Down Gaps](https://www.quantrocket.com/blog/buy-or-sell-down-gaps/) · [QS — Gap fill strategies](https://www.quantifiedstrategies.com/gap-fill-trading-strategies/) · [SharePlanner — Fading SPY/QQQ gaps](https://www.shareplanner.com/blog/strategies-for-trading/fading-the-gap-how-large-overnight-moves-in-spy-and-qqq-play-out-during-the-trading-day.html) · [QuantReturns — Overnight MR](https://quantreturns.com/strategy-review/overnight-mean-reversion/) · [Quantitativo — Turnaround Tuesdays](https://www.quantitativo.com/p/turnaround-tuesdays-on-steroids) · [QS — Turnaround Tuesday](https://www.quantifiedstrategies.com/turnaround-tuesday-strategy/) · [QS — Four down days](https://www.quantifiedstrategies.com/four-down-days-and-up/)

**Academic/regime:** [Medhat & Schmeling (RFS 2022, SSRN)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=3795253) · [Klement — reversal vs momentum](https://klementoninvesting.substack.com/p/short-term-reversal-or-short-term) · [Dai/Medhat/Novy-Marx — Liquidity Provision](https://mysimon.rochester.edu/novy-marx/research/RRLP.pdf) · [Alpha Architect — Short-Term Signals](https://alphaarchitect.com/alpha-from-short-term-signals/) · [Alpha Architect — STR](https://alphaarchitect.com/2015/01/14/quantitative-momentum-research-short-term-return-reversal/) · [Quantpedia — STR in Stocks](https://quantpedia.com/strategies/short-term-reversal-in-stocks) · [Price Action Lab — Autocorrelation drop](https://www.priceactionlab.com/Blog/2020/03/autocorrelation/) · [Price Action Lab — MR waning](https://www.priceactionlab.com/Blog/2021/09/mean-reversion-waning/) · [Oxford JFEC — Autocorrelation of the Stock Market](https://academic.oup.com/jfec/article/19/1/39/6124729) · [QS — Negatively skewed strategies](https://www.quantifiedstrategies.com/negatively-skewed-trading-strategies/)

**Execution constraints:** [Alpaca — Fractional docs](https://docs.alpaca.markets/us/docs/fractional-trading) · [Schwab — $25k minimum scrapped](https://www.schwab.com/learn/story/sec-approves-scrapping-25000-day-trader-minimum) · [QuantInsti — FINRA PDT removal](https://www.quantinsti.com/articles/finra-pdt-rule-removal-2026/)
