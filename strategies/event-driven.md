# Event-Driven / Catalyst Strategy Knowledge Base
### For an autonomous LLM trading agent — $5,000 Alpaca paper account, long-only US stocks/ETFs, fractional shares, decisions at 9:45 AM & 3:30 PM ET, weekly Sunday thesis session, max 25%/position, max 8 orders/session

**Evidence grading:** A = replicated in top journals + out-of-sample; B = solid academic or robust practitioner evidence with caveats; C = practitioner/anecdotal or self-reported.
**Decay status:** ALIVE / WEAKENED / DEAD (post-publication decay matters enormously — roughly 50% of anomaly alpha disappears after publication on average, and some effects go to zero).

---

## 1. Post-Earnings Announcement Drift (PEAD) — the flagship strategy

**The evidence.** The Ball & Brown (1968) lineage, formalized by Bernard & Thomas (1989, 1990): after an earnings surprise, prices continue drifting in the surprise's direction for ~60 trading days because investors underreact — they "fail to recognize fully the implications of current earnings for future earnings." Original magnitudes: top-vs-bottom SUE (standardized unexpected earnings) decile spread of ~4–4.5% per quarter (~18% annualized, long-short, pre-cost); good-news stocks alone drifted ~+2% over 60 days. The effect is documented across dozens of countries and is one of the most replicated anomalies in finance (Fama called it the "granddaddy" of underreaction anomalies).

**The decay — critical.** Multiple studies (see the Katz/Caltech "Anomalous Anomaly" paper and the 2020 ScienceDirect review) show: the high-minus-low SUE spread fell from ~5%/quarter in the 1980s–90s to ≤3% by the late 2010s; **PEAD began disappearing from non-microcap stocks around 2001 and was essentially zero in large caps by ~2006**. Causes: decimalization, Reg NMS/HFT, post-SOX faster announcement-day adjustment. Drift measured against analyst-forecast surprises has decayed more than drift against naive (random-walk) surprises. **Where it survives: small caps, low-analyst-coverage stocks, low-attention announcements, and cases where the surprise is confirmed by raised guidance.** Grade: **A** (existence, historical), decay status: **WEAKENED — dead in large caps, alive in small/mid caps and in "surprise + guidance" composites**.

**Concrete rules for the agent:**
- **IF** (at Friday close / Sunday session, and each 9:45 AM window) a stock reported earnings in the last 1–3 trading days **AND** EPS beat consensus by ≥ +10% (or SUE in top ~2 deciles) **AND** revenue also beat **AND** management raised forward guidance **AND** the announcement-day price reaction was positive (gap up that held — direction of initial reaction confirms the market read the news the same way) → **THEN** buy at the 9:45 AM window the morning after the announcement (or the next 9:45 window), position 10–25% of equity.
- **Hold: 20–60 trading days (4–12 weeks)**; drift is front-loaded — practitioner data suggests most accrues in the first 2–3 weeks, with a well-documented secondary bump around the *next* earnings announcement (Bernard–Thomas autocorrelation pattern). Exit before the next earnings report (see §2).
- **Prefer:** small/mid caps ($300M–$10B), ≤10 analysts, positive same-day reaction of +3% to +12%. **Avoid:** mega-caps (no drift left), beats where the stock *fell* on the news (market judged quality low — "beat on non-recurring items" is a classic trap the LLM can detect by reading the release), and beats driven purely by buybacks/tax items.
- **Symmetric warning:** negative-surprise drift is *stronger* than positive drift in the data. Long-only, the agent can't short bad news — but it MUST apply the mirror rule: **IF a held position reports a miss or cuts guidance THEN exit at the next window; do not "wait for the bounce."** Downward drift persists ~60 days too.
- **Expected edge today:** realistically +1.5–3% abnormal return per event over 4–8 weeks in small/mid caps, ~55–60% hit rate. Not the 1980s' 4%+.

**Window mapping:** Pre-market reporters (~7–9 AM ET) → enter at **9:45 AM same day** (gap has settled; academic drift is measured *after* the announcement reaction, so buying post-gap still captures it). After-hours reporters (~4–5 PM) → evaluate at **9:45 AM next morning**. The 3:30 PM window is for exits and for the pre-earnings check below.

