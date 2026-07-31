# Market Regime Detection & Sector/Macro Rotation — Knowledge Base
*For a $5,000 long-only Alpaca paper account; decisions at 9:45 AM / 3:30 PM ET; weekly regime assessment Sundays; max 25% per position; cash is the only short.*

**Evidence grades used throughout:** **A** = multiple academic studies + out-of-sample persistence; **B** = solid published evidence but meaningful caveats/decay; **C** = folklore-grade, mixed, or post-publication failure. Post-publication decay is flagged explicitly — it is the single most consistent finding across this research.

---

## Regime indicators + rules

### 1. Trend: price vs long-term moving average — Grade A (for drawdown reduction), B- (for raw returns)

The workhorse. Faber's "A Quantitative Approach to Tactical Asset Allocation" (2006, updated 2013): hold the asset when monthly close > 10-month SMA (≈ 200-day MA), else hold T-bills, evaluated **monthly only**. On US stocks 1901–2012 this roughly matched buy-and-hold returns with ~1/3 lower volatility and cut max drawdown from ~-84% to ~-50%; a daily-200dMA variant on the S&P 1929–2019 cut max drawdown from 83% to ~30% at the cost of several points of CAGR in bull decades. Out-of-sample 2006–2012 the model performed as advertised (Faber's 2013 update: GTAA beat buy-and-hold by ~2%/yr with 80% smaller drawdowns).

**The honest caveat:** after the 2009 bottom, the timing model **underperformed stocks in 6 of the next 8 years**. In persistent bull markets the 200-day rule generates whipsaws (2010, 2011, 2015–16, Dec 2018, and the 2020 V-recovery where it exited near the March low and re-entered months later). Faber's real-money GTAA ETF was eventually shuttered. AQR's "A Century of Evidence on Trend-Following" (Hurst, Ooi, Pedersen 2017) found time-series momentum positive in **every decade 1880–2016** across 67 markets — but returns in the most recent decade were the weakest of the sample. Conclusion: trend filters are **insurance, not alpha**. Expect to pay 1–3%/yr in bull markets to avoid -30 to -50% drawdowns.

**Rules for the agent:**
- Primary: SPY weekly close vs 200-day SMA. Above = uptrend, below = downtrend.
- Slope: 200-day SMA today vs 20 trading days ago. Rising slope + price above = confirmed uptrend.
- **Whipsaw dampers (important):** act on Friday/month-end closes, not intraday; require close >1% beyond the MA (hysteresis band) or 3+ consecutive daily closes to flip state (Alvarez Quant Trading showed 2–3 day confirmation cuts trades ~in half with equal or better drawdown protection).

### 2. Volatility regime: VIX level + term structure — Grade B

- **VIX absolute level:** <15 calm; 15–20 normal; 20–30 elevated; >30 stress; >40 crisis/capitulation. Important nuance: **high VIX predicts high *average* forward returns** (VIX>30 → positive 6-month returns 70–83% of the time, avg ~+12%) but **not better risk-adjusted returns** — variance is enormous (Elm Wealth). So VIX>30 is *not* a sell signal; it's a "do not initiate new risk, do not panic-sell into the hole" signal.
- **Term structure (the better signal):** VIX vs VIX3M (tickers ^VIX, ^VIX3M; ratio available free from CBOE/most data feeds). **Contango (VIX/VIX3M < 1, typically ~0.90–0.95)** prevails ~85% of days = normal regime. **Backwardation (ratio > 1)** = acute stress; it has appeared around every major fast drawdown since 1990. But: (a) it's a *state* indicator, not a timing signal — during backwardation the market kept falling 74% of the time short-term; the edge comes from waiting for backwardation to *resolve* back into contango (re-entry signal); (b) **2022 blind spot:** in the slow grinding 2022 bear both VIX and VIX3M were elevated so the curve stayed in contango — term structure catches 2008/2020-style vol shocks, not grinding rate-driven bears. Pair it with the trend filter, which caught 2022.

**Rules:** VIX/VIX3M > 1.0 = stress flag on. Stress flag off (and re-risk window opens) when ratio < 0.95 for 3 consecutive days.

