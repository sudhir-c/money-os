# The Documented Methods of History's Most Successful Traders
### A knowledge base for an autonomous LLM trading agent ($5,000 paper account, long-only US stocks/ETFs, fractional shares, decisions at 9:45 AM & 3:30 PM ET, weekly thesis session, max 25% per position)

**Verifiability grades:** **A** = independently audited/documented (broker statements, court/audit records, contemporaneous press verification, published mechanical rules). **B** = well-documented by the trader's own books/interviews and corroborated by credible secondary sources, but not independently audited. **C** = legend, self-reported, or unverifiable; treat as folklore that may still carry instructional value.

---

## Jesse Livermore (1877–1940)

### Documented rules (*Reminiscences of a Stock Operator*, 1923; *How to Trade in Stocks*, 1940)
- **Trade only the line of least resistance.** Buy strength in bull markets. "Prices are never too high to begin buying or too low to begin selling."
- **Pivotal points.** Wait for price to break a key level (prior high, top of a long consolidation) and *confirm* by continuing before committing — the direct ancestor of every breakout method below.
- **Probe, then pyramid.** Never take the full position at once. Initial probe (~20% of intended size); add *only if the position shows a profit*, at successively higher prices. "It never was my thinking that made the big money for me. It was always my sitting."
- **Never average down** — the cardinal sin in his own writing.
- **Cut losses fast** (~10% bucket-shop-era rule; formalized as exiting when the pivotal-point break fails).
- **Market filter:** trade with "general conditions"; sit in cash when unclear.
- **Sell when the market tells you** — a leader failing to make new highs while the market does, or breaking pivotal support.

### Record vs. myth — Grade B/C
The 1907 (~$1M in a day) and 1929 (~$100M) wins are contemporaneously reported (B); precise figures unauditable (C). **The cautionary arc is equally documented:** broke at least four times (bankruptcies 1915, 1934), lost the 1929 fortune within years — largely by *breaking his own rules* (averaging losers, trading on tips — the Percy Thomas cotton trade) — and died by suicide in 1940. **The rules worked; the man's inability to follow them destroyed him. The single strongest argument for a mechanical, rule-bound agent in this entire corpus.**

### Transferability
Pivotal-point breakouts, pyramiding only into winners, never averaging down, and the general-conditions filter all transfer directly. Pyramiding: treat 25% as the *fully pyramided* maximum (10% probe → +8% → +7%). His blowups are the doctrine: the agent must be architecturally unable to override stops, average down, or "take a flyer." An LLM's equivalent of Livermore's tip-taking is narrative-driven rationalization; the weekly session should audit for it.

---

## Nicolas Darvas (1920–1977)

