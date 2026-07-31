# LLM Agents as Traders: What the Research Actually Says (2023–2026)

Evidence grades: **A** = peer-reviewed venue or live/real-market data with verifiable results; **B** = arXiv preprint, single-run backtest, plausible methodology; **C** = informal/public experiment, small sample, or contested methodology.

---

## StockBench (arXiv 2510.02209, Oct 2025) — Grade B+ (contamination-controlled, single 4-month window)

**Setup.** Contamination-free benchmark: agents trade the top ~20 DJIA stocks with $100K, daily buy/sell/hold decisions from prices, fundamentals, and news, March–June 2025 (post-training-cutoff data). Metrics: cumulative return, max drawdown, Sortino.

**Results (final return / max DD / Sortino):**

| Model | Return | Max DD | Sortino |
|---|---|---|---|
| Kimi-K2 | +1.9% | −11.8% | 0.0420 |
| Qwen3-235B-Ins | +2.4% | −11.2% | 0.0299 |
| GLM-4.5 | +2.3% | −13.7% | 0.0295 |
| Qwen3-235B-Think | +2.5% | −14.9% | 0.0309 |
| OpenAI o3 | +1.9% | −13.2% | 0.0267 |
| Claude-4-Sonnet | +2.2% | −14.2% | 0.0245 |
| **Buy-and-hold baseline** | **+0.4%** | **−15.2%** | **0.0155** |
| GPT-5 | +0.3% | −13.1% | 0.0132 |
| GPT-OSS-120B | −0.9% | −14.0% | — |
| GPT-OSS-20B | −2.8% | −14.4% | −0.0069 |

**What separated winners:** not stock-picking brilliance but **drawdown control** — winners limited max DD to −11–12% vs the baseline's −15.2%. Absolute edges over buy-and-hold were tiny (~1–2pp over 4 months).

**Key failure findings:**
- **Regime asymmetry:** during the downturn sub-period, *every* LLM agent underperformed passive; in the upturn, most beat it. LLM "alpha" was mostly loss-mitigation, not selection.
- **Execution errors:** arithmetic errors in share-count calculations; schema errors — reasoning-tuned models had *more* schema errors from overthinking.
- **Scalability cliff:** beyond ~20 assets, mean returns decline and volatility rises.
- Static financial QA skill did not predict trading skill (GPT-5 near-bottom despite benchmark strength).

---

## When Agents Trade / Agent Market Arena (arXiv 2510.11695; WWW 2026) — Grade A− (live, real-time; short window, 4 assets)

**Setup.** Live trading Aug–Sep 2025 on BTC, ETH, TSLA, BMRN. Four architectures — InvestorAgent (single agent + memory), TradeAgent (multi-analyst), HedgeFundAgent (persona team), DeepFundAgent (streaming memory) — each across 5 backbones (GPT-4o, GPT-4.1, Claude-3.5-Haiku, Claude-Sonnet-4, Gemini-2.0-Flash).

**Results.** Huge dispersion by *architecture*, modest by *backbone*: InvestorAgent+GPT-4.1 +40.8% on TSLA (Sharpe 6.47); HedgeFundAgent +39.7% on ETH but **large losses on TSLA and BTC** — same architecture, different asset, opposite outcome. DeepFundAgent was steadiest (+8.6% TSLA, +9.5% BMRN).

**Takeaways:** (1) **Agent architecture (memory, workflow, risk style) dominates LLM backbone choice.** (2) All agents struggled with **abrupt macro reversals**. (3) **Strategy–asset mismatch** is a first-order risk.

---

## StockAgent (arXiv 2407.18957, 2024) — Grade B (simulation)

200 LLM agents trading simulated stocks. **Model personality is real and large:** GPT agents traded less frequently in larger size, bullish; Gemini agents bearish, high-frequency, **herded strongly**. **Information ablations had perverse effects:** removing the discussion board depressed prices (peer chatter moves LLM valuations — sycophancy to social signal); removing earnings reports *flipped many agents from loss to profit* (more information ≠ better decisions; news can be a contaminant).

## TradingAgents (arXiv 2412.20138) — Grade B− (spectacular numbers, weak protocol)