### 3. Breadth — Grade B- (confirmation), B (Zweig thrust as bullish trigger)

- **% of stocks above their 200-day MA** ($S5TH / $MMTH on StockCharts/TradingView): >70% = broad healthy uptrend; 40–70% = mixed/chop; <30% = entrenched downtrend and, when it turns up from <20%, historically a washout-bottom zone. Divergence (index at highs, breadth falling) is an early-warning, not a timing signal.
- **Alpaca-computable proxy (recommended):** count how many of the 11 SPDR sector ETFs (XLK XLY XLC XLF XLI XLB XLE XLV XLP XLU XLRE) closed above their own 200-day MA. ≥8 = broad, 4–7 = mixed, ≤3 = broken. Also check RSP (equal-weight S&P) vs its 200-day — if SPY is above but RSP is below, the rally is narrow (the 2023 megacap-concentration problem).
- **Zweig Breadth Thrust:** 10-day EMA of NYSE advances/(advances+declines) moving from <0.40 to >0.615 within 10 sessions. Rare (~1x/1–2 yrs at most); historically followed by strongly positive 6–12 month returns. Treat a fresh thrust as permission to re-risk quickly after a decline even if the 200-day rule hasn't repaired yet. Sample size is small (~20 signals since 1945), hence B not A.

### 4. Credit spreads — Grade B

**ICE BofA US High Yield OAS — FRED series `BAMLH0A0HYM2`, free, daily.** The single best non-equity risk gauge available to this agent. Benchmarks: <350bp = risk-on/complacent; 350–500 = normal-to-caution; **>500bp sustained = genuine stress, historically leads recessions by 6–12 months**; >800 = severe. Direction matters as much as level: **a widening of >75–100bp over 4 weeks from any base is a de-risking flag** even if the absolute level is still low. HY OAS tends to lead equity drawdowns by 1–3 months and, unlike breadth, cannot be distorted by 7 megacaps.

### 5. Risk-on/risk-off ratios: defensive vs cyclical — Grade C (use as tiebreaker only)

XLY/XLP (discretionary/staples) and XLU relative strength vs SPY are widely cited: defensives leading = risk-off. The premise is sound and the pattern showed up before/during 2000, 2008, 2022 — but SentimenTrader's formal test found the discretionary/staples ratio is **not a robust standalone timing signal** (too many false positives, and both legs are contaminated by single-stock effects — AMZN/TSLA dominate XLY). Use: compute 3-month relative return of XLP+XLU average vs SPY. Defensives outperforming by >3% over 3 months while SPY is still near highs = subtract one point in the composite score. Never act on this alone.

### 6. Macro overlays: yield curve, Sahm rule — Grade B historically, demoted after 2022–24

The 2s10s curve (FRED `T10Y2Y`) inverted for 26 months (2022–24) — longest ever — and un-inverted with **no recession**; the Sahm rule (FRED `SAHMREALTIME`) triggered July 2024, also falsely (its own creator disavowed the trigger, citing labor-supply distortion). Lesson: post-COVID, macro recession indicators misfired while **price-based indicators (trend, credit, vol) remained the reliable ones**. Keep macro series as context in the Sunday thesis write-up, but give them **zero weight in the mechanical score**.

### 7. Regime-conditional strategy selection: how strong is the evidence really? — Grade B for the phenomenon, C for clean exploitation

The academic base is real: returns show **continuation at 3–12 month horizons** (momentum — Jegadeesh-Titman and hundreds of successors) and **reversal at multi-day horizons** (short-term mean reversion — Poterba-Summers 1988 and the daily-reversal literature), and time-series momentum works precisely because trends persist. Regime-switching models (e.g., ScienceDirect 2023 regime-switching momentum/mean-reversion; the "Slow Momentum with Fast Reversion" changepoint paper, +1/3 Sharpe improvement) confirm that momentum earns its keep in trending states and bleeds in chop. **But** real-time regime classification is noisy — you know a regime mostly after it has been running for weeks. The practical implication is *not* "predict the regime then pick the strategy"; it is **"let slow signals (200-day, credit) set the exposure level, and only apply momentum stock/sector selection when the trend state is ON."** Moreira & Muir (2017, JF) found vol-scaling improves Sharpe on the market factor, but Cederburg et al. (2020, JFE) replication across 103 strategies found **no systematic Sharpe improvement** — so treat vol-targeting as a mild overlay (trim size when VIX>25), not as a core edge.

