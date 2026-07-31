# Momentum and Trend-Following Knowledge Base
## For a long-only, $5k, twice-daily-decision swing/position agent (Alpaca paper)

**Constraint mapping up front.** Everything below is filtered through: long-only US stocks/ETFs, fractional shares, decisions only at 9:45 AM and 3:30 PM ET, weekly Sunday thesis session, max 25% equity/position (= max ~$1,250 initial per position, so a minimum of 4 positions at full deployment), max 8 orders/session. The good news: **momentum is the academic anomaly best suited to this cadence.** Canonical implementations rebalance *monthly*; even fast practitioner variants rebalance weekly. Nothing in the core academic literature requires intraday monitoring. The long-only constraint actually *helps*: the 2009-style momentum crash was overwhelmingly a **short-leg (loser stocks rallying) phenomenon**, and Quantpedia's replications show the long leg of momentum beat the benchmark across ranking periods even when long-short momentum disappointed.

---

## 1. Cross-Sectional (Relative) Momentum — Jegadeesh & Titman lineage

**Evidence grade: A** (peer-reviewed, replicated globally for 30+ years, out-of-sample confirmed)

### Core findings
- Jegadeesh & Titman (1993, *Journal of Finance*): buying past 3–12-month winners and selling past losers earns ~1% per month over 3–12-month holding periods; not explained by systematic risk. The 6-month formation / 6-month holding version earned ~12.01%/yr in their sample.
- Jegadeesh & Titman (2001): the effect **persisted in the 1990s, out of sample** — not data snooping. Key caveat: profits partially reverse **4–5 years** after formation (supports behavioral overreaction stories; irrelevant at your holding horizon, but a reason not to hold winners beyond ~12 months on stale signals).
- Robust internationally; Alpha Architect calls it "the most pervasive contradiction of the EMH."

### The 12-1 convention and the short-term reversal exclusion
- Standard academic momentum signal = **total return from month t-12 to t-1, skipping the most recent month** ("12-1" or "12_2"). The skip exists because Jegadeesh (1990) documented **1-month reversal**: last month's winners tend to *underperform* next month (~2%/month reversal effect in 1934–1987 data). Including month t-1 in your ranking contaminates the momentum signal with reversal. **Rule for the agent: never rank stocks by 1-month return and buy the top; if anything, a big 1-week/1-month pop is a mild argument to wait for a pullback.**
- Novy-Marx (2012, *JFE*): momentum is driven mainly by months **t-12 to t-7** ("intermediate momentum"), especially in large liquid stocks. Goyal & Wahal ("Is Momentum an Echo?") disputed this internationally — no robust echo in 37 non-US markets. Practical takeaway: don't over-engineer; 12-1 is the consensus default, and blending 6-month and 12-month lookbacks (both skipping the last month) reduces specification risk (grade A for 12-1; grade B for the intermediate-horizon refinement).

### Quality-of-momentum refinement ("frog in the pan")
Da, Gurun & Warachka (2014) + Gray & Vogel's *Quantitative Momentum* (Wiley, 2016): among high-momentum stocks, those with **smooth, continuous paths** (high % of positive days, low gappiness) outperform stocks whose gains came in one discrete jump. Tie-breaker rule: given two candidates with similar 12-1 return, prefer the one with the higher fraction of up days / smaller max single-day contribution. **Grade: B+** (peer-reviewed origin, practitioner-replicated, but weaker than the core effect).