Firm-like multi-agent org: analysts, bull-vs-bear researcher **debate**, trader, risk desk. Reported 23–27% returns, Sharpe 5.6–8.2 — but a 3-month bull-period backtest **inside the models' training window** (Profit Mirage's leakage critique applies squarely). Treat the *architecture ideas* (debate, explicit risk desk) as transferable, not the returns.

## FinMem (arXiv 2311.13743) / FinAgent (KDD '24) — Grade B, downgraded by leakage

Layered memory + dual-level reflection; FinAgent reported +36% average improvement over 9 baselines. Canonical evidence that **memory + reflection is the highest-leverage single-agent intervention** — but see Profit Mirage.

## Profit Mirage (arXiv 2510.07920) — Grade B+, the essential corrective

Re-tested LLM financial agents across knowledge-cutoff boundaries: **strong performance inside the training window collapses substantially on post-cutoff data** — much of the published "alpha" is memorization/information leakage. **Distrust any LLM-trading backtest whose test period predates the model's cutoff — which is most of the famous ones.** StockBench and AMA (post-cutoff/live) are the trustworthy datapoints: ~1–2pp edges, not 20%+.

---

## Rebalancing frequency — Grade C→B (two studies, consistent on one point)

1. **Agent4Science (GPT-4.1-mini, 5 stocks, 2023–24):** **weekly Sharpe 1.028 > daily 0.892 (+15%) > monthly 0.421.** But no LLM configuration beat buy-and-hold (Sharpe 1.620) in that bull market.
2. **ChatGPT in Systematic Investing (arXiv 2510.26228):** monthly (Sharpe ~1.1) beat weekly (~0.7), via lower turnover.

**Consistent conclusion:** *more frequent LLM decision-making does not add alpha and usually subtracts it.* Daily is the worst tested frequency in both. The optimum (weekly vs monthly) is unsettled; "less often than daily" is well-supported.

---

## Experimental asset markets (arXiv 2502.15800) — Grade B+ (the "discipline edge" evidence)

Classic Smith bubble experiments rerun with LLM traders: humans reliably blow bubbles; **LLM-only markets trade near fundamental value** (Claude-3.5-Sonnet price-deviation MSE **0.54 vs ~430 for humans**). LLMs showed no overconfidence-driven bubbles. But: **very low strategy variance — LLM agents converge on similar decisions** → crowding risk, no diversification vs other LLM-informed traders.

## Elm Wealth "Crystal Ball" (2025) — Grade B — the position-sizing indictment

Claude, ChatGPT, Gemini, Grok got tomorrow's WSJ front page (15 events) and traded S&P/Treasuries vs 120 finance-trained humans. **Direction: good** — Claude averaged $2.59M ending wealth (60.7% hit rate), beating humans in 76% of matchups. **Sizing: terrible** — all models ran 7–12x leverage against a moderate-risk mandate; **all knew Kelly principles when quizzed but failed to apply them when trading**. Explicit risk guidance injected into context substantially improved calibration. **Position sizing must be imposed externally, never left to the model.**

## Public experiments — Grade C (uncontrolled but instructive)

- **AI Trade Arena (8 months, $100K paper):** Grok 4 +56%, DeepSeek +49%, GPT-5 ≈ +27%, Claude Sonnet 4.5 ≈ +27%, Gemini 2.5 Pro **−9.5%**. Outcomes dominated by one sector-allocation decision, not daily skill; 65pp dispersion across identical setups.
- **Nof1 Alpha Arena S1 (2 weeks, $10K real, crypto perps):** Qwen3-Max +23%; **Claude Sonnet 4.5 −31%, Grok 4 −45%, Gemini −57%, GPT-5 −63%.** Losers over-leveraged and overtraded. Grok won one arena and lost the other — **cross-experiment model rankings do not replicate; bet on structure, not backbone identity.** Leveraged/intraday environments are where LLMs get destroyed.

## Robustness studies — Grade B

- **TradeTrap (arXiv 2512.02261):** small single-component perturbations propagate into extreme concentration, runaway exposure, large drawdowns; injected fake data triggers panic cascades; prompt injection can force liquidations. **LLM agents have no intrinsic circuit breakers — sanity checks must live outside the model.**
- **TrustTrade:** **identical market conditions frequently produce divergent decisions across runs**; consensus filtering (act only on agreement) pulls behavior toward a stable mid-risk profile.
- **Agentic Trading survey (arXiv 2605.19337):** of 19 primary studies, **0/19 fully reproducible, 2/19 time-consistent splits, 1/19 model transaction costs**. Headline numbers are systematically overstated.