---

## The Sunday regime checklist

Run in this order every Sunday. All inputs computable from Alpaca daily bars + one FRED call + one CBOE/VIX quote. Score = sum of points, range 0–10.

| # | Check | How to compute | Points |
|---|-------|----------------|--------|
| 1 | **SPY trend** | Friday close vs 200-day SMA | Above by >1% = **+2**; within ±1% = +1; below by >1% = 0 |
| 2 | **Trend quality** | 200-day SMA level today vs 20 sessions ago | Rising = **+1**; flat/falling = 0 |
| 3 | **Breadth** | # of 11 sector ETFs above own 200-day MA | ≥8 = **+2**; 4–7 = +1; ≤3 = 0 |
| 4 | **Equal-weight confirm** | RSP Friday close vs its 200-day SMA | Above = **+1**; below = 0 |
| 5 | **Volatility** | VIX level and VIX/VIX3M | VIX<20 and ratio<0.95 = **+2**; VIX 20–30 or ratio 0.95–1.0 = +1; VIX>30 or ratio>1.0 = 0 |
| 6 | **Credit** | FRED BAMLH0A0HYM2, latest + 4-wk change | <400bp and not +75bp wider in 4 wks = **+2**; 400–500 or widening = +1; >500bp = 0 |
| 7 | **Defensive leadership** (tiebreaker) | (XLP+XLU)/2 vs SPY, trailing 3-mo return | Defensives outperforming SPY by >3% = **−1**; else 0 |

**Regime mapping (score → posture):**

| Score | Regime | Equity exposure | Portfolio shape |
|-------|--------|-----------------|-----------------|
| **8–10** | **Aggressive (risk-on trend)** | 85–100% | 4–5 positions: momentum sector ETFs / leaders + SPY core; full momentum playbook active |
| **5–7** | **Neutral (mixed/chop)** | 50–70% | SPY/RSP core + at most 2 satellites; favor mean-reversion entries (buy weakness at support) over breakout-chasing; rest in SGOV/BIL |
| **3–4** | **Defensive (deteriorating)** | 25–45% | Only defensive holdings allowed as equity: XLP, XLU, XLV, GLD (≤15%); no new cyclical/growth positions; rest SGOV/BIL |
| **0–2** | **Cash-heavy (risk-off)** | 0–25% | SGOV/BIL as the base; optional single ≤15% GLD sleeve; equity only via XLP/XLU if score is 2 and improving |

**Hysteresis rules (anti-whipsaw — these matter more than the exact thresholds):**
- Move only **one regime tier per week** in the risk-on direction (e.g., cash-heavy → defensive → neutral). De-risking can jump multiple tiers immediately.
- Do not flip a tier unless the score has crossed the boundary by ≥1 point or has held the new level for 2 consecutive Sundays.
- **Fast-exit overrides** (usable at any 9:45/3:30 window, no Sunday needed): (a) SPY closes >2% below 200-day MA when portfolio is Aggressive; (b) VIX/VIX3M closes >1.0; (c) HY OAS +100bp in 2 weeks. Any one → cut equity to the next tier down at the next decision window. **Re-risking always waits for Sunday** — this exit-fast/enter-slow asymmetry is the cheapest known whipsaw reducer.
- **Zweig thrust exception:** a confirmed breadth thrust within the past 10 sessions permits jumping directly to Neutral from any tier.

---

## Regime→strategy mapping