### Concrete strategy — "Long-only 12-1 momentum sleeve" (adapted to constraints)
- **Universe:** liquid US stocks, e.g., S&P 500 or Russell 1000 members, price > $5, avg dollar volume > $10M (fractionals make price irrelevant to sizing).
- **Signal (compute Sunday):** total return t-12→t-1 months (skip last ~21 trading days). Rank universe.
- **ENTRY (IF/THEN):** IF stock is in top decile (or top 10–20 names) by 12-1 return AND above its own 200-day SMA AND market filter passes (SPY > 200d SMA — see §3), THEN buy at Monday 9:45 session. Equal-weight 4–6 positions at 15–25% each.
- **EXIT:** IF stock drops out of the top quartile at a scheduled re-rank, THEN sell at next 9:45 session. Re-rank **monthly** (canonical) or every 2 weeks (faster, more turnover). Also exit on market-filter failure (below).
- **Holding period:** typically 1–4 months per name; academic evidence supports 3–12-month holds.
- **Crash overlay (Han, Zhou & Zhu 2014, "Taming Momentum Crashes," SSRN 2407199):** a simple **10% stop from the price at the start of each month**, checked at your two daily sessions, raised momentum's monthly return from 1.01% to 1.73% in 1926–2011 data and cut worst monthly losses from ~-50% to ~-11% (equal-weighted). Their test used daily closes — **checking at 9:45 and 3:30 is a faithful approximation; this does NOT require intraday monitoring.** CXO Advisory notes the caveat that pre-1940s data drives some of the effect and gap-throughs weaken real fills; still grade B+ as an overlay.
- **Expected characteristics:** long-only winners portfolio historically ~2–5%/yr over benchmark before costs (Quantpedia replication: long leg consistently beat benchmark); win rate per position roughly 50–60%; **drawdowns similar to or worse than market in crashes** (long-only momentum is high-beta in bulls, and momentum crashes hit after bear-market rebounds). Turnover high — expect to replace 20–40% of names monthly. At Alpaca zero commission, cost is spread + slippage only; with 4–6 liquid large caps that's a few bps — Frazzini/Israel/Moskowitz show momentum survives real-world costs even at institutional scale.
- **Crash risk (Daniel & Moskowitz 2016, *JFE*):** long-short momentum lost **-45.6% in March–April 2009** and ~-80% peak drawdown in 2009 replications; crashes occur in "panic states" — after market declines, with high volatility, during sharp rebounds — and are driven by the *short* leg (junk rallying). **Your long-only version dodges the worst of this but will lag badly in V-shaped recoveries** because it holds defensive-tilted "winners" coming out of a bear. Barroso & Santa-Clara (2015): momentum's own realized volatility predicts crashes; scaling exposure down when trailing 6-month daily vol of the strategy is high "virtually eliminates crashes" and ~doubles Sharpe (grade A-). Cheap implementation: IF VIX > ~30 or SPY below 200d SMA, THEN halve momentum-sleeve exposure or require stricter entry criteria.

---

## 2. Time-Series / Absolute Momentum & Dual Momentum (Antonacci)

**Evidence grade: A for the underlying TS-momentum effect; B+ for GEM as a specific recipe** (post-publication live period underperformed buy-and-hold, as designed)

### Core findings
- Moskowitz, Ooi & Pedersen (2012, *JFE*, "Time Series Momentum"): across 58 futures/forwards (equities, bonds, FX, commodities), the **sign of the past 12-month excess return positively predicts the next 1–12 months**. This is the academic backbone of trend-following.
- AQR "A Century of Evidence on Trend-Following" (Hurst, Ooi, Pedersen): simulated back to 1880, consistent across every major regime including the Great Depression and GFC. Caveat: the 2010s were historically weak for trend (AQR attributes this to an exceptional macro regime; Lempérière et al. "Two Centuries of Trend Following" note 10-year trend performance has never gone negative in 200 years, but the 2011+ stretch was near flat).
- Antonacci, "Absolute Momentum: A Simple Rule-Based Strategy and Universal Trend-Following Overlay" (SSRN 2244633): 12-month excess-return-over-T-bills sign as a universal risk switch; and *Dual Momentum* (book, 2014) — combine relative momentum (which asset is strongest) with absolute momentum (is it beating T-bills at all).

### Concrete strategy — GEM (Global Equities Momentum), the canonical $5k-viable version
- **Assets:** SPY (or VOO), VEU/VXUS (ex-US equities), BND/AGG (aggregate bonds); cash proxy BIL.
- **Rules (check once a month, e.g., first Sunday; execute Monday 9:45):**
  - IF 12-month total return of SPY > 12-month return of T-bills (BIL): risk-on. THEN hold whichever of SPY vs VEU has the higher 12-month return.
  - ELSE (SPY 12-mo return < T-bill return): THEN hold BND.