## Lopez-Lira & Tang (arXiv 2304.07619) — Grade A− (the edge-existence evidence)

GPT-4 headline scoring: ~90% hit on the (non-tradable) initial reaction, and **significant prediction of subsequent drift — concentrated in small-cap stocks and negative news**. Capability scales with model size. **Documented strategy returns decline as LLM adoption rises** — the edge is real but self-eroding. Combined with microstructure evidence (macro news impounded in ~5–10 min; large-cap PEAD ≈ 0 since ~2006): an LLM reading headlines twice a day has **zero edge on the initial move in liquid large caps**, and a **narrow, decaying edge on multi-day drift in smaller/complex/negative-news situations**.

---

## Failure-mode catalog

| # | Failure mode | Evidence | Source |
|---|---|---|---|
| 1 | Overtrading / daily noise-chasing | Daily Sharpe 0.892 < weekly 1.028; monthly > weekly | Agent4Science; 2510.26228 |
| 2 | Position-size incoherence | All 4 frontier models used 7–12x leverage vs mandate | Elm Wealth |
| 3 | Bear-market failure | ALL agents underperformed passive in the downturn leg | StockBench; AMA |
| 4 | Run-to-run inconsistency | Identical conditions → divergent decisions | TrustTrade; arenas |
| 5 | Arithmetic & schema errors | Miscomputed share counts; broken JSON | StockBench |
| 6 | Sycophancy to social/news flow | BBS chatter moved valuations; removing news *improved* P&L | StockAgent |
| 7 | Hallucination/leakage confidence | Backtest alpha collapses post-cutoff | Profit Mirage |
| 8 | Fragility to bad/injected data | One perturbed component → panic cascades | TradeTrap |
| 9 | Strategy–asset mismatch | Contrarian persona: +40% on ETH, ruinous on TSLA | AMA |
| 10 | Universe overload | >20 assets → falling returns, rising vol | StockBench |
| 11 | Crowding / low strategy variance | LLM agents converge to near-identical decisions | 2502.15800; Lopez-Lira |
| 12 | Leverage/fast-market destruction | −31% to −63% in 2 weeks on leveraged perps | Alpha Arena |
| 13 | Sector bet masquerading as skill | 8-month outcomes decided by one allocation | AI Trade Arena |

Note: "inability to sit in cash" is *not* strongly documented as universal — the failure is better characterized as **action bias under news flow + aggressive sizing**.

## Interventions that measurably helped