| Regime | Selection style | Evidence | Notes |
|---|---|---|---|
| Aggressive | 3–12 mo relative-strength momentum among sector ETFs / large caps; hold winners, monthly refresh | Momentum premium: Grade A historically, B post-2010 (crowding, crashes) | Momentum's known failure: sharp rebounds after crashes ("momentum crashes," Daniel-Moskowitz) — do not run momentum selection in the first 4–8 weeks after a bear-market bottom signal; use SPY/RSP instead |
| Neutral | Core index + short-term mean reversion (buy 3–5 day pullbacks to support in uptrending names; RSI(2)-style logic) | Short-horizon reversal: Grade B, robust but small per-trade edge | This is the regime where breakout-buying bleeds; twice-daily windows are adequate for multi-day mean reversion, not intraday |
| Defensive | Quality/defensive tilt only (XLP, XLV, XLU, GLD); no single stocks | Defensive-sector bear outperformance: Grade B (2000-02, 2008, 2020 partial, 2022: XLU/XLP fell far less than SPY; staples & utilities also rebounded strongly post-COVID crash) | These still *fall* in bears — they lose less. Only cash reliably doesn't |
| Cash-heavy | SGOV/BIL (0–3 mo T-bills). Optional GLD ≤15% | T-bills: riskless by construction (Grade A). Gold as crisis hedge: Grade B — rose ~21% during the 2007–09 equity halving, rises in ~2/3 of geopolitical shocks, but was flat in 2022 and can chop for years | **Avoid TLT/long duration as the "defensive" asset**: 2022 killed the stocks-down-bonds-up assumption (TLT −31%). Short duration carries the yield without the rate risk |

**Key honesty note on switching strategies:** post-publication decay is severe in exactly this genre. Antonacci's dual-momentum GEM: **17.4%/yr (1974–2013 backtest) → 5.9%/yr with a 33.7% max drawdown out-of-sample (2014–2021)** — worse drawdown than the backtest ever showed, while SPY compounded ~15%. The pre-FOMC drift "disappeared after 2015." Expect any regime rule here to deliver perhaps half its backtested edge; the drawdown-protection function decays far less than the return-enhancement function, so **use regimes to size risk, not to chase return**.

---

## Sector rotation evidence

**Business-cycle playbook (Fidelity framework, 1962–2021 data):**
- *Early cycle* (recession exit, steepening curve, easing Fed): consumer discretionary (beat the market in **every** early cycle since 1962), financials, industrials, materials, real estate.
- *Mid cycle* (longest phase, ~3 yrs): weakest differentiation — no sector wins >50% of the time; tech/communication modest leaders. Fidelity itself says reduce sector bets here.
- *Late cycle* (inflation/rates rising): energy, materials, healthcare, staples, utilities.
- *Recession*: staples, utilities, healthcare outperform (still usually negative absolute).

**Does it actually work? Grade C as a return strategy.** Molchanov & Stangl ("The Myth of Business Cycle Sector Rotation," IJFE 2024; 10 NBER cycles, 1948–2018) tested exactly this playbook and found **no systematic sector outperformance where the playbook predicts it** — significance levels barely different from random, and any edge dies after transaction costs plus realistic cycle-dating error (you only know the cycle phase with a lag). The Fidelity "+3.6%/yr" figure assumes perfect phase identification. **Verdict for the agent:** use the playbook as a *prior* for which defensive/cyclical tilt fits the regime score, never as a standalone alpha source.

**Sector momentum rotation (own top-2/3 sector ETFs by 3–12 mo relative strength, monthly): Grade B-.** Quantpedia and multiple backtests show historical outperformance of a few %/yr with lower drawdowns, consistent with the generic momentum literature; it degrades in sideways markets and at regime turns, and public backtests are survivorship-prone and cost-light. Retail implementations mostly fail to beat SPY after whipsaws — the honest expectation is: modest edge in trending years, underperformance in choppy years, decent drawdown behavior. Reasonable satellite (1–2 positions) in the Aggressive regime only.

**Structural warning:** XLK+XLC+XLY are dominated by a handful of megacaps; "sector" rotation today is substantially a bet on 7 stocks. Prefer RSP or equal-weight sector variants when testing breadth claims.

---

## Seasonality / calendar effects