### Documented rules (*How I Made $2,000,000 in the Stock Market*, 1960)
- **Box theory.** A rising stock oscillates in "boxes" — a range with defined ceiling/floor (top set when a high isn't penetrated ~3 consecutive days). Buy **only** on a decisive break above the current box top, ideally into all-time-high territory, on expanding volume.
- **On-stop buy orders** just above the box top — the market executed his plan without him watching (he traded by telegram from world dance tours, one daily/weekly quote).
- **Trailing stop under the box.** Initial stop just below the breakout level; as the stock climbs into a new higher box, raise the stop to just below the new box floor. Never sell "because it's high" — only on the trailing stop. This is how he rode Lorillard, Universal Products, Thiokol.
- **Techno-fundamentalist selection:** boxes/new highs in industries with dramatic earnings-growth expectations. Primary screen: weekly *Barron's* — a *weekly* research cadence.
- **Market filter:** implicit — nothing makes new highs in bear markets; he sat 100% cash for long stretches.
- **No tips, no brokers' advice, no "bargains," no averaging down.**

### Record vs. myth — Grade C+ (method A-documented, P&L disputed)
*Time* (May 1959) profiled the ~$2M run in ~18 months. In 1960 the NY AG claimed ascertainable profits of only ~$216,000; courts blocked the probe (Jan 1961) as a press-freedom matter, so the dispute was **never resolved**. Even the AG's floor (~$216k ≈ $2M+ today) is a large gain. Survivorship caveat: he traded the 1957–59 bull.

### Transferability — **the single most relevant profile for this agent**
Darvas is the historical existence proof that a **low-information, low-frequency loop** (weekly deep research + daily quote checks + pre-placed mechanical orders) can capture huge trends — nearly isomorphic to this agent's cadence. Weekly session = Barron's screen; 9:45/3:30 checks = "did price break the box top / hit the trailing stop?" Caveat: his tight initial stops caused rapid whipsaw re-entries via standing orders; a 2-window agent should use slightly wider stops.

---

## William O'Neil (1933–2023) — CANSLIM

### Documented rules (*How to Make Money in Stocks*, 4th ed.; IBD)
**The seven letters:**
- **C** — Current quarterly EPS up ≥25% vs year-ago (accelerating is best), ideally sales up ≥25%.
- **A** — Annual EPS growth ≥25% compound over 3 years; ROE ≥17%.
- **N** — New: product, service, management, industry condition, or **new price high**. Big winners emerge from proper bases *near new highs*.
- **S** — Supply/demand: reasonable float; breakouts on volume **40–50%+ above average**; tightness and volume dry-up in bases.
- **L** — Leader: buy the #1–#3 stock in a leading industry group; RS rating ≥80 (preferred 90+). Never buy laggards.
- **I** — Institutional sponsorship: increasing quality fund ownership (some, not over-owned).
- **M** — **Market direction: the master filter.** 3 of 4 stocks follow the market. (a) **Distribution days** — 4–6 decline-on-rising-volume days in the indexes within ~5 weeks marks a top; (b) **follow-through day** — index rising ~1.25–1.7%+ on higher volume, day 4–10 of a rally attempt, confirms a new uptrend. No buying in confirmed downtrends.

**Entry:** the **cup-with-handle** — prior uptrend ≥30%; base 7–65 weeks, 12–33% deep; handle drifting *down* on light volume in the upper half; buy point = handle high + $0.10; never chase >5% past the pivot. Also: flat base, double bottom, base-on-base.

**Sell rules (selling is harder and more important than buying):**
- **Hard stop: sell ANY stock 7–8% below buy price. No exceptions.** 3:1 ratio — take 20–25% gains, never allow more than 7–8% losses.
- **Take most profits at 20–25%** — *except* the **8-week hold rule**: a stock gaining 20%+ within 3 weeks of breakout is held at least 8 weeks (possible monster).
- Sell into **climax runs** (largest daily gain of the move, exhaustion gaps, late 25–50% spurts on huge volume).
- Sell on base failure, break of the 50-day line on big volume after an extended move, and when M turns.

### Record vs. myth — Grade B
Verified: youngest NYSE seat buyer at 30 (1963), funded by a documented 1962–63 run; founded William O'Neil + Co. and IBD. Personal-account percentage claims are self-reported (C). The *model book* study of the greatest winners (1880s–present) is real published research. AAII's independent CANSLIM-screen tracking showed strong multi-decade outperformance (B).

### Transferability — **highest structural transfer of any profile**
CANSLIM was designed for end-of-day decision-making by part-time individuals. Weekly session = screen + watchlist with pivots; 9:45 = overnight gaps/breakouts; 3:30 = volume-confirmed breakouts near the close. The **M filter is computable from daily index OHLCV** — the agent's regime switch. The **7–8% stop + 20–25% profit rule + 8-week exception** is a complete, unambiguous, LLM-executable exit system. Caution: O'Neil warned against buying in the first ~30–45 minutes on gap days — prefer 3:30 confirmation for marginal breakouts.

---

## Mark Minervini — SEPA

### Documented rules (*Trade Like a Stock Market Wizard*, 2013; *Think & Trade Like a Champion*, 2017)
**SEPA:** (1) Trend — only Stage 2 uptrends; (2) Fundamentals — accelerating earnings/sales/margins; (3) Catalyst; (4) Entry point — low-risk pivot from a sound base; (5) Exit points — predefined stop and profit plan.

**The Trend Template — all 8 criteria must be met:**
1. Price above both the 150-day and 200-day MAs.
2. 150-day MA above the 200-day MA.
3. 200-day MA trending up ≥1 month (preferably 4–5+).
4. 50-day MA above both the 150- and 200-day MAs.
5. Price above the 50-day MA.
6. Price ≥25–30% above its 52-week low.
7. Price within 25% of its 52-week high.
8. RS ranking ≥70 (preferably 80s–90s), RS line rising.

**VCP (Volatility Contraction Pattern):** 2–6 progressively *tighter* contractions (each pullback roughly half the prior — 25% → 12% → 6% → 3%), volume drying up to "no supply" in the final tightness; buy the pivot breakout as volume expands.

**Risk doctrine (his most mechanical contribution):**
- Risk defined *before* entry; **average loss ~5–6%, never let any loss exceed 10%** (the "sound barrier").
- Reward/risk ≥2:1, preferably 3:1 at the trade level.
- **Progressive exposure:** pilot positions first; scale up only when recent trades are working — your own P&L is the best market indicator. Size down automatically after failures.
- Move stop to breakeven after a cushion; **never let a 2–3× risk gain turn into a loss**.
- Sell into strength when extended.

### Record vs. myth — Grade A–
1997 US Investing Championship: **+155%** (real-money, monitored — A). 2021 USIC: **+334.8%** (A). The "~220%/yr audited 5-year run" cites a KPMG audit that isn't public (B). Ongoing claims self-reported (C); he sells education — weigh incentive bias. The contest results are genuinely externally verified.

### Transferability
The **Trend Template is 100% mechanical from daily OHLCV** — adopt as the non-negotiable candidate filter. VCP proxies are computable (shallower successive pullbacks, contracting ranges, declining volume). The risk doctrine transfers verbatim. Nothing in SEPA requires intraday action.

---

## Dan Zanger

### Documented rules (interviews — *Fortune* Dec 2000; chartpattern.com)
- Pure chart-pattern breakout trading in the market's fastest leaders: cup-with-handle (learned from O'Neil's book), high tight flags, channels, wedges, triangles.
- **Volume is the #1 confirmation** — breakouts without volume are suspect.
- Buy the breakout above the pattern pivot; **sell if it fails back below the breakout point**. Never chase more than a few percent.
- Trade only the cycle's leaders; concentrate heavily; full margin in raging bulls; cut exposure fast when patterns fail en masse (pattern-failure breadth as market filter).
- Days-to-weeks holds; obsessive nightly chart review; 10–11 hours/day at screens.

### Record vs. myth — Grade A for the core run, C after
**~$10,775 → ~$18M in under 2 years (1998–2000), ~29,233% in 12 months on margin** — first 12 months audited, and *Fortune* reviewed tax returns and trading records before publishing. One of the few *externally verified* extreme retail runs. **Nothing since audited.** Context: full margin + the most explosive momentum market since 1929 + survivorship. He blew up accounts before 1997.

### Transferability
Confirms the O'Neil playbook's ceiling in real money — but his edge conditions (margin, intraday tape-reading, a bubble) don't transfer. Transferable: volume-confirmed breakouts only; sell immediately on pivot failure; concentrate in the cycle's leaders; pattern-failure breadth as an early regime warning.

---

## The Turtle Traders (Richard Dennis & William Eckhardt, 1983–88)

### Documented rules — the fullest public mechanical system ("The Original Turtle Trading Rules" PDF)
- **Volatility unit "N":** N = 20-day exponential ATR. **1 Unit = 1% of equity ÷ (N × dollars per point)** — every position sized so a 1N move ≈ 1% of equity.
- **Entries:** System 1: **20-day Donchian breakout**, *skipped if the previous S1 breakout in that market would have been a winner* (the 55-day breakout catches missed trends). System 2: **55-day breakout, always taken**.
- **Initial stop: 2N from entry** (= 2% equity risk/unit); stops raised ½N per add-on.
- **Pyramiding:** add 1 unit each **½N of favorable movement**, up to **4 units**/market; heat limits: 6 units correlated, 10 per direction, 12 total.
- **Exits:** System 1 on a **10-day low**; System 2 on a **20-day low**. No profit targets — ever. Large open-profit givebacks by design.
- **Drawdown rule: cut unit size 20% for each 10% drawdown.**
- Expect ~40–50% win rate; expectancy lives in a few huge trends; **taking every signal is mandatory** (the skipped signal is the one that pays for the year).

### Record vs. myth — Grade A for the experiment, B for the numbers
The experiment is thoroughly documented (Covel, Faith). Aggregate ~80%/yr claims are Dennis-attributed; individual results varied enormously; several Turtles (Jerry Parker/Chesapeake) built long verified CTA records (A). The raw 20/55-day edge has decayed since the 1980s. It was a **futures** system — long-only equities means fewer independent bets and higher correlation (heat rules matter *more*).

### Transferability — **the most transferable framework, if not the parameters**
(1) ATR-based sizing works perfectly at $5k with fractionals; (2) 2-ATR initial stops; (3) close-basis Donchian entries/exits computable at 3:30 (the honest adaptation of intraday breaks); (4) ½N pyramiding within the 25% cap; (5) the drawdown governor (−20% size per −10% equity) is an ideal autonomous-agent safety valve; (6) correlation limits: "don't hold 4 stocks that are the same trade." **"Take every valid signal" is *more* enforceable for an LLM than for the humans who failed by second-guessing.**

---

## Qullamaggie — Kristjan Kullamägi

### Documented rules (qullamaggie.com; Chat With Traders #201)
**Setups:** (1) **Breakout:** strong momentum leg (+30–100%+ in 1–3 months), consolidation 2–8+ weeks with higher lows/tightening range/declining volume, surfing the rising 10/20-day MA; buy the opening-range-high break; stop = low of day. (2) **Episodic Pivot (EP):** gap-up ≥10% on a *game-changing catalyst* in a stock that hasn't already run, on massive early volume; buy day-1 ORH; stop = low of day. (The logic: institutional repricing takes days-to-months — PEAD monetized.) (3) Parabolic short — **long-only, excluded**.

**Exit doctrine:**
- **Sell 1/3 to 1/2 into strength after 3–5 days** (pays for the trade).
- **Trail the remainder on the 10-day (faster) or 20-day MA (bigger swing) — sell only on a *close* below.** Monsters move to the 50-day.
- Breakeven stop quickly after day 1–3 strength.
- **Win rate ~25–35% by his own statements**; losers are ~0.5–1R scratches, winners 5–20R+. Most breakouts fail; the system expects it.
- **Market filter:** trades biggest in uptrends; sizes down dramatically or sits out in chop; "how are breakouts acting" is the real regime tell.
- Sizing: risks ~0.25–1% per trade (positions 10–20%+ with tight day-low stops).

### Record vs. myth — Grade B+
~$5k-ish (several blowups) → profitable from ~2013 → **$100M+ claimed by ~2021–23**, with partial verification (streamed his live account for years; third-party citations of audited statements; Nordic press tax records indicating nine-figure income). Not a formal full-run audit. Peak years coincided with 2020–21's friendly momentum tape.

### Transferability
His exit engine — **partial sell into strength day 3–5, trail rest on 10/20-day MA close-basis** — is arguably the *best-fit exit system in this corpus for a 2-window agent* (a 3:30 check approximates close-basis MA trails well). EPs on earnings gaps are executable at 9:45 (crude "ORH-15"). Day-low stops must widen to prior-day low or 2-ATR. His high-ADR small/mid caps raise gap risk — cap size below the 25% max on volatile names.

---

## Stanley Druckenmiller & George Soros

### Documented doctrine (*The New Market Wizards*; *Alchemy of Finance*; Lost Tree Club speech 2015)
- **The sizing-asymmetry doctrine:** *"When you have tremendous conviction on a trade, you have to go for the jugular… It's not whether you're right or wrong, but how much you make when you're right and how much you lose when you're wrong."* Sizing is "70–80% of the equation."
- **Concentrate, don't diversify:** few big bets a year; watch the basket closely. (1992 GBP short: ~$10B position, ~$1B+ profit.)
- **When wrong, fold instantly and completely** — Soros: "I'm only rich because I know when I'm wrong." Druckenmiller flipped from short to long within days around the 1987 crash.
- **Never trade to recover / when emotional; when confused, go to cash.** Druckenmiller's worst loss (buying $6B of tech near the March 2000 top, −$3B) came, by his own telling, from envy/FOMO: "I knew better, I did it anyway."
- **Preserve capital first; compound hard when hot.** Press when running hot; shrink after losses.
- Look 12–18 months ahead; liquidity (central banks) moves markets, not earnings.

### Record vs. myth — Grade A
Quantum ~30%+ annualized over ~30 years; Duquesne ~30% annualized over 30 years with **zero losing years**. The pound trade is exhaustively documented. The 2000 tech loss is self-reported but corroborated.

### Transferability
Policy, not setups: (1) **conviction-tiered sizing** — 25% is the "jugular" tier, earned only by A-grade setups; don't default to 4 equal 25% slots. (2) **Asymmetry accounting:** judge the system by avg-win/avg-loss, not win rate — a mandated weekly metric. (3) **Reversal without ego** — no narrative sunk-cost between windows. (4) **The 2000 lesson is the LLM's chief failure mode:** buying a story late under FOMO-narrative pressure; encode "never initiate in a name extended >X% above the pivot/MA" as a hard rule. (5) Cash is a position; confusion → flat.

---

## Paul Tudor Jones

### Documented rules (*Market Wizards*; the 1987 *Trader* documentary; Tony Robbins interview)
- **The 200-day moving average is his master filter:** *"My metric for everything I look at is the 200-day moving average of closing prices… If it goes under the 200-day moving average, you get out."* It had him flat/short into the 1987 crash. "I've seen too many things go to zero."
- **5:1 reward/risk doctrine:** *"5:1 means I'm risking one dollar to make five… I can be wrong 80% of the time and still not lose."*
- **Defense first:** "Play great defense, not great offense." "Don't focus on making money; focus on protecting what you have." Sizes down when trading worst; "every day I assume every position I have is wrong."
- **Never average losers** — the sheet of paper above his desk: **"Losers Average Losers."**
- Decrease size when losing, increase when winning.
- 1987: ~+125% net for the year (some sources higher), shorting into the crash after 1929-analog work.

### Record vs. myth — Grade A
Tudor Investment's multi-decade record is institutionally documented; the 1987 windfall contemporaneously reported; decades without a losing year. The *Trader* documentary corroborates his methods.

### Transferability
**The 200-day MA rule is the single cheapest, most robust market filter for this agent** — composable with O'Neil's M as a two-layer regime filter. 5:1 transfers as: require modeled reward ≥3–5× stop distance before entry. "Losers average losers" → a literal hard constraint. Defense-first sizing triple-converges with Minervini/Turtle governors — consensus doctrine.

---

## Ed Seykota & the Market Wizards Distillation

### Seykota's documented rules (*Market Wizards*, 1989)
- His five rules, verbatim: **(1) Cut losses. (2) Ride winners. (3) Keep bets small. (4) Follow the rules without question. (5) Know when to break the rules.** (The important ones are the first three.)
- **"The elements of good trading are: (1) cutting losses, (2) cutting losses, and (3) cutting losses."**
- Systematic trend-follower — built one of the first computerized trading systems (punch cards, late 1960s); risk ~1–2%/trade; pyramids winners; exits on trend reversal, no targets.
- "The key to long-term survival and prosperity has a lot to do with the money management techniques incorporated into the technical system."

### Record vs. myth — Grade B
Schwager reports a model account +250,000% over 16 years — statements seen by Schwager, never publicly audited; single-best-account selection risk. His mentorship lineage (Marcus → Kovner) is well documented.

### The recurring principles across ALL Market Wizards interviews (Schwager's synthesis)
Methodology-independent traits shared by every wizard:
1. **Rigid risk control / cut losses fast** — universal, zero exceptions across ~60+ interviews.
2. **Let winners run** — asymmetry matters more than accuracy; most win well under 50%.
3. **Position sizing as the survival variable** — Kovner: "undertrade, undertrade, undertrade."
4. **A defined edge + a method that fits your personality.**
5. **Discipline > prediction** — the losses come from deviations.
6. **Patience** — (Rogers: "wait until there's money lying in the corner"); doing nothing is a position.
7. **Standardized drawdown response** — reduce, don't press; never revenge trade.
8. **Own your results** — mistakes (rule-breaks) are distinct from losses (statistical outcomes).

---

## The Consensus Rules
*(Where nearly all ten profiles independently agree — agent doctrine, hard policy.)*

1. **Cut losses fast, at a predefined level, without exception.** Zero dissent across ten profiles. → Every entry carries a stop recorded at entry (7–8% or 2-ATR, never wider than 10%); a breached stop is executed at the window it's detected, no re-litigation.
2. **Never average down. Never add to a losing position.** → A forbidden action in the agent's action space.
3. **Ride winners; exit on trailing evidence, not hope-born targets.** → Trail all winners mechanically; partial profits into strength permitted (Qullamaggie/O'Neil hybrid); full exits only on trailing-rule violation.
4. **Buy strength — new highs, breakouts from consolidations — not dips or "bargains."** Universal among the equity traders. → Entries require a breakout above defined resistance from a defined base, in an uptrend (Trend Template), ideally on above-average volume.
5. **Use a market-regime filter; be defensive or flat in downtrends.** → Two-layer filter: (a) SPY vs 200-day MA, (b) O'Neil distribution-day count / follow-through state. Below filter: no new breakout buys, smaller sizes, cash is default.
6. **Expect a low win rate; make the math work through asymmetry.** → Track avg-win/avg-loss weekly; require prospective reward ≥2–3× risk at entry; judge on expectancy, never recent hit rate.
7. **Size down after losses; size up only when working.** → After account drawdown >5%, halve new-position risk; restore on new equity highs.
8. **The rules only work if followed — deviation, not the market, is the destroyer.** Livermore's arc, Druckenmiller's 2000 buy, Seykota's rule 4. → The historically fatal failure mode is *narrative override of mechanical rules*. Stop execution and no-averaging-down are non-overridable; the weekly session audits every plan-vs-action deviation.

## Where They Disagree

- **Profit-taking vs. pure trailing.** O'Neil: bank most at +20–25% (8-week monster exception); Turtles/Seykota/Darvas: never take profits on strength, only trail violations. Qullamaggie splits (⅓–½ into strength, trail the rest). *The hybrid is the right default for a small account that can't wait for one 10-bagger a year.*
- **Concentration vs. unit diversification.** Druckenmiller/Soros/Darvas/Livermore: bet huge on extreme conviction. Turtles/Seykota/Kovner: many small normalized units. *The 25% cap imposes the Turtle side; within it, adopt conviction tiering — 25% is earned by A-grade setups only.*
- **Fundamentals required vs. price-only.** O'Neil/Minervini: earnings acceleration is half the edge. Turtles/Zanger/Qullamaggie: price and volume suffice. *Use fundamental screens when data is available, but never let a good story excuse a bad chart.*
- **Mechanical vs. discretionary regime reading.** Turtles: take every signal, no opinion. PTJ/Druckenmiller/O'Neil: exposure override is the whole job. *For an LLM, mechanical wins — the agent's comparative advantage is tireless rule-following; its weakness is plausible-narrative override. Encode regime as rules, not vibes.*
- **Buy-window timing.** Zanger/Qullamaggie enter intraday at breakout; O'Neil warns off the first 30–45 minutes; Darvas/Turtles used standing orders. *Governs the 9:45 vs 3:30 choice.*
- **Pyramiding.** Livermore/Turtles/Darvas pyramid; O'Neil small follow-ons only; Qullamaggie mostly full-size. Low-stakes: pyramiding optional, averaging *down* is not.

## Transferability Map (2 decisions/day, long-only, $5k, fractional shares, 25% cap)

**Transfers cleanly (adopt as core system):**
- Minervini Trend Template (all 8 criteria) as the candidate filter — pure daily-OHLCV math.
- O'Neil M-filter + PTJ 200-day MA as the two-layer regime switch — computable at 3:30.
- Breakout-from-base entries (Darvas box / O'Neil pivot / VCP proxies) on daily closes at 3:30, or gap/EP entries at 9:45.
- 7–8% (max 10%) or 2-ATR stops checked at both windows; ATR-normalized sizing (risk 0.5–1% of equity per trade); fractional shares make this exact.
- Qullamaggie exit engine: partial into strength day 3–5; trail on 10/20-day MA closes.
- Turtle drawdown governor and correlation cap (max ~4 positions; no two positions that are "the same trade").
- Darvas's operating cadence — the existence proof that this agent's cadence can catch major trends.
- PTJ/Druckenmiller meta-rules: no averaging down (hard constraint), asymmetry accounting weekly, cash-when-confused, conviction-tiered sizing.

**Transfers with modification:**
- Donchian 20/55-day breakouts → close-basis versions; slightly later entries/exits.
- Qullamaggie ORH entries → crude "ORH-15" at 9:45 for EPs/gaps only; day-low stops widened to prior-day low or 2-ATR; overnight gap-through risk is borne, so cap single-position risk.
- Pyramiding → total pyramided position ≤25%.
- O'Neil fundamental letters → weekly session work; degrade gracefully to the technical subset if data is thin.

**Does not transfer (excluded):**
- All short-side rules (Livermore raids, parabolic shorts, macro shorts, Turtle shorts).
- Margin/leverage (Zanger's run, Turtle futures leverage) — expectations must be de-levered accordingly.
- Intraday tape-reading, sub-daily reversals, macro instruments.
- **Seykota's rule 5 ("know when to break the rules"): for an autonomous LLM, rule-breaking discretion is the documented death mode. The agent gets rules 1–4 only.**

**Net design implication:** the historical evidence most strongly supports an agent that is *Darvas in cadence, Minervini/O'Neil in selection, Turtle in sizing and risk governance, Qullamaggie in exits, and PTJ/O'Neil in regime filtering* — with Livermore and Druckenmiller-2000 installed not as methods but as the permanent warning label against narrative override.

## Sources

- The Original Turtle Trading Rules (PDF): https://oxfordstrat.com/coasdfASD32/uploads/2016/01/turtle-rules.pdf
- Turtle summaries: https://alchemymarkets.com/education/strategies/turtle-trading-guide/ ; https://www.quantifiedstrategies.com/donchian-channel/
- Minervini Trend Template: https://deepvue.com/screener/minervini-trend-template/ ; https://www.chartmill.com/documentation/stock-screener/technical-analysis-trading-strategies/496-Mark-Minervini-Trend-Template-A-Step-by-Step-Guide-for-Beginners
- Books (primary): *Reminiscences of a Stock Operator*; *How to Trade in Stocks*; *How I Made $2,000,000 in the Stock Market*; *How to Make Money in Stocks* (4th ed.); *Trade Like a Stock Market Wizard*; *Think & Trade Like a Champion*; *Way of the Turtle*; *The Complete TurtleTrader*; *Market Wizards* series; *The Alchemy of Finance*; *Money: Master the Game* (PTJ interview).
- Zanger verification: https://www.stockbrokers.com/education/dan-zanger-review-world-record-returns ; https://www.chartpattern.com/about.cfm ; https://optionstradingiq.com/dan-zanger/
- Darvas controversy: https://www.anylaw.com/case/matter-attorney-general-state-new-york-nicolas-darvas-and-american-research-council/new-york-supreme-court/12-30-1960/U7pjVWYBTlTomsSBSS0S ; https://law.justia.com/cases/new-york/court-of-appeals/1961/10-n-y-2d-108-0.html ; https://www.quantifiedstrategies.com/nicolas-darvas/
- O'Neil sell rules: https://medium.com/@socialmedia_96459/selling-right-how-oneil-mastered-selling-4d5b7770119e ; https://www.tradingwithrayner.com/23-trading-rules-by-william-j-oneil/
- Qullamaggie: https://www.kristjankullamagi.com/ ; https://timelessmarkettheory.com/traders/kristjan-qullamaggie ; https://letters.statsedgetrading.com/p/he-turned-5000-into-100-million-his
- Paul Tudor Jones: https://mebfaber.com/2014/11/06/paul-tudor-jones-on-the-200-day-moving-average/ ; https://www.turtletrader.com/trader-jones/ ; https://traderlion.com/quotes/paul-tudor-jones-quotes/
- Druckenmiller/Soros: https://tradebytrade.substack.com/p/druckenmillers-philosophy-on-position ; https://focusdst.com/layers-of-conviction-soros-and-druckenmiller-shorting-the-pound/ ; https://completetradersedge.com/stanley-druckenmiller-trading-record-2/
- Seykota: https://dailypriceaction.com/blog/ed-seykota/ ; https://www.daytrading.com/ed-seykota ; https://www.tradingwithrayner.com/ed-seykota-trading-lessons/
