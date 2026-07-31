# Trade Execution Quality for a Small Autonomous Trading Agent

**Context assumed throughout:** $5,000 Alpaca paper account, long-only US stocks/ETFs, fractional shares, positions ~$500–1,250, decisions only at 9:45 AM and 3:30 PM ET.
**Evidence grades:** A = peer-reviewed academic / exchange / regulator / broker primary docs; B = credible industry data, SSRN working papers, vendor research; C = practitioner sources, unverified.

---

## Order-type policy for the agent (concrete rules)

### The economics at this size

At $500–1,250 per position, execution cost is **entirely spread cost; market impact is zero**. A $1,250 order in a stock trading $50M+/day is <0.0025% of daily volume.

Quantified spread costs (A/B):
- **SPY:** average spread ~0.3 bps ($0.01 wide). Half-spread cost of a market order on $1,250: **~$0.02–0.06**.
- **Liquid mega caps:** ~1–5 bps quoted; half-spread cost: **$0.06–0.31**. Typical large caps: ≤15 bps.
- **Small caps:** routinely 50–500+ bps. A 200 bps spread costs ~$12.50 per round trip on $1,250 — 1% of the position, often exceeding the expected edge. Average spread across all ~2,900 US-listed ETPs is 0.52% — most ETFs are *not* SPY.

### Adverse selection: why resting limit orders are a trap for this agent

- A standing limit order is a **free option written to the market** (Copeland & Galai 1983, A). It fills preferentially when it is wrong: your buy limit at $99.50 fills exactly when news pushes fair value through it, and doesn't fill when the stock runs without you. Picking-off risk rises with volatility, time in book, and **lack of monitoring** — this agent is unmonitored ~5.75 hours between checks and ~17.75 hours overnight.
- Harris & Hasbrouck 1996 (A): limit orders at/inside the quote had lower ex-post cost than marketable orders — but netting fills only; the cost of *non-execution* reverses much of the advantage for momentum-style entries.
- Anand, Samadi & Sokobin, "Retail Limit Orders," Review of Finance 2025 (A): **retail resting limit orders suffer higher adverse-selection costs than institutional ones** — picked off by faster traders, not actively monitored. Monitoring is the documented mitigant — precisely what a twice-daily agent lacks.
- Offsetting: live retail marketable orders get wholesaler **price improvement inside the NBBO**, so realized cost is usually *less* than half the quoted spread. (Paper trading simulates none of this.)

### Concrete rule set

1. **Default entry order: marketable limit, DAY.** Buy limit = current ask + max(1–2 cents, ~5 bps). Behaves like a market order normally but caps damage from a stale/crossed quote or a mini flash move. Never a plain market order in anything with spread > 5 bps.
2. **Plain market orders acceptable only** in names with spread < 5 bps and ADV > ~$100M (SPY/QQQ-class, mega caps), during RTH, never 9:30–9:40.
3. **Never leave a non-marketable buy limit resting between decision windows.** If the entry isn't worth the current ask, skip and re-evaluate next window. All entry orders DAY; cancel any unfilled entry at the next run before re-deciding.
4. **GTC is reserved for protective exits only** (stop-loss legs, bracket take-profit legs). Alpaca auto-cancels GTC after 90 days; re-verify open orders every run. Cancel-and-replace exits rather than stacking (wash-trade section).
5. **Liquidity floor:** no names with quoted spread > 20 bps at decision time, price < $5, or ADV < ~$20M notional.
6. **Sub-penny rule:** limit prices ≥ $1.00 → 2 decimals; < $1.00 → 4 decimals.
7. **Exits in liquid names:** marketable limit = bid − 1–2 cents. For end-of-day exits, prefer the closing auction (LOC/CLS) if enabled.

---

## Time-of-day execution

### Documented intraday spread pattern

- **Reverse-J / U-shape (A):** McInish & Wood (JF 1992): NYSE minute-by-minute spreads widest at 9:30, decaying steeply over the first 15–60 minutes, tightest through midday/afternoon, modest uptick in the final minutes. Nasdaq studies find spreads narrowing into the close. Volatility follows the same U-shape.
- **Implications:**
  - **9:45 AM** is past the worst of the open, but spreads/volatility still ~1.5–3x midday in large caps and far worse in small caps. Acceptable for large caps with marketable limits; **do not enter small/mid caps at 9:45**.
  - **3:30 PM** is statistically the *better* execution window: spreads near daily tights, deepest continuous-book liquidity, before auction cutoffs. Prefer 3:30 for anything under ~$100M ADV and for all non-urgent exits.