| Effect | Claim | Evidence grade | Verdict for a $5k agent |
|---|---|---|---|
| **Turn-of-month** | Last ~4 + first ~3 trading days capture most of the monthly equity premium (Lakonishok-Smidt; McConnell-Xu; Unger backtest: positive ~64% of windows) | **B** — most robust calendar anomaly, persists internationally | Worth a mild bias: schedule adds early in that window, avoid scheduled trims during it. Not worth standalone trades |
| **Sell in May / Halloween** | Nov–Apr ≫ May–Oct (Bouman-Jacobsen 2002: 36/37 countries; Zhang-Jacobsen 2021: persists across 109 markets, 323 yrs) | **B-** — statistically real, but implementable strategies "do not generate abnormal profits" in several tests; being out May–Oct forfeits positive average returns | Do NOT exit on the calendar. Acceptable as a tiebreaker: demand one extra score point before upgrading regime tier during May–Oct |
| **September weakness** | Worst average month since 1950 | **C+** — real in averages, useless per-instance (huge variance) | Context only |
| **Santa rally (last 5 + first 2 days)** | Positive on average globally (FPA study) | **C** — 2000–2021 US subsample shows no effect | Ignore |
| **Pre-FOMC drift** | +49bp avg in 24h before FOMC (Lucca-Moench 2015, Fed staff) | **C today** — "essentially disappeared after 2015" (Finance Research Letters 2020); some post-2020 revival claims (QuantSeeker) | Don't trade it. Do avoid *initiating de-risking* in the hours before FOMC (vol, gaps) |
| **FOMC cycle even weeks** | Equity premium earned in weeks 0, 2, 4 of the FOMC cycle (Cieslak-Morse-Vissing-Jorgensen 2019, since 1994) | **B academically**, hard to exploit at 2 decisions/day | Awareness only: schedule risk-adds early in even weeks if otherwise indifferent |
| **Presidential year 3** | Strongest cycle year (~+13–15% avg, 1948–2020) | **C** — pattern weakened recently | Context in Sunday thesis only. 2026 = midterm year (year 2, historically weakest + biggest intra-year drawdowns) — worth noting in the thesis, not the score |

**General rule: no calendar effect should ever move the regime score. Calendar = scheduling and tiebreakers only.** These are the anomalies with the worst data-snooping problem in finance.

---

## Failure modes