---

## 2. Holding Through Earnings — the coin-flip the agent must usually avoid

**The evidence.** Options markets price an "implied move" (ATM straddle cost) before each report. Practitioner datasets (ORATS, EarningsWatcher, Option Alpha) show realized moves exceed the implied move only ~25–63% of the time depending on the name (NVDA ~25%, AMD/META ~63% in recent samples) — i.e., the market's estimate of earnings risk is roughly fair to slightly rich. **Directionally, post-announcement moves are close to 50/50 conditional on public information available beforehand.** A typical single stock moves ±5–8% overnight on earnings; with 25% of a $5k account in one name, one bad print = −1.5 to −2% of total equity in a single unhedged overnight jump the agent cannot manage intraday.

**Counter-evidence (honest note):** Frazzini & Lamont's "earnings announcement premium" — buying stocks *expected to announce* in the coming month earned ~60bp/month excess historically, driven by small-investor attention buying. Grade B, but it's an average across huge diversified portfolios; with 4–8 positions the idiosyncratic risk swamps the premium. **Not implementable at this account's concentration.**

**Concrete rules:**
- **AT EVERY 3:30 PM SESSION:** check the earnings calendar for every held position. **IF** a position reports after today's close or before tomorrow's open **AND** the position was not entered as an explicit PEAD-continuation thesis with a gain cushion ≥ the typical implied move (~6–8%) → **THEN** sell at 3:30 PM. Re-enter post-print via the §1 rules if the report is strong. Cost of this discipline: forgoing the announcement premium and occasional re-entry slippage. Benefit: eliminating the largest single tail risk the twice-daily cadence exposes.
- Grade: **A** (that the pre-announcement direction is near-unpredictable and implied moves are fairly priced); status: **structural, not an anomaly — doesn't decay**.

---

## 3. Analyst Estimate Revisions & Recommendation Changes

**The evidence.** Two related effects:
- **Estimate-revision momentum:** prices drift in the direction of analyst forecast revisions (Givoly & Lakonishok 1979; Chan, Jegadeesh & Lakonishok 1996 — revisions contributed ~3–4% over 6 months; earnings-based momentum decays faster than price momentum). Dische (SSRN): stronger when forecast *dispersion* is low (consensus agreement = higher-quality signal). Zacks built a business on it — self-reported Rank #1 average +23.5%/yr over 37 years, but that is **hypothetical, weekly-rebalanced, pre-cost marketing data (Grade C on the magnitude; Grade B on the direction of the effect)**.
- **Recommendation changes (Womack 1996, J. Finance):** post-upgrade drift **+2.4%, lasting only ~1 month**; post-downgrade drift **−9.1% over ~6 months**. Asymmetry again favors the *sell* discipline over the *buy* signal for a long-only agent.

**Decay:** WEAKENED. Post-2000 (Reg FD) and post-publication, upgrade drift in large caps is small and fast; revision *momentum* (the level and trend of consensus estimates) has held up better than one-off upgrade pops. Alpha decays within days for the recommendation event itself.