- **Holding:** until next monthly check. ~1.5 trades/year historically — trivially within 8 orders/session.
- **Documented characteristics:** Antonacci's backtest (1971–2013): ~17.4%/yr vs ~10.5% for the S&P with max drawdown roughly halved (~-23% vs -51%); extended backtest to 1950 and the 1973–74 out-of-sample check (+20% while S&P fell >40%) support robustness. **Honest post-publication record: 2014–2022 GEM did ~5.9%/yr with a -33.7% max drawdown and underperformed S&P buy-and-hold** — a whipsaw-prone period for monthly signals (notably the Dec-2018 and Mar–Apr 2020 round trips). Defenders (Antonacci, Corey Hoffstein's rebuttal exchange) argue this is expected behavior in a relentless US bull; critics (Newfound "Fragility Case Study: Dual Momentum GEM"; ReSolve "Global Equity Momentum: A Craftsman's Perspective") show results are **highly sensitive to the single 12-month lookback and single rebalance date** — a 10- vs 12-month lookback or a mid-month vs month-end rebalance changed multi-year outcomes by hundreds of bps ("timing luck").
- **Robustness fixes (grade B, from Newfound/ReSolve):** average signals across multiple lookbacks (6–12 months) rather than one; and/or tranche — split the sleeve into 2–4 sub-sleeves rebalanced on staggered weeks. Your twice-daily cadence makes weekly-staggered tranches trivial.
- **Fit note:** because your account is long-only anyway, absolute momentum is the *single most important* concept in this document: it's the difference between riding 2022 down in full equity exposure vs sitting in bonds/cash.

### Time-series momentum applied per-position (overlay)
- **Rule:** IF any held asset's 12-month excess return turns negative at a weekly check, THEN rotate that sleeve to cash/BIL/short-duration bonds. Grade A- for the concept; expect ~1–2 whipsaws per multi-year cycle costing a few % each, paid for by large bear-market savings.

---

## 3. Moving-Average Trend Filters (200-day rule, 10-month SMA, golden cross)

**Evidence grade: B+ as a *risk-management* device; C as a *return-enhancement* device.** This distinction is the single most misunderstood point in retail trend-following.

### What the data actually shows
- **Faber (2007, "A Quantitative Approach to Tactical Asset Allocation," SSRN 962461)** — the most-downloaded SSRN paper in the space: hold asset when price > 10-month SMA (≈200-day), else cash. On the S&P 1900–2005: **equity-like returns with materially lower volatility and max drawdown** (invested ~70% of the time); 2006–2012 out-of-sample: max drawdown -9.5% vs -46% buy-and-hold. Works as a drawdown truncator across 20+ tested markets.
- **Zakamulin ("The Real-Life Performance of Market Timing with Moving Average and Time-Series Momentum Rules," *J. Asset Mgmt* 2014; also "Fooled by Data-Mining")** — the essential cold shower: out-of-sample, with realistic frictions, **no statistically significant outperformance vs buy-and-hold in the second half of the sample**; published backtests carry heavy data-mining bias. MA timing mainly delivers a **better risk profile, not higher returns**, and its whole historical edge comes from a handful of big bear markets (1929–32, 1973–74, 2000–02, 2008). Between crises it bleeds small whipsaw losses.
- **Golden cross (50d SMA crossing above 200d SMA):** QuantifiedStrategies and similar backtests on SPY since 1993: ~+645% vs ~+567% buy-and-hold, ~+20% avg gain per signal, essentially all outperformance from sidestepping 2000–02 and 2008; frequent whipsaws in sideways tape. Same character as the 200-day rule but slower/laggier. Grade B for risk reduction; no strong evidence it beats the simpler price-vs-200d/10-month rule.
- **Consensus synthesis (Faber + Zakamulin + AQR):** use MA filters to decide *whether* to be exposed, not to generate alpha. Expected: ~55–70% of filter round-trips are small whipsaw losses; the rare wins are enormous (missing a -40% bear).