1. **Architecture over backbone** (A-grade, AMA): spend effort on the loop, not model shopping.
2. **Memory + dual-level reflection** (FinAgent/FinMem/DeepFundAgent's live consistency).
3. **Explicit risk rules in context** (Elm Wealth): cheapest known fix for sizing incoherence.
4. **Drawdown-first framing** (StockBench): the winners' entire margin was loss-mitigation.
5. **Cross-run consensus / self-consistency** (TrustTrade): act only on agreement; deterministic anchors stabilize outputs.
6. **Bull/bear adversarial debate + separate risk desk** (TradingAgents): promising-unproven (B−).
7. **Lower decision frequency**: weekly-or-slower beats daily on Sharpe.
8. **Small fixed universe** (≤20 candidates).
9. **Structured output + external validation**: never let the model compute share counts unchecked.

## The realistic edge

**No edge (structural):** initial reaction to news in liquid large caps (priced in minutes); anything intraday; anything leveraged or fast. Reacting to a headline 6 hours later in AAPL is trading on fully priced information.

**Narrow, real edge documented:** (a) multi-day drift after complex/negative news in smaller caps (decaying with LLM adoption); (b) breadth of synthesis — catching slow-diffusion, hard-to-process news; (c) **behavioral discipline** — LLMs demonstrably don't bubble or panic; the durable "edge" for a $5K account is really *avoiding human error*: no FOMO, no panic selling, systematic loss-cutting; (d) consistency of process. **Honest expectation from post-cutoff evidence: roughly market returns ±2pp with better drawdowns**, not the +20% of leakage-era backtests.

## Design prescriptions for our agent

1. **Make HOLD the default; force an explicit "why not hold?" evaluation before any trade.** Require the agent to state what buy-and-hold would do and beat it in expectation before trading.
2. **Concentrate real decisions in the weekly session; make the twice-daily sessions monitoring-first** (exit triggers, stop conditions, flagging candidates for Sunday).
3. **Never let the model choose position size freely.** Hard-code caps; restate limits every run; validate sizes in code, not prompt.
4. **Compute share quantities and cash math outside the LLM.** The agent outputs target dollar amounts; code converts and rejects infeasible orders.
5. **Cap the active universe at ~15–20 tickers.**
6. **Prompt for drawdown-first, not return-first.** Decision format requires: thesis, downside scenario, exit condition, portfolio drawdown impact before entry.
7. **Install a regime guard** (SPY vs 200-day, VIX level); in risk-off regimes, tighten the trade bar and allow larger cash allocation.
8. **Don't trade the last 12 hours' news in large caps.** Frame news as thesis input for multi-day/multi-week positions; reserve news-reaction trades for slow-diffusion cases (complex filings, small/mid caps, negative-news drift).
9. **Use self-consistency before acting:** morning-session flag → afternoon-session confirm for non-urgent buys; low temperature; restate deterministic anchors (date, prices, positions) at the top of every prompt.
10. **Maintain a trade journal + reflection memory and feed it back** — but **embargo outcomes**: journal what was known at decision time; reflections must not retroactively import later information as foreseeable.
11. **Mandatory bear-case step:** before any buy, generate the strongest argument against the trade and explain why it fails.
12. **Force benchmarking weekly:** portfolio vs SPY since inception and trailing month; explicitly justify continued active management of any underperforming thesis.
13. **Sanity-gate all inputs:** cross-check any extraordinary claim (>10% move, shock headline) against a second source; treat unverifiable claims as absent.
14. **Distrust memorized price history.** Reason only from supplied current data, never from recalled prices — pre-cutoff "knowledge" is memorization.
15. **Set expectations in the system prompt:** the documented realistic goal is *match the market with smaller drawdowns plus occasional small alpha from slow-diffusion news*. An agent prompted to "maximize returns" is the one that ends up at 12x leverage or −63%; an agent prompted to protect capital first is the one that beat buy-and-hold in StockBench.

## Sources

- StockBench: https://arxiv.org/abs/2510.02209 ; https://stockbench.github.io/
- Agent Market Arena: https://arxiv.org/abs/2510.11695 ; https://dl.acm.org/doi/10.1145/3774904.3792821
- StockAgent: https://arxiv.org/abs/2407.18957
- TradingAgents: https://arxiv.org/abs/2412.20138
- FinMem: https://arxiv.org/abs/2311.13743 ; FinAgent: https://arxiv.org/abs/2402.18485
- Profit Mirage: https://arxiv.org/pdf/2510.07920
- Rebalancing: https://agent4science.org/peerreview/review_mnyhrsavcqylzr4d ; https://arxiv.org/html/2510.26228v1
- Experimental asset markets: https://arxiv.org/html/2502.15800v2
- Elm Wealth Crystal Ball: https://elmwealth.com/ai-trading/
- AI Trade Arena: https://www.aitradearena.com/research/we-ran-llms-for-8-months
- Alpha Arena: https://protos.com/llm-crypto-trading-contest-finds-llms-cant-trade-crypto/ ; https://www.iweaver.ai/blog/alpha-arena-ai-trading-season-1-results/
- Lopez-Lira & Tang: https://arxiv.org/abs/2304.07619 ; https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4412788
- TradeTrap: https://arxiv.org/abs/2512.02261 ; TrustTrade: https://arxiv.org/abs/2603.22567
- Agentic Trading survey: https://arxiv.org/html/2605.19337v1
- Price-discovery speed: https://www.nber.org/system/files/working_papers/w11312/w11312.pdf ; PEAD decay: https://www.sciencedirect.com/science/article/pii/S2214635020303750 ; https://klementoninvesting.substack.com/p/which-news-is-incorporated-slowly