### Auctions and MOC/LOC

- The closing auction is the **single deepest liquidity event of the day** (~10–15% of daily volume; B). Executing there means the benchmark price with ~zero spread cost at retail size.
- **Cutoffs:** NYSE MOC/LOC by **3:50 PM**; Nasdaq MOC 3:55, LOC 3:58 (A). The 3:30 run has comfortable margin.
- **Alpaca support:** TIF **`cls`** (MOC/LOC) and **`opg`** (MOO/LOO) exist in API v2 — but the docs flag OPG/CLS as *requiring sales-team approval*, and they are **whole-share only**. Verify in the paper account before building the LOC workflow; fallback is a 3:30 marketable limit.
- **Rule:** for planned end-of-day entries/exits in whole shares, submit **LOC** (limit ~10–20 bps through the 3:30 price) at the 3:30 run. LOC over MOC in single names to cap auction-imbalance surprises.

---

## Alpaca-specific mechanics + paper-vs-live caveats

All grade A (docs.alpaca.markets) unless noted.

### Order classes and constraints

- **Order types:** market, limit, stop, stop-limit, trailing stop. TIF: DAY, GTC (90-day auto-cancel), OPG, CLS, IOC, FOK (last four whole-share, may need approval).
- **Bracket** (`order_class: "bracket"`): entry + take-profit (limit) + stop-loss; once one exit fills, the other cancels. TIF DAY or GTC. **Extended hours not supported** for brackets. **OCO** = two linked exit orders; **OTO** = entry + one exit.
- **Bracket/OCO do NOT support fractional/notional quantities.** Policy: size positions as **whole shares rounded down from the dollar target** whenever a bracket is wanted. Fractional-only positions must have exits managed manually at decision windows (fractional supports plain stop/stop-limit DAY orders, but DAY stops die at 4:00 PM, leaving the position unprotected overnight until re-placed). **Strong argument for preferring whole-share brackets over fractional convenience.**
- **Stops do not protect outside RTH:** stop, stop-limit, and trailing-stop orders **only trigger during 9:30–4:00 ET**. Extended-hours sessions accept *only* DAY/GTC limit orders (whole shares, `extended_hours: true`). A GTC stop held overnight does nothing until 9:30; if the stock gaps through it, the stop converts to a market order at the gapped price. **Stop-losses bound intraday losses only; overnight/weekend gap risk is bounded only by position size.**
- **Wash-trade rejections:** Alpaca rejects (HTTP 403 "potential wash trade detected") any order that could interact with your own opposite-side open order — the classic trigger is separately placing a stop *and* a limit exit for the same position. **Bracket, OCO, and trailing-stop are the sanctioned exceptions.** Rules: (1) always use native bracket/OCO for dual exits; (2) before any new order in a symbol, list open orders and cancel conflicts first (confirm the cancel before the new submit).
- **Fractional matrix:** market/limit/stop/stop-limit, **DAY only**, 9-decimal qty or $1-min notional; `qty` and `notional` mutually exclusive; **notional orders cannot be replaced** (cancel and re-submit).

### Paper-trading fill simulation — what to distrust

- Fills simulate against the **NBBO of its data feed**; paper-only accounts use **IEX only** (~2% of consolidated volume) — quotes can be wider, thinner, staler than the SIP NBBO.
- **No queue position:** a non-marketable limit fills as soon as the quote *touches* it. Live, touching ≠ fill. **Paper systematically overstates passive-limit fill rates** — any edge that depends on resting-limit fills is inflated. (Marketable orders barely affected — another reason for the marketable-limit policy.)
- **Unlimited liquidity:** order quantity is not checked against NBBO size. Irrelevant at $1,250 in liquid names; badly misleading in small caps.
- **Randomized partial fills:** 10% of eligible fills are deliberately partial — code must handle partial-fill states.
- **Not simulated:** latency slippage, market impact, queue, **price improvement**, regulatory fees, dividends. Net at this size: paper is mildly *pessimistic* for marketable orders in liquid names, substantially *optimistic* for passive limits and anything illiquid.
- **Trust calibration:** for the recommended policy (marketable limits, liquid names, $500–1,250), paper ≈ live within a few bps. Distrust paper for: passive-limit strategies, small caps, spread-capture, size above a few thousand dollars in thin names.