### Concrete rules
- **Portfolio regime filter (recommended, always on):** IF SPY monthly close (or Friday close, checked Sunday) < 10-month SMA (or price < 200d SMA at Sunday check), THEN cut equity momentum exposure to 0–50% and park in BIL/SHV/short-duration bond ETF; re-enter when it recloses above. Check **weekly at most** — daily checking of a 200d filter multiplies whipsaws for no documented benefit.
- **Per-position filter:** IF a held stock closes below its 200d SMA at the 3:30 session, THEN flag; if still below at the next Sunday review, exit at Monday 9:45. (The confirmation delay is a whipsaw damper; grade C for the exact delay length — reasonable but not academically pinned down.)

---

## 4. 52-Week-High Momentum & Relative Strength

**Evidence grade: A for the cross-sectional 52-week-high effect; B for breakout-timing uses of it**

- **George & Hwang (2004, *Journal of Finance*):** ranking stocks by **nearness of current price to the 52-week high** (price ÷ 52-wk high) predicts returns *better than* past-return momentum, and the profits **don't reverse long-term** (unlike J&T momentum's 4–5-year reversal). Behavioral driver: anchoring — traders are slow to bid stocks through a salient reference price, so good news near the high gets underreacted to. Replicated internationally (profitable in 18 of 20 markets; significant in 10 — grade A with the caveat that significance is spottier abroad).
- Interaction with crashes: research (e.g., Marquette study "Momentum Crashes and the 52-Week High") finds 52-week-high momentum has **its own crash episodes** in the same panic-rebound states; it is not a free lunch vs 12-1 momentum, but blends well with it.
- **Relative strength (practitioner form, e.g., IBD RS ratings, Levy 1967 lineage):** percentile-rank each stock's 6–12-month return vs universe; buy only high-RS names. This is just cross-sectional momentum re-labeled; the IBD "RS ≥ 80–90" heuristic maps to top quintile/decile 12-month momentum. Grade A for the underlying ranking, C for any specific proprietary rating cutoff.

### Concrete strategy — "Near-high momentum screen" (blends §1 and §4)
- **Signal (Sunday):** price ÷ 52-week high ≥ 0.90 (within 10% of high) AND 12-1 momentum in top quintile AND above 200d SMA.
- **ENTRY:** IF a watchlist name closes (3:30 check) at a **new 20-day high** or new 52-week high, THEN buy next session (9:45), 15–25% position. Buying the close-confirmed breakout at the next open sacrifices a little vs intraday buying but requires no monitoring — this is the correct adaptation, and George & Hwang's effect is measured monthly anyway, so precision timing is not where the edge lives.
- **EXIT:** trailing rule — IF price falls >15–20% from its post-entry high (checked at the two sessions), or drops below the 50d SMA for 5+ consecutive sessions, or falls out of the top-half momentum rank at re-rank, THEN sell.
- **Holding period:** weeks to months.
- **Characteristics:** individual-trade win rate ~40–55%; payoff skew positive (winners run, losers cut); expect worse-than-market drawdowns if the regime filter is off. No published win-rate stats exist for this exact retail bundle (that composite is grade C), but each component is A/B.

---

## 5. ETF Momentum / Rotation at $5,000

**Evidence grade: B+ overall** — mostly practitioner/Quantpedia-verified backtests built on A-grade underlying effects. This family is the **best structural fit for your constraints**: 1–5 orders/month, fractional shares make any ETF price workable, diversification comes free inside each ETF, and 25%-per-position caps map naturally onto top-3/top-4 rotation.

### 5a. Sector rotation (Faber-style / Quantpedia "Sector Momentum — Rotational System")
- **Universe:** the 11 SPDR sector ETFs (XLK, XLF, XLV, XLE, XLI, XLY, XLP, XLU, XLB, XLRE, XLC).
- **Rules:** monthly (Sunday calc, Monday 9:45 execution): rank by 12-month (or blended 3/6/12-month) total return. Buy top 3 equal-weight (~33% each exceeds your 25% cap — use **top 4 at 25%** instead). IF a held sector drops out of the top 4 (with a 1–2 rank buffer to cut churn), THEN rotate. Absolute-momentum overlay: IF a top-ranked sector's 12-month return < T-bill return, THEN hold BIL in that slot instead.
- **Evidence:** momentum in industries/sectors documented back to the 1920s (Moskowitz & Grinblatt 1999 for industry momentum — grade A for the effect); Faber's sector-rotation extension and StockCharts/Quantpedia replications show buy-and-hold outperformance in ~70% of years, but with tracking-error-heavy stretches. Quantpedia's refinements pieces show results are sensitive to lookback choice — blend lookbacks.
- **Turnover/cost:** ~1–3 ETF swaps per month; negligible at Alpaca.