1. **Whipsaw bleed (the #1 cost).** The 200-day rule underperformed in 6 of 8 post-2009 years; every crossing in a bull market costs ~1–3%. Mitigations built into the checklist: weekly (not intraday) evaluation, ±1% hysteresis band, one-tier-per-week re-risking, multi-indicator score instead of single MA.
2. **V-recoveries.** March 2020: trend rules exited near the low and re-entered months higher. The Zweig-thrust exception and "VIX>30 is not a sell signal" rule exist precisely for this. Never *initiate* de-risking after the market is already down >15% and VIX>35 — at that point the expected value of selling is poor.
3. **Grinding bears evade vol signals.** 2022: VIX term structure stayed in contango all year; only the trend and credit legs caught it. This is why the score requires multiple families of indicators (trend, breadth, vol, credit).
4. **Macro indicator false positives.** 2s10s inversion (26 months, no recession) and Sahm rule (July 2024, disavowed) both misfired post-COVID. Price-based indicators outrank macro indicators; macro is narrative context only.
5. **Post-publication decay.** GEM: 17.4% → 5.9% with deeper drawdowns out-of-sample. Pre-FOMC drift: gone after 2015. Assume half the backtested edge, and prefer rules whose value is *risk reduction* (decays slowly) over *return enhancement* (decays fast).
6. **Breadth distortion by megacap concentration.** SPY above its 200-day while RSP and 8 sectors are below = narrow market; the checklist's RSP and sector-count legs are the defense.
7. **Sector-rotation costs and cycle-dating lag.** Molchanov-Stangl: the edge disappears with realistic phase-timing error. The agent cannot date the cycle in real time; nobody can.
8. **Regime-flip thrash.** A weekly score that oscillates 4↔5 will churn the account. The 2-Sunday confirmation and one-tier-per-week rules cap turnover at a tolerable level.
9. **Defensive assets are not cash.** XLP/XLU fell ~double digits in 2022 and ~-25% in March 2020; TLT fell 31% in 2022; gold was flat in 2022. For this account, **SGOV/BIL is the only true risk-off asset**; everything else is a *lower-beta bet*, sized accordingly.
10. **LLM-specific: narrative override.** The greatest risk is the agent talking itself out of the mechanical score because the news narrative is compelling. The score is computed first, mechanically; the Sunday thesis may adjust the *selection within* a tier, never the tier itself except via the written override rules above.

**Data sources the agent can automate:** Alpaca daily bars (SPY, RSP, 11 XL* sectors, GLD, SGOV/BIL — all MAs computable locally); FRED API free (`BAMLH0A0HYM2` HY OAS, `T10Y2Y`, `VIXCLS`, `SAHMREALTIME`); VIX3M from CBOE/free quote feeds; $S5TH-style breadth via StockCharts if scrapeable, else the 11-sector proxy.

---

## Sources

**Trend-following / Faber:** [Faber, A Quantitative Approach to TAA (SSRN)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=962461) · [2013 update (PDF)](https://allocatortraining.com/wp-content/uploads/2023/06/A-Quantitative-Approach-to-Tactical-Asset-Allocation.pdf) · [Meb Faber timing model](https://mebfaber.com/timing-model/) · [Quantpedia: Asset Class Trend-Following](https://quantpedia.com/strategies/asset-class-trend-following) · [AQR: A Century of Evidence on Trend-Following](https://www.aqr.com/Insights/Research/Journal-Article/A-Century-of-Evidence-on-Trend-Following-Investing) · [Alpha Architect: TSMOM refresh](https://alphaarchitect.com/time-series-momentum-aka-trend-following-the-historical-evidence/) · [QuantifiedStrategies: 200-day MA backtest](https://www.quantifiedstrategies.com/200-day-moving-average-trading-strategy/) · [Alvarez: reducing 200-day whipsaws](https://alvarezquanttrading.com/blog/reducing-whipsaws-when-using-200-day-moving-average-for-market-timing/) · [7 Circles: Faber TAA review](https://the7circles.uk/tactical-asset-allocation-meb-faber/)

**Volatility:** [eco3min: VIX term structure regimes](https://eco3min.fr/en/vix-backwardation-contango-volatility-term-structure/) · [Macroption: VIX futures curve](https://www.macroption.com/vix-futures-curve/) · [Harbourfront: VIX term-structure trading](https://harbourfrontquant.substack.com/p/using-vix-futures-term-structure) · [Elm Wealth: When Fear Spikes](https://elmwealth.com/vix-buy-signal/) · [Moreira & Muir (NBER w22208)](https://www.nber.org/papers/w22208) · [Cederburg et al. (JFE 2020)](https://www.sciencedirect.com/science/article/abs/pii/S0304405X2030132X)

**Breadth:** [StockCharts: % above 200-day](https://articles.stockcharts.com/article/arthurhill-2025-08-stocks-above-200-day-expands-tech-consolidates-big-banks-lead/) · [Schwab: breadth check](https://www.schwab.com/learn/story/breadth-check-strength-and-weakness-trend-tracker) · [StockCharts: Zweig Breadth Thrust](https://articles.stockcharts.com/article/zweig-breadth-thrust-sets-up-how-to-identify-a-stampede-in-upside-participation/) · [OptionsTradingIQ: ZBT history](https://optionstradingiq.com/zweig-breadth-thrust-signal/)

**Credit / macro:** [Convex: HY OAS thresholds](https://convextrade.com/glossary/high-yield-spread-oas) · [FRED BAMLH0A0HYM2](https://www.tradingview.com/symbols/FRED-BAMLH0A0HYM2/ideas/) · [eco3min: Sahm rule false signals](https://eco3min.fr/en/sahm-rule-false-signals-history/) · [CNBC: yield curve failure 2024](https://www.cnbc.com/2024/07/24/why-an-indicator-that-has-foretold-almost-every-recession-doesnt-seem-to-be-working-anymore.html) · [Britannica Money: Sahm rule](https://www.britannica.com/money/sahm-rule-recession-indicator)

**Regime-conditional:** [Regime-switching momentum & mean reversion (ScienceDirect 2023)](https://www.sciencedirect.com/science/article/pii/S0264999323000494) · [Slow Momentum with Fast Reversion (arXiv)](https://arxiv.org/pdf/2105.13727) · [Quantt: mean reversion guide](https://www.quantt.co.uk/resources/mean-reversion-trading-guide) · [Robot Wealth: Dual Momentum review](https://robotwealth.com/dual-momentum-review/) · [GEM pre/post-publication](https://www.linkedin.com/pulse/dual-momentum-pre-post-publication-performance-abdennour-aissaoui) · [Antonacci: extended GEM backtest](https://medium.com/@garyantonacci_30463/extended-backtest-of-global-equities-momentum-dual-momentum-eb12902612e0)

**Sector rotation:** [Fidelity: Business Cycle Approach (PDF)](https://www.fidelity.com/webcontent/ap101883-markets_sectors-content/20.07.0/business_cycle/Business_Cycle_Sector_Approach_2020.pdf) · [Fidelity Viewpoints](https://www.fidelity.com/viewpoints/investing-ideas/sector-investing-business-cycle) · [Molchanov & Stangl: The Myth of Business Cycle Sector Rotation (IJFE 2024)](https://onlinelibrary.wiley.com/doi/10.1002/ijfe.2882) · [Quantpedia: Sector Momentum](https://quantpedia.com/strategies/sector-momentum-rotational-system) · [Quantpedia: Improve ETF Sector Momentum](https://quantpedia.com/how-to-improve-etf-sector-momentum/) · [QuantifiedStrategies: ETF rotation](https://www.quantifiedstrategies.com/etf-rotation-strategy/)

**Risk-off assets:** [VanEck: gold in crises](https://www.vaneck.com/us/en/blogs/gold-investing/gold-in-a-storm-how-gold-holds-up-during-market-crises/) · [Man Group: Gold — Bugs, Bears and Myths](https://www.man.com/insights/gold-bugs-bears-myths) · [Kavout: defensive sectors](https://www.kavout.com/market-lens/defensive-sectors-how-to-protect-your-portfolio-in-volatile-markets) · [StockCharts: defensive sectors signal](https://articles.stockcharts.com/article/utilities-staples-health-care-are-defensive-sectors-signaling-market-trouble/) · [SentimenTrader: XLY/XLP not robust](https://sentimentrader.com/blog/consumer-discretionary-vs-consumer-staples-relative-ratio)

**Calendar effects:** [Lucca & Moench (NY Fed)](https://www.bostonfed.org/-/media/Documents/conference/PDF/Lucca_preFOMCDrift.pdf) · [Disappearing pre-FOMC drift (FRL 2020)](https://www.sciencedirect.com/science/article/pii/S1544612320315956) · [QuantSeeker: pre-FOMC drift](https://www.quantseeker.com/p/trading-the-fed-the-pre-fomc-drift) · [Bouman & Jacobsen (SSRN)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=76248) · [Zhang & Jacobsen (JIMF 2021)](https://www.sciencedirect.com/science/article/abs/pii/S0261560620302242) · [Unger: turn-of-month](https://ungeracademy.com/blog/turn-of-the-month-rally) · [FPA: Santa rally evidence](https://www.financialplanningassociation.org/article/journal/MAR15-yes-virginia-there-santa-claus-rally-statistical-evidence-supports-higher-returns-globally) · [Beyer et al.: Presidential cycle (PDF)](https://www.uwosh.edu/faculty_staff/beyers/workingpapers/Presidential%20Cycle%20JPM%20forthcoming.pdf) · [QuantifiedStrategies: election cycles](https://www.quantifiedstrategies.com/president-election-cycles/)