---

## Gap risk stats (the twice-daily trader's core tail risk)

- **Index/mega-ETF base rates (B):** SPY average absolute overnight gap ≈ **0.45%** (H1 2026); ~1 in 3 sessions opens ≥0.5% away. ~45% of 1–2% QQQ gaps fill intraday, ~30% for gaps ≥2%.
- **Single large caps:** ~2–3x the index (TSLA avg absolute overnight gap ≈ 1.05%). A material fraction of single-stock variance is realized overnight, when stops cannot trigger.
- **Earnings gaps (B):** typical implied moves ±5–8%; realized tails of 10–20% routine in growth names. A 15% overnight gap on a $1,250 position = −$187 = 3.75% of the account, and **no stop order would have helped**.
- **Small caps:** news/earnings gaps of 10–30% common; combined with 50–500 bps spreads at the open, small-cap overnight holds are the worst risk/cost combination available to this agent.
- **Weekend/holiday:** ~65 hours of news accrual vs ~17.5 overnight.
- **Policy implications:** (1) size every position so a 20% adverse gap is survivable; (2) **do not hold single names through scheduled earnings** — check the calendar at 3:30 and exit or skip; (3) stops are intraday tools; position size is the only true overnight risk control; (4) index/sector ETFs carry ~½–⅓ the gap risk of single names.

---

## V2 appendix — strategy families outside current guardrails

### Shorting
- **Alpaca:** margin account ≥$2,000 equity; ~5,000+ easy-to-borrow names with $0 borrow fees; HTB not generally available; no fractional shorts. (A)
- **Realities:** asymmetric payoff (bounded gain, unbounded loss); squeezes concentrate in the names retail wants to short; retail short sellers on average lose after borrow costs (B). At $5k, one 30% squeeze on a $1,250 short = −7.5% of equity plus margin mechanics.
- **Verdict:** highest architecture cost-to-edge ratio. If enabled: ETB-only, ETF-only, hard caps. Evidence retail-scale shorting adds alpha: **C**.

### Options
- **Two-sided evidence:** Index-level systematic selling has A-grade support — Cboe **BXM** ~11.8% vs 11.7% S&P over 18 years at ~⅔ the vol; **PUT** comparable returns at SD ~10% vs ~15% (Bondarenko 2019); engine is the vol risk premium (IV 19.3% vs RV 15.1%, 1990–2018). **But** Bauer, Cosemans & Eichholtz (JBF 2009, large retail dataset): most individual investors **lose substantially more on options than stocks** — poor timing + costs; motivations skew to gambling.
- **Small-account arithmetic:** covered calls need 100 shares (only sub-$50 stocks addressable at $5k → forced concentration). One CSP on a $40 stock ties up $4,000 (80% of the account). Defined-risk spreads fit the capital but frictions consume much of the $20–50 max profits at this size.
- **Verdict:** the only family with A-grade class-level evidence, but this account size sits exactly in the population Bauer et al. show loses. Feasible V2 pilot: **one** CSP or covered call on a broad ETF, never single names. Grade **B−**.

### Crypto via Alpaca
- **Mechanics (A):** 24/7 spot, ~20 coins, fractional, GTC/IOC only, paper supported. Fees: taker 0.25% + spread markup at low volume.
- **Interaction with a scheduled agent:** no overnight-gap discontinuity — a GTC stop-limit actually works at 3 AM Sunday, unlike equity stops. But the agent is blind 23.5 of 24 hours in a market moving 3–6% daily, and round-trip cost ≥ ~50 bps is ~50–100x SPY. Must be low-frequency (days–weeks) or fee drag dominates.
- **Verdict:** operationally easiest to lift, economically justified only for multi-day trend/rebalance logic. Grade **C**.