### 5b. Dual-momentum GEM (§2) — 3 ETFs, ~1.5 trades/year. The lowest-effort, best-documented option.

### 5c. Faber GTAA / Ivy 5 (multi-asset)
- **Universe:** SPY/VTI, VEU, BND/IEF, DBC (commodities), VNQ (REITs), 20% each.
- **Rule:** monthly, IF asset > 10-month SMA THEN hold, ELSE that 20% goes to cash/BIL.
- **Evidence:** Faber 2007/2013 updates — 1973–2012: ~10.5%/yr, vol ~7%, max DD ~-9.5% (timing version) vs buy-and-hold's -46%; grade B+ (author-replicated across decades, widely reproduced, but post-2013 live results are more modest — commodities/REIT legs dragged in the 2010s). Note your 25% cap is satisfied by design.

### 5d. What NOT to do at $5k
- Leveraged-ETF rotation (TQQQ strategies): volatility decay + regime sensitivity + no peer-reviewed support at daily-decision granularity; popular blog backtests are heavily overfit to the post-2009 bull. Grade C, and the drawdown profile (-80%+ plausible) is inappropriate. Skip.
- Anything requiring >8 orders/session or intraday rotation triggers: not applicable; nothing in this family needs it.

---

## 6. Practitioner Entry/Exit Rules — breakouts, pullbacks, trailing exits (honest evidence audit)

This is where evidence quality craters relative to §§1–5. Grade each rule before trusting it.

### Breakout entries (O'Neil/CANSLIM, Minervini VCP, Darvas lineage)
- **The rules:** buy when price clears a multi-week consolidation ("base"/pivot) on volume 40–50% above average; stop 3–8% below entry; sell partial into 20–25% gains; O'Neil's "cut all losses at 7–8%."
- **Evidence quality: B- to C.** Minervini's US Investing Championship wins are audited (real track record → B for "the man can trade"), but headline claims like "220% average annual returns" and stats like "90.77% of successful VCP breakouts occur when indices are above the 10-month EMA" are self-reported/marketing-grade — **C, unverified**. No peer-reviewed validation of VCP or CANSLIM as mechanical systems exists; independent mechanical CANSLIM backtests (AAII's screen) showed strong but volatile results with severe drawdowns. What IS academically supported in this bundle: the 52-week-high proximity effect (§4), the market filter ("M" in CANSLIM ≈ 200d rule, §3), and high relative strength (§1). The chart-pattern component is the unverified part.
- **Executability:** **as taught, NOT executable** — O'Neil/Minervini buy intraday as price crosses the pivot and manage stops in real time. **Adaptation that is executable:** require a *close* above the pivot at the 3:30 check, enter at next 9:45 open, initial stop 8% below entry checked twice daily (accept gap risk through stops — with 15–25% positions, an overnight -20% single-stock gap costs the portfolio ~-4%; survivable but real). This adaptation loses some edge (breakout day often runs) and no one has published clean stats on the delayed version — treat as C+.

### Pullback entries in established trends
- **The rule:** IF stock is in top-decile momentum AND above rising 50d/200d SMA, AND has pulled back 3–8% to the 20d/50d MA without breaking it, THEN buy at next session; stop below the pullback low.
- **Evidence:** consistent with short-term reversal working *for* you (you're buying weakness in strength — §1's Jegadeesh 1990 reversal now aids entry rather than hurting ranking). Quantified backtests (QuantifiedStrategies.com and similar) show pullback entries in uptrends have higher per-trade win rates (~55–65%) but smaller average wins than breakouts; no peer-reviewed treatment of the exact rule. **Grade B-** — mechanically sensible, directionally supported by the reversal literature, unverified in journal form. Fully executable at your cadence.