**Concrete rules:**
- **Don't buy an upgrade as a standalone catalyst** — by 9:45 AM the +2–4% pop has happened and residual drift is ~1–2% over a month, mostly inside bid-ask noise at this scale.
- **DO use revisions as a confirmation filter and Sunday-session screen:** IF a PEAD/news candidate also has ≥2 analysts raising estimates in the past 2 weeks AND consensus FY EPS rising → upgrade conviction/size. IF consensus estimates for a *held* name are being cut → exit at next window (piggybacks Womack's −9.1% downgrade drift).
- **Sunday thesis session:** screen for stocks with the largest 4-week % increase in consensus FY estimates (the Zacks-style factor), intersect with recent earnings beats. Hold 4–12 weeks.
- Grade: **B**; status: **WEAKENED but alive as a slow-moving factor, dead as a same-day event trade**.

---

## 4. Index Inclusion / Deletion — DEAD; do not trade

**The evidence.** Greenwood & Sammon, "The Disappearing Index Effect" (Journal of Finance, 2025): S&P 500 addition abnormal returns went from +3.4% (1980s) → **+7.4% (1990s) → <1% and statistically indistinguishable from zero in the 2010s–2020s**, despite indexed assets *growing*. Deletion effects also ~zero. Mechanisms: pre-positioned liquidity providers, index migrations from the S&P 400, S&P's own methodology changes. Same decay documented across other index families. Occasional idiosyncratic spikes (e.g., a mega-momentum name added) are not a systematic edge and the announcement pop happens in after-hours minutes, which the agent cannot access.
- **Rule: NO TRADE on index add/delete announcements.** At most, treat an upcoming S&P inclusion as a modest liquidity/attention tailwind footnote in an existing thesis.
- Grade: **A** (evidence of decay); status: **DEAD**. This is the knowledge base's clearest example of why decay status matters.

---

## 5. Insider Buying (Form 4 Clusters)

**The evidence.** Open-market *purchases* predict returns; sales mostly don't (liquidity-driven). Key refinements:
- **Cohen, Malloy & Pomorski (2012, J. Finance), "Decoding Inside Information":** separating **opportunistic** (irregular-timing) from **routine** (same-month-every-year) traders — opportunistic buys carry ~**+5.2% six-month alpha**; routine trades carry none.
- **Cluster buys** (≥2–3 distinct insiders buying within ~2–4 weeks) roughly **double** the signal of single buys; historical estimates ~4–8% abnormal over 6–12 months, strongest in **small caps** (~7.4% over 12 months for officer cluster buys in small caps per one summary), strongest for **officers/CEO/CFO** and buys after price declines.

**Decay:** WEAKENED but alive — well-known since the 1970s yet persistent, likely because it's concentrated in illiquid small caps and slow-moving. Post-publication attenuation exists but the opportunistic-cluster subset has held up. Grade: **B+**.

**Concrete rules:**
- **IF** ≥2 distinct insiders (at least one being CEO, CFO, or a director buying meaningfully, e.g., ≥$50k or ≥25% salary equivalent each) file Form 4 open-market **P** (purchase) transactions within 14 days **AND** the buys are not routine (no same-calendar-month purchases in prior years, not 10b5-1 plan) **AND** market cap <$10B → **THEN** buy at next 9:45 AM window. **Hold 3–6 months** (this is the agent's longest-horizon event signal — manage it in the Sunday session, not daily).
- **Ignore:** option exercises, 10b5-1 plan buys, tiny token buys, purchases by 10% institutional owners rebalancing.
- **LLM edge:** Form 4s are free on EDGAR in near-real-time; parsing transaction codes, footnotes (where 10b5-1 status hides), and insider purchase history is exactly a reading-comprehension task. Filings land throughout the day → act at the next window; the signal's 6-month horizon makes hours of latency irrelevant.

---

## 6. FDA / Biotech Catalysts, Product Launches, Guidance Changes

**FDA/PDUFA binary events:** Grade B evidence that these are **lotteries, not edges**, for an outsider: single-day moves of ±40–200%; heavy run-ups into PDUFA dates followed by "sell-the-news" drift *even on approval* (approval value already priced during development); adverse outcomes gap −50%+ overnight with no exit opportunity for a twice-daily trader. **Rules:**
- **NEVER hold a small/mid-cap biotech through a scheduled PDUFA date, AdCom vote, or Phase 2/3 topline readout** — same logic as §2 but with fatter tails. 3:30 PM check: maintain a catalyst calendar (RTTNews/BiopharmaWatch-style FDA calendars) for every held name.
- **Tradable long-only variant:** *post*-event drift on **surprising, under-covered positive outcomes** — e.g., an unexpected approval, label expansion, or strong Phase 3 data in a small cap with low coverage; large-cap partner reactions (big pharma moves little on partner's positive readout → mild drift). Enter 9:45 AM after the event *only if* the agent can articulate why the market's initial repricing understates commercial value (peak-sales math vs. added market cap). Hold 2–8 weeks. This is a **C+/B− discretionary play** — cap at ≤10% of equity.
- **"Sell-on-news" corollary:** never buy the run-up into a known catalyst date.

**Product launches:** weak systematic evidence; anticipation is priced. Only tradable version: post-launch *data points* (preorder numbers, app-store ranks, prescription data mentioned in news) that surprise — treat under news-drift rules (§7). Grade C.

**Guidance changes (non-earnings-day):** Grade B, underrated. Academic work (Das et al. on management forecasts) documents **post-guidance drift** analogous to PEAD, economically significant net of costs; a mid-quarter *unscheduled* guidance raise is rarer and stronger than an earnings-day one (managers raise only with high confidence). Caveat: one study finds investors *overweight* guidance relative to analyst forecasts when the gap is extreme — avoid chasing guidance that's wildly above consensus on thin reasoning. **Rule: IF a company issues an unscheduled guidance raise (8-K/press release) with specifics (raised revenue AND EPS ranges) THEN treat identically to a top-decile earnings beat: buy next 9:45 window, hold 4–8 weeks.** Mirror: unscheduled guidance *cuts* on held names → exit immediately (pre-announcement of bad quarters drifts down hard).

---

## 7. News Sentiment Drift — the agent's native habitat

**The evidence chain:**
- **Chan (2003, JFE):** stocks with big moves *accompanied by public news* exhibit **drift (momentum) for up to 1–12 months**, concentrated in bad news and small caps; big moves *without* news **revert**. This news/no-news distinction is the single most useful classification an LLM reader can make.
- **Tetlock (2007, 2011):** media pessimism predicts short-horizon pressure then reversion; **stale/reprinted news** triggers overreaction that *reverses* — the agent must distinguish genuinely new information from recycled coverage (an LLM-tractable task humans do poorly at scale).
- **Speed of incorporation:** for large caps, headline information is ~fully priced within minutes-to-hours; residual drift lives in **small caps, complex news (litigation outcomes, contract wins with hard-to-value terms, 8-K details, spin-off filings), and negative news** (limits-to-arbitrage: shorting frictions slow bad-news pricing — long-only, this again mostly gives the agent an *exit* edge, plus buying overdone no-news dips).
- **LLM-specific: Lopez-Lira & Tang (2023, "Can ChatGPT Forecast Stock Price Movements?", SSRN 4412788):** GPT-4 headline scores predicted next-day returns; the *tradable drift* component (entering the next session, i.e., exactly this agent's constraint) showed **hit rates ~55–58%, mean ~0.34–0.50% per event, pre-cost Sharpe ~2.6–3.0 across a diversified daily portfolio** — strongest in **small stocks and negative news**. Two crucial caveats the agent must internalize: (1) capability scales with model size; (2) **the paper documents that returns to the strategy decline as LLM adoption rises** — this edge is actively decaying because every desk now runs it. Grade: **B**, status: **ALIVE but WEAKENING fast in liquid names**.

**Concrete rules:**
- **At each window:** sweep news since the last window. Classify each held/candidate name: (a) *material new information* vs. stale/recycled; (b) direction and magnitude vs. what's plausibly priced (compare to the actual price move); (c) news-driven move vs. no-news move.
- **BUY rule:** IF small/mid-cap has genuinely new, quantifiable positive news (contract win with disclosed dollar value, favorable litigation/regulatory resolution, unexpected guidance raise) AND the price reaction seems incomplete relative to a back-of-envelope value estimate AND the story broke <24h ago → buy, hold **3–15 trading days**, exit on price target or staleness.
- **DIP rule (Chan's no-news reversal):** IF a held or watchlist name dropped >5% on *no identifiable news* (verify by exhaustive search — this is the LLM's comparative advantage) → candidate to buy the reversal, hold 1–4 weeks. Grade B.
- **NEVER** buy a large cap at 9:45 AM because of a headline from 7 AM "before the market notices." The market noticed. For mega-caps assume ≤30 minutes to full incorporation.

---

## 8. Macro Event Playbooks: FOMC & CPI

**Pre-FOMC announcement drift.** Lucca & Moench (2015, J. Finance): 1994–2011, the S&P earned **~49bp in the 24h before scheduled FOMC announcements** — ~80% of the era's equity premium. Post-publication evidence is **split**: a Finance Research Letters paper ("The disappearing pre-FOMC announcement drift") finds it **essentially gone after 2015**; practitioner backtests through 2024 (QuantSeeker) find it flat 2016–2019 but **resurgent in high-uncertainty years (2020, 2022–23)**, with the drift concentrated in high-VIX regimes and near-zero when VIX is low. Honest synthesis: **regime-dependent, WEAKENED**; Grade B for the conditional version.
- **Rule:** IF tomorrow is a scheduled FOMC decision day AND VIX > ~20 → buy SPY (or hold existing equity rather than trimming) at the **3:30 PM window the day before**; reassess at the **3:30 PM window on decision day** (post-2:00 PM announcement — the agent conveniently gets a post-announcement decision slot). IF VIX < 15 → no trade. Expected edge: ~25–50bp per event in high-vol regimes; ~8 events/year. Small but nearly free to harvest with SPY.
- **FOMC-cycle "even weeks"** (Cieslak, Morse & Vissing-Jorgensen, J. Finance 2019): equity premium since 1994 earned in weeks 0, 2, 4, 6 after FOMC meetings. Grade B academically, but post-publication out-of-sample evidence is thin — use only as a scheduling nuance (prefer initiating longs early in even weeks), not a standalone strategy. Status: **UNCERTAIN/WEAKENED**.

**CPI day.** No reliable *unconditional* premium. Recent work (Applied Economics Letters, 2021–2025 sample of 48 releases): **cooler-than-expected CPI → +0.88% to +1.19% abnormal S&P return over 1–2 days (significant); hotter-than-expected → losses of similar size but statistically insignificant**. The reaction happens at 8:30 AM, before the agent's first window — **the 8:30 print is NOT tradable as a reaction**, but the 1–2 day continuation after a *large dovish surprise* is marginally accessible at 9:45.
- **Rule:** IF CPI (core, MoM) printed ≥0.1pp *below* consensus at 8:30 AM → permissible to add broad-index exposure (SPY/QQQ) at 9:45 AM, hold 1–2 days. IF CPI hot → do nothing aggressive, but tighten exits on high-beta positions at 9:45. Grade: **C+** (short sample, regime-specific — this pattern is an artifact of the 2021–2025 inflation-targeting regime and should be assumed **decaying** as inflation normalizes).
- **Both macro events:** primary value is **risk management, not alpha** — the 3:30 PM pre-event check should flag "FOMC/CPI tomorrow" and veto opening new concentrated positions into macro binaries.

---

## Bonus signal (LLM-native): filing-language changes ("Lazy Prices")

Cohen, Malloy & Nguyen (J. Finance 2020): firms that make **significant textual changes to their 10-K/10-Q** (especially in risk factors, litigation, executive-team language) subsequently underperform; **non-changers outperform** — long-short alpha up to 188bp/month in the original sample, with **no announcement-day reaction** (pure inattention; returns accrue over months). For a long-only agent: use as a **screen and a veto** — at the Sunday session, diff the latest 10-Q/10-K risk factors of held names against the prior filing; materially expanded risk language → reduce/exit; unchanged boilerplate → comfort. Grade: **B**; status: presumed **WEAKENED** post-publication (NLP funds arbitrage it) but the *veto* use costs nothing. This is among the most LLM-suited signals in existence — it is literally a reading task no human retail investor performs.

---

## The LLM Agent's Realistic Edge

1. **Breadth of reading, not speed.** The agent will never beat HFT to a headline; it can beat *any human* at reading every 8-K, Form 4 footnote, guidance table, and small-cap press release issued since the last window. Every strategy above was therefore filtered for **multi-day-to-multi-month horizons** where hours of latency don't matter: PEAD (weeks), insider clusters (months), revisions (weeks-months), guidance drift (weeks), filing diffs (months).
2. **Classification quality.** The documented edges live in distinctions LLMs handle well: opportunistic vs. routine insider buys; new vs. stale news; earnings beat "quality" (organic vs. one-off); guidance specificity; risk-factor language changes. Lopez-Lira & Tang is direct evidence LLM judgment adds return-relevant signal beyond the initial price move — with the sober caveat that this exact edge is being competed away by other LLMs.
3. **Discipline as alpha.** Half this playbook is *avoidance* rules (no holds through earnings/PDUFA, exit on misses/guidance cuts/estimate cuts immediately, no index-add trades, no chasing priced headlines). The academic asymmetries (bad-news drift > good-news drift; downgrade drift −9.1% vs. upgrade +2.4%) mean a long-only account's biggest quantifiable edge is **selling deteriorating positions faster than humans do** — no hope, no anchoring.
4. **Where the money concentrates:** small/mid caps, low coverage, complex disclosures. Fractional shares on Alpaca make a $500–$1,250 position in a $400 stock feasible. A realistic composite expectation: 3–6 concurrent event positions, each targeting 1.5–4% abnormal return over 2–8 weeks, ~55–60% hit rate — meaningful but modest; anyone promising the 1980s academic magnitudes is quoting dead history.

## Failure Modes

- **Trading dead anomalies:** index effect (dead), large-cap PEAD (dead), unconditional pre-FOMC drift in calm regimes (dormant). The knowledge base must be treated as perishable; re-verify decay annually.
- **Stale-news overreaction:** buying a "catalyst" that is recycled coverage (Tetlock) → buying tops. Mandatory first-report timestamp check.
- **Gap risk with 25% positions:** one earnings/PDUFA hold-through mistake costs more than a month of drift harvesting. The 3:30 PM calendar check is the single most important routine in this document.
- **Small-cap microstructure:** wide spreads eat 20–100bp per side; drift edges of 1.5–3% survive this only if turnover is controlled — no round-tripping positions inside a week without a specific exit trigger.
- **Sell-on-news traps:** buying FDA approvals or product launches that were fully priced during the run-up.
- **Data-quality traps:** consensus-estimate figures from free sources differ from the institutional consensus that defines the "surprise"; whisper numbers explain many "beat but fell" reactions — the announcement-day price reaction is the ground-truth arbiter, always defer to it.
- **Crowding by other LLMs:** the Lopez-Lira finding that returns fall as LLM adoption rises applies to this agent itself; expect news-drift edges to compress in liquid names first and retreat toward smaller caps and longer horizons.
- **Long-only asymmetry:** the strongest documented drifts (negative surprises, downgrades, bad news) are short-side. The agent can only monetize them defensively; sizing expectations must reflect harvesting the weaker half of each anomaly.

## Sources

- PEAD review & decay: [Katz et al., "PEAD: An Anomalous Anomaly" (Caltech)](https://jkatz.caltech.edu/documents/28622/peads.pdf) · [ScienceDirect review of PEAD](https://www.sciencedirect.com/science/article/pii/S2214635020303750) · [Wikipedia: PEAD](https://en.wikipedia.org/wiki/Post%E2%80%93earnings-announcement_drift) · [The Logbook PEAD summary](https://freeportlogbook.substack.com/p/post-earnings-announcement-drift) · [FMP PEAD implementation](https://site.financialmodelingprep.com/education/other/tracking-postearnings-announcement-drift-with-fmps-market-data)
- Implied vs realized moves: [ORATS Nvidia expectations vs reality](https://orats.com/blog/nvidia-earnings-options-market-expectations-vs-reality) · [EarningsWatcher beat rates](https://earnings-watcher.com/wiki/earnings-expected-moves) · [Option Alpha IV expected vs actual](https://optionalpha.com/lessons/iv-expected-vs-actual-move) · [Resonanz on straddles](https://resonanzcapital.com/insights/options-straddles-and-earnings-move-estimates)
- Earnings announcement premium: [Frazzini & Lamont (SSRN)](https://papers.ssrn.com/abstract=986940) · [NBER digest](https://www.nber.org/digest/mar08/stocks-rise-around-earnings-announcements)
- Analyst revisions/recs: [Jegadeesh 2001 momentum](https://breesefine7110.tulane.edu/wp-content/uploads/sites/16/2015/10/Momentum-2001.pdf) · [Womack 1996 (J. Finance)](https://onlinelibrary.wiley.com/doi/abs/10.1111/j.1540-6261.1996.tb05205.x) · [Dische, dispersion & earnings momentum (SSRN)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=270036) · [Zacks Rank methodology/returns (self-reported)](https://www.zacks.com/stocks/zacks-rank)
- Index effect: [Greenwood & Sammon, "The Disappearing Index Effect" (J. Finance 2025)](https://onlinelibrary.wiley.com/doi/10.1111/jofi.13410) · [NBER w30748](https://www.nber.org/system/files/working_papers/w30748/w30748.pdf) · [Alpha Architect summary](https://alphaarchitect.com/disappearing-index-effect/)
- Insiders: [Quant Decoded: insider trading signals](https://quantdecoded.com/en/insider-trading-signals-informative-trades) · [arXiv microcap insider study](https://arxiv.org/html/2602.06198v1) · [MarketTriage cluster definitions](https://markettriage.com/insider-trading-signals)
- FDA/biotech: [BiopharmaWatch FDA guide](https://www.biopharmawatch.com/blog/how-to-invest-in-biotech-stocks-beginners-guide-fda-approvals-clinical-trials-pdufa-dates) · [DrugPatentWatch on approval effects](https://www.drugpatentwatch.com/blog/overnight-millionaires-or-a-decade-long-marathon-deconstructing-the-drug-patent-approval-effect-on-stocks/) · [Biotech Analyzer: why approvals drop](https://biotechanalyzer.com/insights/why-some-fda-approvals-trigger-stock-drops-instead-of-gains)
- Guidance: [Das et al., management forecasts (NYU Stern)](https://web-docs.stern.nyu.edu/salomon/docs/conferences/das%20et%20al.pdf) · [HBS: when guidance is most influential](https://www.hbs.edu/ris/Publication%20Files/00-042_4b511b76-c732-4afb-9bd1-e675530be523.pdf)
- News drift: [Chan 2003, JFE](https://www.sciencedirect.com/science/article/abs/pii/S0304405X03001466) · [Tetlock, stale news](http://www.econ.yale.edu/~shiller/behfin/2007-12/tetlock.pdf) · [Fed Board: predicting returns from news](https://www.federalreserve.gov/econresdata/feds/2016/files/2016048pap.pdf) · [Lopez-Lira & Tang (SSRN 4412788)](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4412788) / [arXiv 2304.07619](https://arxiv.org/abs/2304.07619)
- Filings language: [Cohen, Malloy & Nguyen, "Lazy Prices" (J. Finance 2020)](https://onlinelibrary.wiley.com/doi/abs/10.1111/jofi.12885) · [NBER w25084](https://www.nber.org/system/files/working_papers/w25084/w25084.pdf)
- Macro: [Lucca & Moench 2015 (J. Finance)](https://onlinelibrary.wiley.com/doi/abs/10.1111/jofi.12196) · [NY Fed SR512](https://www.newyorkfed.org/research/staff_reports/sr512.html) · ["The disappearing pre-FOMC announcement drift" (FRL)](https://www.sciencedirect.com/science/article/abs/pii/S1544612320315956) · [QuantSeeker 1993–2024 backtest](https://www.quantseeker.com/p/trading-the-fed-the-pre-fomc-drift) · [Cieslak, Morse & Vissing-Jorgensen (J. Finance 2019)](https://onlinelibrary.wiley.com/doi/abs/10.1111/jofi.12818) · [StockAlarm CPI asymmetry summary](https://pro.stockalarm.io/blog/cpi-inflation-report-stock-market)
- Factor decay generally: [arXiv: "Not All Factors Crowd Equally" (alpha decay)](https://arxiv.org/pdf/2512.11913)