### True intraday (ORB)
- Zarattini & Aziz (2023, SSRN 4416622): 5-min opening-range breakout on QQQ 2016–2023, reported ~675–1,484% total vs 169% QQQ, Sharpe 1.12 — **assuming 4x leverage, $0.0005/share commissions, zero spread/slippage**, trading at 9:35 (the widest-spread window), with the short side contributing much of the alpha. No live track record. Transferability to long-only, unlevered, twice-daily: **C**.
- **Architecture gap:** requires a 9:35 decision (edge gone by 9:45), streaming bars, immediate stop management, shorts + leverage. A different system, not a parameter change. If pursued: first re-run long-only, unlevered, with realistic 9:35 spreads; expect headline numbers to shrink drastically.

---

## Sources

**Alpaca official (A):**
- Orders/TIF/order classes: https://docs.alpaca.markets/docs/orders-at-alpaca
- Fractional trading: https://docs.alpaca.markets/docs/fractional-trading
- Paper trading simulation: https://docs.alpaca.markets/docs/paper-trading
- User protection (wash trades): https://docs.alpaca.markets/us/docs/user-protection
- Margin & short selling: https://docs.alpaca.markets/us/docs/margin-and-short-selling
- ETB $0 borrow fees: https://alpaca.markets/blog/zero-borrow-fees-on-short-selling-etb-stock-shares-alpaca-trading-api/
- Crypto fees: https://docs.alpaca.markets/us/docs/crypto-fees

**Alpaca community (B/C, cross-checked):**
- Wash-trade 403: https://forum.alpaca.markets/t/apierror-potential-wash-trade-detected-use-complex-orders/13441
- Bracket + fractional unsupported: https://forum.alpaca.markets/t/bracket-order-with-fractional-shares/12027

**Microstructure / academic (A unless noted):**
- McInish & Wood (JF 1992): https://digitalcommons.memphis.edu/facpubs/11507/
- Chan, Christie & Schultz (Nasdaq): https://www.researchgate.net/publication/24103194
- Copeland & Galai lineage: https://arxiv.org/pdf/1610.00261
- Harris & Hasbrouck (1996): https://www.semanticscholar.org/paper/1becb7448d402476c8e94d4d9548dd11e91a7c31
- Anand, Samadi & Sokobin (RoF 2025): https://academic.oup.com/rof/article/30/2/459/8277182
- Bauer, Cosemans & Eichholtz (JBF 2009): https://papers.ssrn.com/sol3/papers.cfm?abstract_id=965810
- Bondarenko (Cboe 2019): https://cdn.cboe.com/resources/education/research_publications/PutWriteCBOE19_v14_by_Prof_Oleg_Bondarenko_as_of_June_14.pdf
- Zarattini & Aziz ORB: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4416622 ; https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4729284 ; CXO review: https://www.cxoadvisory.com/technical-trading/day-trading-with-an-opening-range-breakout-strategy/

**Exchange / auction / spread data (A/B):**
- NYSE auctions: https://www.nyse.com/publicdocs/nyse/markets/nyse/NYSE_Opening_and_Closing_Auctions_Fact_Sheet.pdf
- Nasdaq cross cutoffs: https://www.nasdaqtrader.com/content/technicalsupport/specifications/TradingProducts/openclosequickguide.pdf
- BMLL closing-auction share: https://www.bmlltech.com/news/market-insight/into-the-close-unpacking-u-s-closing-auction-dynamics-and-the-impact-of-the-russell-reconstitution
- SSGA SPY spreads: https://www.ssga.com/us/en/intermediary/insights/comparing-spy-and-splg-two-spdr-etfs-for-s-p-500-exposure
- ETF.com spread survey: https://www.etf.com/sections/news/etfs-highest-lowest-trading-spreads
- Overnight gaps: https://www.strasmore.com/blog/why-do-stocks-gap-overnight ; https://www.shareplanner.com/blog/strategies-for-trading/fading-the-gap-how-large-overnight-moves-in-spy-and-qqq-play-out-during-the-trading-day.html
- Earnings implied moves: https://earnings-watcher.com/wiki/earnings-expected-moves ; https://orats.com/university/volatility-around-earnings

**Caveats:** (1) OPG/CLS "sales-team approval" — test CLS in the paper account before building the LOC workflow; (2) the SPY 0.45% / TSLA 1.05% gap figures are grade B/C — re-derive from the agent's own daily-bar data if precision matters; (3) fractional GTC support has changed over time — docs currently say DAY-only, which this policy assumes.