### Trailing exits
- **Ranked by evidence:**
  1. **Monthly re-rank exit** (drop out of top quartile → sell): grade A — this *is* the academic exit.
  2. **10% fixed stop from month-start price** (Han/Zhou/Zhu): grade B+ (see §1); checkable at your two sessions.
  3. **Exit on close below 200d/10-mo MA:** grade B+ as regime exit (§3).
  4. **ATR-based trailing stops (e.g., 3×ATR(20) chandelier), 25% trailing stops:** grade C+ — ubiquitous practitioner lore; the few systematic studies (Dai et al. 2021 *Int'l Review of Finance*; quant-investing.com's tests) find trailing stops **reduce drawdown and volatility, with mixed-to-slightly-negative effect on raw return** vs re-rank exits. Use for risk control, not return enhancement.
- **Anti-rule with strong evidence:** do NOT take quick profits on momentum names ("sell at +10%") — that amputates the right tail that funds the whole strategy. The academic profit distribution depends on holding winners 3–12 months.

### Explicitly NOT executable under constraints (flagged)
- Intraday breakout entries at pivot-cross with real-time volume confirmation (O'Neil/Minervini as written).
- Intraday stop-loss management / same-bar stop-and-reverse.
- Qullamaggie-style episodic-pivot day-1 gap buying (requires 9:30–9:45+ tape reading; your 9:45 window *might* catch opening-range-breakout closes, but the strategy's documented edge is in the first minutes — treat as not executable).
- Any 1-month-formation/1-week-holding fast momentum with daily rotation — turnover fine cost-wise, but the short-term reversal effect actively fights it; also weak after costs (Frazzini et al.: short-horizon strategies are the most cost-constrained).

---

## Common Failure Modes (all families)

1. **Momentum crashes / rebound risk.** Long-short CS momentum: -45.6% in Mar–Apr 2009 (Daniel & Moskowitz), ~-80% strategy drawdowns in replications; crashes cluster in panic states — post-decline, high-vol, sharp rebound. Long-only version's failure mode is different but real: **massive relative underperformance during V-recoveries** (your "winners" are defensives; the junk you don't own doubles). Mitigants with A/B evidence: volatility scaling (Barroso & Santa-Clara), stop-loss overlay (Han et al.), and simply being long-only.
2. **Whipsaw bleed in trend filters.** The 200d/10-mo rule loses small amounts repeatedly in sideways markets (2011, 2015–16, 2018, 2023 head-fakes) and pays off only in rare big bears. Zakamulin: no significant out-of-sample outperformance — the honest expectation is **insurance, not alpha**. If the agent evaluates the filter over any 1–3-year window it will usually look like a mistake; that's by design.
3. **Specification fragility / timing luck.** GEM's post-2014 disappointment is partly the *specific* 12-month, month-end spec (Newfound, ReSolve). One-parameter strategies are lottery tickets on that parameter. Mitigate: blend lookbacks (6–12m), tranche rebalances across weeks.
4. **Short-term reversal contamination.** Ranking on 1-month returns, or chasing last week's spike, systematically buys the reversal. Always skip the most recent month in formation; prefer pullback or consolidation-close entries after big pops.
5. **Crowding and factor decay.** Post-publication factor decay (McLean & Pontiff) applies: momentum's paper edge has compressed. Crowding research (Lou/Polk "Crowding and Tail Risk in Momentum Returns") links crowded momentum to worse tails. The 2010s were historically weak for trend-following (AQR attributes to macro regime). Expect maybe half the backtest edge going forward.
6. **Turnover cost at retail scale — mostly a non-issue, with one exception.** Zero commission + fractional + liquid large caps/ETFs ⇒ spread/slippage of a few bps/trade; momentum survives costs at *institutional* scale, so a $5k account trading SPY-tier liquidity is fine. Exception: small caps and <$1M-ADV names — spreads of 20–100bps make fast rotation expensive; also 9:45 AM entry avoids the worst opening-auction spreads (deliberately good design), but **avoid 3:30 entries in illiquid names** near close.
7. **Taxes/frictions on churn** — paper account now, but monthly-turnover strategies are short-term-gains machines; relevant if ever live.
8. **Long-flat opportunity cost.** Absolute-momentum sleeves sat in bonds during chunks of 2015–2016 and late 2023 rallies; and in 2022 the bond "safe asset" *also* fell — GEM's -33.7% 2014–2022 max drawdown partly came from rotating into duration during a rate shock. Mitigant: use short-duration (BIL/SHV) not AGG/TLT as the risk-off asset when yields are rising (grade B, post-2022 practitioner consensus).
9. **Sunday-thesis staleness.** Signals computed Sunday can be invalidated by a Monday gap. Mitigant: make Sunday produce *conditional* orders ("buy X at Monday 9:45 unless it gapped >4% above Friday close — then wait for Thursday check or the 3:30 session"), which the two daily sessions can adjudicate.

---

## What Fits the 2-Checks-Per-Day Cadence Best (ranked)

1. **Dual-momentum ETF core (GEM-style, §2) — best fit.** Monthly signal, ~1.5 trades/yr, A-grade underlying evidence, drawdown-truncating, impossible to violate the 8-order cap. Recommend it as the portfolio's 50–75% backbone, upgraded with multi-lookback blending (6/9/12-mo average) and BIL as risk-off asset.
2. **Sector-ETF rotation, top-4 at 25% each, monthly with absolute-momentum overlay (§5a).** 2–4 orders/month, natural fit to position caps, B+ evidence.
3. **Long-only 12-1 stock momentum sleeve, 4–6 names, monthly/biweekly re-rank + 10% monthly stop + 200d market filter (§1).** The highest-evidence stock-picking strategy available to this agent; sessions are used only for scheduled entries/exits and stop checks. Suits a 25–50% satellite.
4. **52-week-high / near-high momentum screen with close-confirmed breakout or pullback entries (§4, §6).** Fits the cadence but is the most execution-sensitive; run small (≤2 positions) until live stats accumulate.
5. **Pure Faber 10-month filter on a single index ETF (§3)** — fits trivially; strictly dominated by #1 which contains it.
6. **NOT fit:** intraday breakout buying as taught by O'Neil/Minervini/Qullamaggie; sub-weekly rotation; 1-month-lookback fast momentum; real-time stop management; leveraged-ETF daily strategies.

**Cadence-specific design notes:** use 9:45 as the *execution* session (post-open liquidity, avoids auction chaos) and 3:30 as the *confirmation/stop-check* session (near-close prices ≈ the daily closes every cited study uses — this makes academic close-based rules faithfully implementable). Sunday computes ranks and writes conditional orders; the 8-order cap comfortably covers a full monthly rotation of a 6-position book split across two sessions.

---

## Sources

**Academic (grade-A anchors)**
- Jegadeesh & Titman (1993): https://www.bauer.uh.edu/rsusmel/phd/jegadeesh-titman93.pdf ; https://onlinelibrary.wiley.com/doi/abs/10.1111/j.1540-6261.1993.tb04702.x
- Jegadeesh & Titman (2001), out-of-sample persistence: https://onlinelibrary.wiley.com/doi/abs/10.1111/0022-1082.00342 ; https://www.nber.org/papers/w7159
- Jegadeesh (1990) short-term reversal context + skip-month convention: https://alphaarchitect.com/quantitative-momentum-research-short-term-return-reversal/ ; https://www.globalequitymomentum.com/articles/lookback-delay
- Daniel & Moskowitz (2016), "Momentum Crashes": https://www.kentdaniel.net/papers/published/jfe_16.pdf ; https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2371227 ; https://www.nber.org/papers/w20439
- Barroso & Santa-Clara (2015), "Momentum Has Its Moments": https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2041429
- Moskowitz, Ooi & Pedersen (2012), "Time Series Momentum": https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2089463 ; https://www.aqr.com/Insights/Research/Journal-Article/Time-Series-Momentum
- George & Hwang (2004), 52-week high: https://onlinelibrary.wiley.com/doi/abs/10.1111/j.1540-6261.2004.00695.x ; international evidence: https://www.sciencedirect.com/science/article/abs/pii/S0261560610001099
- Novy-Marx (2012), intermediate momentum + debate: https://alphaarchitect.com/when-academics-disagree-on-momentum-investing/
- Han, Zhou & Zhu, "Taming Momentum Crashes: A Simple Stop-Loss Strategy": https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2407199 ; skeptical read: https://www.cxoadvisory.com/technical-trading/stop-losses-to-avoid-stock-momentum-crashes/
- Frazzini, Israel & Moskowitz, "Trading Costs of Asset Pricing Anomalies": https://ssrn.com/abstract=2294498 ; https://alphaarchitect.com/surprise-the-size-value-and-momentum-anomalies-survive-after-trading-costs/
- Zakamulin, "Real-Life Performance of Market Timing with MA and TS-Momentum Rules": https://www.ssrn.com/abstract=2242795 ; https://link.springer.com/article/10.1057/jam.2014.25 ; profile: https://alphaarchitect.com/the-moving-average-research-king-valeriy-zakamulin/
- 30-year momentum literature review: https://link.springer.com/article/10.1007/s11408-022-00417-8

**Practitioner / established quant (grade B)**
- Faber, "A Quantitative Approach to Tactical Asset Allocation": https://mebfaber.com/wp-content/uploads/2016/05/SSRN-id962461.pdf ; https://mebfaber.com/timing-model/ ; CXO review: https://www.cxoadvisory.com/technical-trading/long-term-outperformance-from-trends-defined-by-moving-averages/
- Antonacci, "Absolute Momentum" (SSRN 2244633): https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2244633 ; GEM extended backtest: https://dualmomentum.net/2018/10/16/extended-backtest-of-global-equities-momentum/ ; stops discussion: https://dualmomentum.net/2015/06/13/momentum-and-stop-losses/
- GEM fragility debate: Newfound https://blog.thinknewfound.com/2019/01/fragility-case-study-dual-momentum-gem/ ; Antonacci reply https://www.optimalmomentum.com/whither-fragility-dual-momentum-gem/ ; ReSolve https://investresolve.com/global-equity-momentum-executive-summary/ ; post-publication numbers: https://www.quantifiedstrategies.com/dual-momentum-trading-strategy/
- AQR, "A Century of Evidence on Trend-Following": https://www.aqr.com/Insights/Research/Journal-Article/A-Century-of-Evidence-on-Trend-Following-Investing ; Lempérière et al., "Two Centuries of Trend Following": https://arxiv.org/pdf/1404.3274
- Gray & Vogel, *Quantitative Momentum* / frog-in-the-pan: https://alphaarchitect.com/quantitative-momentum-investing-philosophy/
- Quantpedia momentum factor + sector rotation: https://quantpedia.com/strategies/momentum-factor-effect-in-stocks ; https://quantpedia.com/strategies/sector-momentum-rotational-system ; https://quantpedia.com/how-to-improve-etf-sector-momentum/
- Faber sector rotation (StockCharts writeup): https://chartschool.stockcharts.com/table-of-contents/trading-strategies-and-models/trading-strategies/fabers-sector-rotation-trading-strategy
- Golden cross backtests: https://www.quantifiedstrategies.com/golden-cross-trading-strategy/ ; https://tosindicators.com/research/golden-cross-trading-strategy-20-year-backtest-results
- Trailing stops evidence: Dai et al. https://onlinelibrary.wiley.com/doi/abs/10.1111/irfi.12328 ; https://www.quant-investing.com/blog/truths-about-stop-losses-that-nobody-wants-to-believe
- Minervini/O'Neil rules (grade B-/C, flagged as such): https://www.financialwisdomtv.com/post/how-legendary-traders-enter-breakouts-minervini-kullamagi-darvas-o-neil ; https://www.chartmill.com/documentation/stock-screener/fundamental-analysis-investing-strategies/465-Mark-Minervini-Strategy-Think-and-Trade-Like-a-Champion-Trading-Strategy
- Crowding and momentum tail risk: https://www.cambridge.org/core/journals/journal-of-financial-and-quantitative-analysis/article/abs/crowding-and-tail-risk-in-momentum-returns/870ADE1D7ADCE877CD4C3F5E71581E15
