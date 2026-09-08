# Market Regime Judgment Framework — v1.0 (Draft)

- Date: 2026-09-08
- Status: **WORKING HYPOTHESIS — NOT YET VALIDATED**
- Scope: How the project defines, scores, and validates "market state," and how that state is combined with per-asset scores to produce buy intensity.
- Relationship to existing rules: this document does not replace the FX Buy Intensity rule (`CLAUDE_HANDOVER_2026-09-08.md` §6), the Portfolio Allocation staging rule (`PORTFOLIO_ALLOCATION_RULE_v0.1.md` §7), or the Stress Convergence three-state system (Early Warning / Tightening State / Crisis Confirmation). It specifies how a broader market-regime layer sits alongside them.

> **Governance note.** Every threshold, weight, and formula in this document is a **candidate for backtesting**, not a hard trading rule. Per `INVESTMENT_RESEARCH_LOOP.md`, nothing here may be treated as a decision rule until it has gone through Data → Threshold → Backtest → Falsification → Action, and no threshold may be tuned post hoc to fit historical results.

---

## 0. Why this document exists

Prior sessions established:

1. A single price/index move is not sufficient to call a market "risk-on" (`LESSONS_LEARNED_2026-09-08_MARKET_SESSION.md`: "AI/반도체 강세 ≠ broad risk-on").
2. Buy intensity must combine multiple axes, not one indicator (`Buy Intensity = Portfolio Gap × Asset Opportunity × Risk Gate × FX Benefit`).
3. Crisis-adjacent states must be separated into Early Warning / Tightening / Crisis Confirmation, and no state has yet been promoted to a standalone action rule.

What was missing is an explicit, falsifiable **market-state layer** that sits between raw market data and those existing decision rules, plus a validation protocol strict enough to avoid the failure mode this repository is designed to prevent: mistaking a fitted backtest for a working rule.

This framework formalizes that layer. It does not certify any of it as validated.

---

## 1. Indicator inventory (five axes)

Market state is defined as the joint condition of five axes, not any single series. No axis alone determines the regime.

| Axis | Purpose | Example series (candidates, not final) |
|---|---|---|
| A. Trend | Direction and structure of price over multiple horizons | 1D/5D/20D/60D/120D return, price vs. 20/60/200D MA, MA slope/ordering, drawdown from high |
| B. Breadth | Whether strength is broad-based or concentrated | advance/decline ratio, % of stocks above their MA, new-high/new-low ratio, advancing volume share, large-cap vs. small-cap dispersion |
| C. Volatility / Risk | Priced-in and realized risk | VIX (or local equivalent), realized volatility, ATR, max drawdown, credit spreads (IG/HY), option skew, vol term structure |
| D. Rates / Liquidity / Credit | Macro financial conditions | UST 2Y/10Y, 10Y-2Y **and** 10Y-3M slope (see §1.2 — the NY Fed's own official recession-probability model uses 10Y-3M, not 10Y-2Y), real yields, breakevens, policy-rate expectations, KR rates, dollar liquidity proxies, IG/HY spreads |
| E. Cross-asset flow | Whether risk-taking is internally consistent across assets | US equities/futures, USD index, USD/JPY, USD/KRW, oil, gold, semiconductors, KOSPI, crypto |

This axis set is deliberately the same shape as the project's existing practice of combining rate/oil/FX/breadth/relative-strength signals in the standard session checklist (`CLAUDE_HANDOVER_2026-09-08.md` §15); this document turns that checklist into a scored, versioned system.

### 1.1 Indicator selection discipline

- An indicator enters this framework as a **candidate** only. It is promoted to "in use" only after passing the validation stack in §10.
- Do not add an indicator solely because it improved a historical backtest fit (data-snooping guard, §10.9).
- Every candidate must have a stated economic mechanism (why it should matter) before any statistical test is run (`INVESTMENT_RESEARCH_LOOP.md` step 1).

### 1.2 Independent evidence check (2026-09-08 addendum)

The two prior sessions on this framework reviewed a research memo's claims and its citation quality (see `LESSONS_LEARNED_2026-09-08_DSR_PBO_SOURCE_REVIEW.md`). This addendum goes one step further: it runs this project's own independent searches for primary/institutional evidence behind each axis, rather than relying on either memo's citations. Findings (via WebSearch only — WebFetch to primary PDFs was blocked by this session's network policy for every domain tried, so exact formula/figure text below is not a verbatim PDF read and should be spot-checked when fetch access is available):

**Axis A — Trend.** Moskowitz, Ooi & Pedersen, "Time Series Momentum," *Journal of Financial Economics* (2012) — tested 58 futures/forward contracts (equity indices, currencies, commodities, sovereign bonds) over 25+ years; found consistent 1-12 month return persistence that partially reverses over longer horizons. This is a real, independently reproducible academic result, not a marketing claim, and it directly supports using **multiple lookback horizons together** (this framework's 1D/5D/20D/60D/120D set) rather than one fixed window — but note the original paper studied futures on indices/FX/commodities/bonds, not individual equities or a composite index-level "market score" as proposed here, so the transfer to this framework's Trend axis is still an assumption to test in §9, not an inherited result.

**Axis B — Breadth.** Zaremba, Szyszka, Karathanasopoulos & Mikutowski, "Herding for Profits: Market Breadth and the Cross-Section of Global Equity Returns," *Economic Modelling* (2019/2020) — market breadth (share of advancing vs. declining stocks) is reported as a robust predictor of future market/industry returns across 64 countries, 1973-2018, and the effect reportedly survives controls for size, style, volatility, skewness, momentum, and trend-following signals. This is materially stronger and more specific support for the Breadth axis than the illustrative KOSPI example in §0-era discussion; it is also a single (if broad) study and should not be treated as final until this project replicates the pattern on its own data (§9-§10).

**Axis C — Volatility/Risk.** Independent research on VIX-credit combinations reports a meaningfully positive VIX-to-credit-spread correlation and supports using both together (each captures different, only partly overlapping information) rather than either alone. Practitioner/academic volatility-regime studies commonly define a "stress" state using a percentile cut on realized/implied volatility (one cited example: the empirical 90th percentile of a volatility proxy) and a Z-score cut on credit spreads (one cited example: Z > 2.0). These are useful **starting points for the percentile-transform design in §4**, but — consistent with §10.2's treatment of the DSR/PBO thresholds — specific cut points like "90th percentile" or "Z > 2.0" are recorded here as candidates to recalibrate on this project's own data, not values to import directly.

**Axis D — Rates/Liquidity/Credit.** Two corrections/refinements from this check:
1. The New York Fed's own official recession-probability model (Estrella & Mishkin, 1996, published as NY Fed *Current Issues in Economics and Finance* and FRB research) uses the **10-year minus 3-month** Treasury spread, not 10Y-2Y, and reports that 10Y-3M has outperformed 10Y-2Y as a leading indicator in post-1980 cycles. This framework's axis table (§1) has been corrected to include 10Y-3M alongside 10Y-2Y rather than only 10Y-2Y.
2. The Federal Reserve Bank of Chicago's National Financial Conditions Index (NFCI) is a concrete, published example of exactly the multi-variable financial-conditions approach this framework's Rates/Liquidity/Credit axis is modeled on: it aggregates 105 weekly financial-activity series (grouped into risk, credit, and leverage categories) into one factor via a Dynamic Factor Model (Brave & Butters, Chicago Fed working paper 2010-02, updated 2014), normalized to mean 0 / SD 1 since 1971. This is a directly reusable **methodological template** for this axis's percentile/z-score transform (§4) and is a stronger anchor than the general "Fed combines multiple variables" claim in the earlier memo.

**Axis E — Cross-asset flow.** No single canonical academic paper was found defining a standardized "risk-on/risk-off cross-asset index" the way NFCI or the yield-curve model are canonical; this axis remains the least academically anchored of the five and should be prioritized for the project's own indicator-selection work in §12 P0 rather than assumed to already have a validated external template.

**Net effect on this framework:** Axes A, B, and D now have credible primary/institutional anchors; Axis C has partial anchoring with candidate (not final) thresholds; Axis E has the weakest external grounding and is flagged as higher-priority, higher-uncertainty work. None of this changes the framework's status — it is still WORKING HYPOTHESIS, not validated on this project's own data — but it replaces several previously vague claims with checkable citations, and it surfaces one concrete correction (10Y-3M vs. 10Y-2Y).

---

## 2. Data sources and provenance

Per the existing evidence hierarchy (`CLAUDE_HANDOVER_2026-09-08.md` §2), each series used in this framework must record:

1. Primary source tier (central bank/government/exchange data preferred; financial data vendors/Reuters-Bloomberg-tier next; aggregail commentary lowest weight and hypothesis-only).
2. Exact series definition (e.g., "CBOE VIX close" vs. "intraday level").
3. Update frequency (daily/weekly/monthly) and publication lag.
4. Historical availability window (how far back the series is usable without gaps or methodology breaks).

No specific vendor/API is frozen in this document. Source selection is a separate P-item (§11) because it directly affects how far back backtesting (§9) and out-of-sample validation (§10) can go.

## 3. Update cadence

| Axis | Cadence | Rationale |
|---|---|---|
| Trend | Daily | Price data is daily-native |
| Breadth | Daily | Needed same-day as trend to detect divergence |
| Volatility/Risk | Daily (VIX/ATR), event-driven (credit spreads can lag) | Credit data often has T+1 lag |
| Rates/Liquidity | Daily (yields), weekly/monthly (policy-conditions composites) | Central bank data is not daily |
| Cross-asset | Daily | Needed for the session-close checklist already in use |

Market Regime (§6) is recomputed daily. It is not intended to be an intraday signal; this project's existing rules already reject same-day panic decisions (`LESSONS_LEARNED_2026-09-08_MARKET_SESSION.md`).

## 4. 0–100 score transform

Each axis produces a 0–100 sub-score before combination, to avoid mixing incompatible units (percent returns, index points, basis points) directly.

Candidate transform per series:

```
percentile_rank(x, trailing_window) -> 0-100
```

i.e., each raw series value is converted to its percentile rank within a trailing lookback window (candidate: 3-year rolling window, to be tested against fixed full-history percentiles in §10.6 sensitivity).

Rules for the transform itself (all falsifiable, not fixed):

- Use trailing, not full-sample, percentiles wherever a full-sample calculation would leak future information into a historical backtest point (look-ahead bias guard).
- Winsorize extreme tails (e.g., 1st/99th percentile) before ranking, to avoid a single historical outlier dominating the scale.
- Direction-normalize so 100 always means "more supportive of risk-taking" and 0 always means "less supportive," even for series where a rise is bearish (e.g., invert VIX and credit spreads before ranking).

Axis sub-score = average (or documented weighted average) of its component percentile scores. Component weights within an axis are themselves subject to §10.7 parameter-sensitivity testing.

### 4.1 Concrete candidate indicator construction (v0.1, 2026-09-08 addendum)

A follow-up memo proposed a fully worked-out version of §1 and §4: named component indicators per axis, an explicit sub-weight for each, and specific numeric cut points for the 0-100 transform. This is recorded here as the project's first **executable candidate specification** — concrete enough for §9's backtest code to implement directly — but with the same caveat applied throughout this document: **every numeric cut point below is an untested candidate, not a frozen rule**, and most of the memo's own citations for these cut points were SEO/blog-tier sources (profitma.com, mastermind-x.com, finwiz.io, deanfi.com, thetrading.tools, tapeboard.com, buildalpha.com, etc.), which sit below this project's evidence bar (`INVESTMENT_RESEARCH_LOOP.md` §2) and are not adopted as authority for the thresholds — only as a source of candidate starting values to calibrate away from in §10.6/§10.7. Where a cut point conflicts with the stronger academic/institutional anchors already recorded in §1.2, §1.2 takes precedence (see the 10Y-3M note under Axis D below).

**Axis A — Trend**

| Component | Definition | Candidate sub-weight |
|---|---|---|
| Short momentum | 5D, 20D return | 0.25 |
| Medium momentum | 60D, 120D return | 0.25 |
| Long trend | position vs. 200D MA, 200D MA slope | 0.25 |
| MA alignment | boolean: 20D > 60D > 200D | 0.15 |
| Drawdown from 52W high | (price - 52W high) / 52W high | 0.10 |

Candidate transform notes: MA alignment as a 3-tier step function (fully aligned up / partially aligned / fully aligned down) rather than a continuous percentile; drawdown as a step function (shallower drawdown scores higher). Both are simplifications of the general percentile-rank rule in §4 and must be tested against the continuous version in §10.6 rather than assumed superior.

**Axis B — Breadth**

| Component | Definition | Candidate sub-weight |
|---|---|---|
| Advance ratio | advancing / (advancing + declining) | 0.20 |
| Advance-Decline Ratio (ADR) | advancing count / declining count | 0.20 |
| New-high minus new-low (NH-NL) | 52W new highs - 52W new lows, trailing z-score | 0.20 |
| % above 200D MA | count above 200D MA / total | 0.25 |
| % above 50D MA | count above 50D MA / total | 0.15 |

This sub-weight split (25% to the 200D-MA breadth measure, the single largest component) is directionally consistent with the independently-verified breadth literature in §1.2 (Zaremba et al., 2019/2020) treating broad-based participation as the dominant breadth signal, but the specific split has not itself been tested by this project.

**Axis C — Volatility/Risk**

| Component | Definition | Candidate sub-weight |
|---|---|---|
| VIX level | index close | 0.25 |
| VIX term structure | VIX3M - VIX (contango positive / backwardation negative) | 0.15 |
| Realized volatility | 20D return std, annualized | 0.20 |
| Max drawdown | current drawdown from trailing high | 0.15 |
| Credit spread | HY OAS - IG OAS | 0.25 |

**Axis D — Rates/Liquidity/Credit**

| Component | Definition | Candidate sub-weight | Note |
|---|---|---|---|
| Yield-curve slope | 10Y-2Y **and** 10Y-3M | 0.25 | Per §1.2, the NY Fed's own official model uses 10Y-3M; a candidate scoring rule should not rely on 10Y-2Y alone the way the original follow-up memo did |
| Real yield | 10Y nominal - breakeven inflation | 0.20 | |
| Dollar (DXY) | trailing return | 0.20 | |
| HY credit spread | HY OAS level | 0.35 | Largest single sub-weight, consistent with credit spreads being one of the three NFCI categories (§1.2) |

**Axis E — Cross-asset flow**

| Component | Definition | Candidate sub-weight |
|---|---|---|
| US equities | S&P 500 20D return | 0.30 |
| US rates | 10Y yield 20D change | 0.15 |
| Dollar/KRW | USD/KRW 20D change (KRW strength scores higher, per the existing FX Benefit logic in `CLAUDE_HANDOVER_2026-09-08.md` §6) | 0.15 |
| Oil | WTI 20D change | 0.15 |
| Gold | Gold 20D change (direction-inverted: gold strength scores as *lower* risk appetite) | 0.10 |
| Semiconductors | SOX 20D return | 0.15 |

Per §1.2, Axis E has the weakest external methodological anchor of the five; this component/weight table is a starting candidate for the project's own P0 design work, not an imported validated model.

**Illustrative step-function cut points** (candidate only — e.g. VIX ≤ 18 → high sub-score, HY OAS ≤ 250bp → high sub-score, breadth ≥ 60% advancing → high sub-score, and their symmetric low-score counterparts) are a reasonable starting grid for implementing §4's percentile-rank transform in code, but must be replaced by this project's own trailing-percentile calculation (§4) once historical data is loaded — hardcoded absolute levels do not adapt across regimes or over multi-year drift the way a trailing percentile does, and are kept here only as a bootstrap default before real history exists.

## 5. Composite Market Score

```
Market Score (0-100)
= 0.25 x Trend
+ 0.20 x Breadth
+ 0.20 x Volatility/Risk
+ 0.20 x Rates/Liquidity/Credit
+ 0.15 x Cross-Asset
```

These weights are a **starting candidate**, not a fitted result. They must be tested against at least the sensitivity sweep in §10.7 before being treated as more than a placeholder.

### 5.1 Investment period weighting — Market Score vs. Stock Score

The project intentionally keeps stock-level scoring and market-level scoring separate (per this document's originating research memo), then blends them with different weights depending on holding horizon, because market conditions matter progressively more as horizon shortens:

| Horizon | Stock Score weight | Market Score weight |
|---|---:|---:|
| Long-term | 70% | 30% |
| Mid-term | 60% | 40% |
| Short-term | 40% | 60% |

This is a **blend**, not a multiplication (`Investment Score ≠ Stock Score × Market Regime Modifier`), so a poor market regime dampens but does not zero out a strong individual stock score, and vice versa.

Stock Score composition is out of scope for this document; it belongs to a separate stock-scoring specification and is referenced here only for the blending interface.

---

## 6. Market Regime classification (R1–R6)

Regime is a discrete read of the same Market Score plus its internal composition (not just the blended number), because two markets can share the same headline score for different reasons (e.g., strong trend offsetting weak breadth vs. genuinely broad strength).

| Regime | Label | Candidate condition (illustrative, to be fit via §9-10) |
|---|---|---|
| R1 | Strong Risk-On | Trend, Breadth, Risk, Rates/Liquidity all above ~70th percentile score |
| R2 | Normal Risk-On | Market Score in upper range but at least one axis moderate, not all strong |
| R3 | Late-Stage / Caution | Trend strong but Breadth and/or Risk deteriorating (internal divergence) |
| R4 | Neutral / Transition | Market Score mid-range, no axis dominant, low directional conviction |
| R5 | Risk-Off | Trend broken and Risk/Rates axes weak |
| R6 | Panic | Sharp drawdown + volatility spike + liquidity/credit deterioration concurrently |

### 6.1 Relationship to the existing Stress Convergence three-state system

R1–R6 is a **market-regime** read (trend/breadth/risk/liquidity/cross-asset), while Early Warning / Tightening State / Crisis Confirmation is this project's existing **macro-stress detection** layer. They are different axes measuring related but distinct things and must not be merged into one label.

Working (unvalidated) mapping to keep them consistent rather than contradictory:

- A live **Crisis Confirmation** state should never coexist with an R1/R2 read; if it does, treat it as a flag that the Market Score inputs are stale, mis-specified, or lagging, not evidence that the crisis is unimportant.
- **Tightening State** most plausibly overlaps with R3 (late-stage/caution): rate/policy pressure without confirmed damage.
- **Early Warning** most plausibly overlaps with R3/R4 transition zones.
- R5/R6 should be the regimes most likely to co-occur with **Crisis Confirmation**, but co-occurrence is an empirical question for §9, not an assumption.

This cross-check is itself a falsification target (§10): if R-regime and Stress Convergence state routinely disagree with no explainable cause, one or both classification schemes need revision.

### 6.2 Concrete candidate regime decision rule (v0.1, 2026-09-08 addendum)

The §6 table above is deliberately qualitative ("illustrative"). A follow-up memo proposed a fully computable boolean version, evaluated top-down (first matching rule wins):

```
R1  if  Market_Score >= 80  AND  Breadth_Score >= 70  AND  VIX <= 18            AND  HY_OAS <= 250bp
R2  if  60 <= Market_Score < 80  AND  Breadth_Score >= 50
R3  if  Market_Score >= 60  AND  (Breadth_Score < 50  OR  VIX > 22)
R4  if  40 <= Market_Score < 60
R5  if  20 <= Market_Score < 40  OR  (Drawdown > 15%  AND  VIX > 25)
R6  if  Market_Score < 20  OR  (VIX > 35  AND  HY_OAS > 500bp)
```

This is recorded as this framework's first testable Regime formula — concrete enough to run against history in §9 — but every numeric threshold in it (80/70/18/250bp/60/50/22/40/20/15%/25/35/500bp) is an untested candidate carried over from the same follow-up memo discussed in §4.1, sourced mostly from blog-tier restatements rather than this project's own data. Before this rule is used for anything beyond a backtest input, it must clear at minimum §10 Levels 1-3 (economic logic — already partially established in §1.2; statistical relationship; historical backtest), and its specific cut points must survive the §10.6 parameter-sensitivity sweep (e.g., does R1 still separate cleanly if 80 is replaced with 75/85, or 18 with 16/20?) rather than being adopted because they look reasonable.

Two structural notes carried over from the qualitative §6 table still apply and are not superseded by the boolean form: (1) R1-R6 must be cross-checked against the Stress Convergence three-state system per §6.1, and (2) mid-band regimes (R3/R4) that AND/OR-combine on both a level and a divergence condition are exactly the "index up, internals weak" case this framework exists to catch (`LESSONS_LEARNED_2026-09-08_MARKET_SESSION.md`) — a pure Market_Score cutoff without the breadth/VIX override would miss it.

---

## 7. Connection to Buy Intensity

The existing Buy Intensity formula (`CLAUDE_HANDOVER_2026-09-08.md` §6):

```
Buy Intensity = Portfolio Gap x Asset Opportunity x Risk Gate x FX Benefit
```

This framework proposes Market Regime as an explicit input to **Risk Gate**, replacing "Risk Gate = discretionary judgment" with "Risk Gate = a documented function of Market Regime and horizon":

```
Risk Gate(horizon) = f(Investment Score(horizon))
Investment Score(horizon) = StockScoreWeight(horizon) x Stock Score
                           + MarketScoreWeight(horizon) x Market Score
```

Candidate Risk Gate bands (illustrative, not frozen):

| Regime | Candidate Risk Gate posture |
|---|---|
| R1 | Normal-to-full staged deployment allowed |
| R2 | Normal staged deployment |
| R3 | Reduce tranche size; do not increase pace |
| R4 | Hold; do not initiate new tranches |
| R5 | Defensive; only pre-committed defensive tranches |
| R6 / Crisis Confirmation | No new discretionary deployment; only the pre-declared final Stress/Panic tranche (`PORTFOLIO_ALLOCATION_RULE_v0.1.md` §7: "Stress/panic regime: final 30%") |

This must not be read as replacing the FX Benefit or Portfolio Gap terms; Market Regime modulates Risk Gate only. It also must not be used to auto-trigger the panic tranche — per existing rules, FX/volatility alone never triggers a large purchase (`CLAUDE_HANDOVER_2026-09-08.md` §14).

## 8. Connection to Risk Score

A separate Risk Score (portfolio-level, not market-level) should combine:

- Market Regime (this document)
- Concentration/overlap rules already in force (`PORTFOLIO_ALLOCATION_RULE_v0.1.md` §6: Samsung/semiconductor overlap, NVIDIA overlap)
- Current staged-deployment position (how much of the planned tranche is already deployed)
- Stress Convergence state (Early Warning / Tightening / Crisis Confirmation)

Risk Score is not defined further here; it requires its own specification once Market Regime (§6) has at least completed §10 levels 1-3 (economic logic, statistical relationship, historical backtest).

---

## 9. Historical backtest design (10-20 year horizon)

Before any Market Score is used for a live decision, run:

1. Compute daily Market Score and Regime label over the longest available consistent history for each candidate market (target 10-20 years where data quality allows).
2. For each historical day, record forward returns at 5/20/60/120 trading days.
3. Build the score-bucket vs. forward-return table (as in the originating research memo's Section 10 example) for each forward horizon, separately.
4. Build the Regime vs. realized-performance table (mean return, win rate, realized volatility, max drawdown) for each of R1-R6.
5. Repeat step 3-4 pipeline separately for each market this project cares about (KOSPI plus at least one broad US benchmark), not just one market (§10.7 below generalizes this further).

A monotonic (or near-monotonic) relationship between score bucket and forward return, replicated across horizons and markets, is the minimum bar to advance past Level 3 in §10. A disordered relationship (e.g., mid-score buckets outperforming high-score buckets) is a rejection signal, not something to patch by re-fitting weights on the same sample.

### 9.1 First exploratory result (2026-09-08) -- falsification condition triggered

Ran the §4.1/§6.2 candidate spec (`research/scripts/run_market_regime_v0.1_backtest.py`, GitHub Actions run `34189772007`) against real KOSPI, KOSDAQ, S&P 500, Russell 2000, VIX, gold, and UST-yield data covering **1996-12-11 to 2026-09-08 (9,342 trading days, ~30 years)** -- this session's own network egress blocks FRED/Yahoo Finance directly, so the script ran in CI, matching the existing `run_v0.2.3_daily_panel.py` pattern. Status: **EXPLORATORY**, not an OFFICIAL run (no frozen fixture/spec hash yet, per `research/stress-convergence/README.md`'s reproducibility gate).

**Result: the score-bucket vs. forward-return relationship is not monotonic, and at the 60-120 day horizons the lowest-score bucket and the Panic (R6) regime often show among the *strongest* forward returns, not the weakest.**

Selected figures (full tables in the CI run's `report.md` artifact):

| Market | Horizon | 0-20 bucket mean fwd return | 80-100 bucket mean fwd return |
|---|---:|---:|---:|
| KOSPI | 60d | **+7.97%** (n=378) | +0.66% (n=23) |
| KOSPI | 120d | **+8.25%** (n=378) | +13.16% (n=23, noisy) |
| S&P 500 | 120d | **+8.84%** (n=420) | +2.49% (n=106) |

| Market | Horizon | R6 (Panic) mean fwd return / win rate | R2 (Normal Risk-On) mean fwd return / win rate |
|---|---:|---:|---:|
| KOSPI | 120d | **+4.86%** / 81.5% (n=162) | +5.87% / 62.8% (n=1571) |
| S&P 500 | 120d | **+7.65%** / 82.8% (n=262) | +3.87% / 75.9% (n=2077) |

This is precisely falsification condition **§11.1** ("score-bucket vs. forward-return relationship is not monotonic across at least two independent forward horizons") **being triggered**, on real data, across both markets tested, at the 60d and 120d horizons specifically. Per §11's own instruction, this is a signal to revise the current axis weighting, not something to patch by re-fitting weights on this same sample.

**Read this result carefully, not as "the framework failed" but as informative:**

1. **The pattern looks like classic post-drawdown mean reversion / panic-recovery**, not evidence that the five axes are meaningless. Low Market Score and R6 (Panic) days are disproportionately drawn from a small number of major crisis-recovery episodes (2000-2002, 2008-2009, 2020 COVID crash, 2022 rate shock); a single-bucket average over 30 years does not distinguish "this score level generically predicts a bounce" from "a handful of well-known V-shaped recoveries dominate the average of a small bucket." This has not yet been decomposed by episode.
2. **Sample sizes at the extremes are thin and the R1/R6 boolean conditions in §6.2 are evidently too strict**: KOSPI R1 fired on only 6 of 9,342 days in 30 years; S&P 500 R1 fired on only 1 day. A rule that essentially never fires cannot be evaluated meaningfully and needs its own cut-point recalibration (§10.6) before its bucket/regime statistics are trusted at all.
3. **This is a single full-sample run, not out-of-sample or walk-forward** (§10 Levels 4-5). A full-sample bucket table is exactly the Level-3 evidence this document's own validation stack says is insufficient on its own -- this result is the concrete illustration of why L4/L5 are required next, not a reason to promote or reject any rule yet.
4. The Trend axis's own economic anchor (Moskowitz/Ooi/Pedersen 2012, §1.2) documents momentum operating on a 1-12 month continuation basis with reversal over longer horizons -- so a reversal-dominated pattern at 60-120 days is not inherently inconsistent with that literature; it may indicate this candidate's blend of axes (particularly Risk/Macro, weighted toward "conditions have already normalized" rather than "conditions are currently deteriorating") is capturing something closer to a recovery-confirmation signal than a forward-looking risk-on signal as currently specified.

**Immediate implication for §7 (Buy Intensity connection):** the current Risk Gate mapping (R1 = full deployment, R6 = no new deployment) is **not** supported by this result as specified, and must not be treated as validated. It is explicitly still gated behind the unmet §10 L1-L3 bar (§8, §12), and this result adds a concrete reason it should not advance further without the decomposition and OOS/walk-forward work in §12.

## 10. Validation stack (Levels 1-10)

This is the gate a rule must pass before promotion to a decision rule, and it extends the project's existing research loop (`INVESTMENT_RESEARCH_LOOP.md`) with the additional overfitting-control steps this document's originating memo specified.

```
L1  Economic-logic check        - does a mechanism justify the indicator before any test is run?
L2  Statistical relationship    - score-bucket vs. forward-return table (S9)
L3  Historical backtest         - full-sample backtest with FP/FN/lead-time/coverage
L4  Out-of-sample               - freeze rule on an early sub-period, test unseen later period
L5  Walk-forward                - rolling train/test windows, not one static split
L6  Parameter sensitivity       - vary each threshold/window (e.g., MA length) and confirm
                                   the result is not a single-point artifact
L7  Transaction cost/slippage   - re-run with realistic cost assumptions before judging return
L8  Cross-market validation     - same rule tested on KOSPI + at least one non-Korean market
L9  Data-snooping control       - correct for the number of rules/parameters tried
                                   (White's Reality Check / SPA-style correction; see note below)
L10 Paper trading / live watch  - monitor the rule live, unfunded, before it can size real capital
```

Notes:

- **L9** exists specifically because this project (and its originating research) will inevitably test many indicator/threshold combinations; an apparently good result found among many trials is expected to occur by chance and must be discounted accordingly, not reported as if it were the only test run.
- A rule that has only passed L1-L3 (economic logic + statistical pattern + one historical backtest) is explicitly **not** eligible for capital deployment under this project's existing discipline ("A successful backtest is not sufficient evidence for deployment," `INVESTMENT_RESEARCH_LOOP.md`).
- For advanced statistical rigor once a rule reaches L6-L9, the project may additionally apply a Deflated Sharpe Ratio and/or a Probability-of-Backtest-Overfitting (PBO / CSCV) check before final promotion; these are optional strengthening steps, not a substitute for L1-L9.

### 10.1 Rule Confidence Score (separate from Investment Score)

Per the originating research memo, this framework additionally tracks how far a rule has progressed through the validation stack, so a well-validated 82 and a barely-tested 82 are never treated the same:

| Validation component | Points |
|---|---:|
| Economic logic (L1) | 20 |
| Statistical significance (L2) | 15 |
| Out-of-sample (L4) | 15 |
| Walk-forward (L5) | 15 |
| Parameter robustness (L6) | 10 |
| Transaction cost realism (L7) | 10 |
| Cross-market validation (L8) | 10 |
| Data-snooping control (L9) | 5 |
| **Total** | **100** |

`Investment Score` and `Validation Score` must always be reported together for any rule surfaced in a live decision, e.g. "Market Score = 82, Validation Score = 43 (L1-L3 only — not eligible for sizing decisions yet)."

### 10.2 L9 methodology detail — verified against primary sources (2026-09-08 addendum)

A follow-up research memo proposed concrete formulas/thresholds for the L9 data-snooping step and beyond (DSR, PBO/CSCV, White's Reality Check, Hansen's SPA). Before adopting any of it, the underlying citations were checked against this project's evidence hierarchy (`INVESTMENT_RESEARCH_LOOP.md` §2). Result:

**Primary sources confirmed to exist and be correctly attributed** (via search, not direct PDF fetch — this session's network policy blocked outbound fetches to davidhbailey.com, wikipedia.org, sdm.lbl.gov, and arxiv.org, so formula text below is stated from established prior knowledge of these papers, not a fresh read of the PDFs; a future session with fetch access should confirm directly before this framework is finalized):

- Bailey, D.H. & López de Prado, M. (2014). "The Deflated Sharpe Ratio: Correcting for Selection Bias, Backtest Overfitting and Non-Normality." *Journal of Portfolio Management*, 40(5), 94-107. (SSRN #2460551)
- Bailey, D.H., Borwein, J., López de Prado, M., & Zhu, Q.J. (2017, working paper 2014). "The Probability of Backtest Overfitting." *Journal of Computational Finance*, 20(4), 39-69. (SSRN #2326253)
- White, H. (2000). "A Reality Check for Data Snooping." *Econometrica*, 68(5), 1097-1126.
- Hansen, P.R. (2005). "A Test for Superior Predictive Ability." *Journal of Business & Economic Statistics*, 23(4), 365-380.

**Rejected as citation-quality sources for this project**: most of the numbered links attached to the follow-up memo (e.g. saral.money, usekeel.io, surmount.ai, aifinhub.io, globalmarketstructure.com) are secondary blog/SEO-tier restatements of the above papers. Per this project's rule against counting re-publications of the same original as independent evidence, they are not cited further here; the four primary sources above are the ones this framework relies on.

**Formula/procedure (candidate, pending direct primary-source re-verification):**

```
DSR = Z( (SR_hat - SR0) * sqrt(T-1) / sqrt(1 - gamma3*SR_hat + ((gamma4-1)/4)*SR_hat^2) )
```

- `Z(.)`: standard normal CDF.
- `SR_hat`: the strategy's estimated (non-annualized, per-period) Sharpe ratio.
- `SR0`: the *expected maximum* Sharpe ratio obtainable from N independent trials under the null of zero true skill, estimated via extreme-value theory from the variance of Sharpe ratios across trials and N (not simply 0).
- `gamma3`, `gamma4`: skewness and kurtosis of the strategy's return distribution.
- `T`: number of return observations.
- `N`: number of independent strategy/parameter trials considered (this is the number that must be honestly reported — see L9 note above).

CSCV / PBO procedure:

1. Build a `T x N` matrix of returns (T periods, N candidate rule/parameter configurations).
2. Split the T periods into `S` contiguous, equal-length blocks (the original paper's illustrative examples commonly use S=16; S is a design choice, not fixed by theory).
3. Form all `C(S, S/2)` ways to select half the blocks as an in-sample (IS) combination, with the complementary half as out-of-sample (OS).
4. For each combination: pick the configuration with the best IS performance statistic, then find that same configuration's relative rank among all N configurations' OS performance.
5. PBO = the share of combinations in which the IS-selected winner ranks at or below the OS median (i.e., the in-sample winner is a below-median out-of-sample performer).

**On numeric acceptance thresholds**: the follow-up memo's "DSR >= 0.95" and "PBO <= 0.10" are **not being adopted as this project's pass/fail lines**. DSR is a probability-style statistic and 0.95 is simply the conventional significance level an analyst can choose (analogous to p<0.05), not a value mandated by the original paper. The PBO paper reports PBO as a diagnostic — its own empirical examples include cases with PBO around 0.5 (i.e., near-certain overfitting) — and does not itself prescribe a universal cutoff. Per this project's rule against importing externally-asserted thresholds as hard governance rules without independent testing, `DSR` and `PBO` acceptance lines for this project must instead be calibrated from this project's own L1-L8 backtests once they exist, and recorded as a new candidate threshold with its own falsification condition, not copied from secondary sources.

These two techniques remain **optional strengthening steps for L9/L10**, applicable only after a rule has already cleared L1-L8; they do not substitute for out-of-sample, walk-forward, parameter-sensitivity, transaction-cost, or cross-market testing.

---

## 11. Falsification conditions (framework-level)

Reject or revise this framework, in whole or in the relevant axis/weight, if any of the following is demonstrated on a frozen benchmark:

1. Score-bucket vs. forward-return relationship (§9) is not monotonic across at least two independent forward horizons. **TRIGGERED 2026-09-08 — see §9.1**: the first exploratory ~30-year run showed a non-monotonic, partly-inverted relationship at the 60d/120d horizons on both KOSPI and S&P 500. Per this section's own rule, the current axis weighting/cut points may not be promoted from this evidence and require the episode-decomposition and OOS/walk-forward work in §12 before any revision is drafted.
2. Regime classification (§6) shows no meaningful separation in realized volatility/drawdown/return across R1-R6.
3. The 25/20/20/20/15 axis weighting or the 70/30-60/40-40/60 horizon blend is not robust to reasonable parameter perturbation (§10.6).
4. Results do not replicate out-of-sample (§10.4) or across markets (§10.8).
5. Adding an axis or indicator only improves in-sample fit and fails L9 data-snooping correction.
6. Market Regime and Stress Convergence state disagree systematically without an identifiable, documented cause (§6.1).
7. A DSR/PBO acceptance threshold copied from a secondary source (rather than calibrated on this project's own L1-L8 results, per §10.2) is used to justify promoting a rule.
8. Any of the §4.1/§6.2 candidate numeric cut points (e.g., VIX <= 18, HY OAS <= 250bp, the 80/60/40/20 Market_Score bands) is used in a live decision before it has been recalibrated on this project's own trailing-percentile data (§4) and passed §10.6 parameter-sensitivity testing.

## 12. Immediate open work (P-items)

Consistent with the existing "Immediate Open Work" convention (`CLAUDE_HANDOVER_2026-09-08.md` §13):

- **P0 — Indicator/source freeze.** Select the concrete series for each of the 5 axes and freeze their exact definitions and sources (§1-§2) before any scoring code is written.
- **P0 — Cross-Asset (Axis E) methodological anchor.** §1.2 found no canonical academic/institutional template for this axis (unlike NFCI for Axis D or the breadth literature for Axis B); define and justify this project's own cross-asset composite before treating it as equally evidenced as the other four axes.
- **P1 — Score-bucket vs. forward-return backtest (§9).** DONE (2026-09-08, exploratory) — see §9.1. Falsification condition §11.1 triggered; do not repeat this step without addressing the P0 items below first.
- **P1 — Regime vs. Stress-Convergence cross-check (§6.1).** Once Market Regime exists historically, compare its labels against the existing Stress Convergence window results already computed in `research/stress-convergence/`.
- **P1 — Implement and backtest the §4.1/§6.2 candidate spec.** DONE (2026-09-08, exploratory, `research/scripts/run_market_regime_v0.1_backtest.py`, GitHub Actions run `34189772007`) — see §9.1 for results. Both the hardcoded-cut-point and trailing-percentile-transform variants share the same underlying axis inputs in this run; the two have not yet been run and compared separately, which remains open.
- **P0 — Episode decomposition of the §9.1 result.** Break the score-bucket and regime-performance tables down by known historical episode (2000-2002, 2008-2009, 2020 COVID crash, 2022 rate shock, and the "normal" periods between them) to test whether the mean-reversion pattern found is generic or driven by a small number of V-shaped recoveries dominating a thin low-score/R6 bucket.
- **P0 — Out-of-sample / walk-forward split before any weight revision.** Per §10 L4-L5: freeze a training sub-period, evaluate on an untouched later period, and repeat with rolling windows, before drawing any conclusion about whether the current axis weights should change. Do not re-fit weights on the same full sample that produced the §9.1 result.
- **P0 — Recalibrate the R1/R6 boolean cut points (§6.2).** §9.1 found R1 fired on only 6 of 9,342 KOSPI days and 1 of 9,342 S&P 500 days in 30 years -- too rare to evaluate meaningfully. Test alternative cut points (per §10.6 parameter sensitivity) before trusting any R1/R6 statistic.
- **P2 — Risk Gate wiring (§7).** Only after L1-L3 pass: connect Market Regime output to the Buy Intensity Risk Gate term as a documented, versioned function, not a discretionary override.
- **P2 — Parameter sensitivity and cross-market replication (§10.6, §10.8).**
- **P3 — Data-snooping correction and Rule Confidence Score tooling (§10, §10.1).**
- **P3 — Primary-source re-verification for §10.2.** Directly fetch and re-check the DSR (Bailey & López de Prado, 2014) and PBO/CSCV (Bailey, Borwein, López de Prado & Zhu, 2017) papers once network/fetch access allows, since this session could only confirm them via search, not a direct PDF read.

## 13. What this document does not do

- It does not certify any weight, threshold, or regime boundary as validated.
- It does not authorize using Market Score/Regime to trigger a trade on its own.
- It does not replace the FX Buy Intensity rule, the Portfolio Allocation staging rule, or the Stress Convergence three-state system; it specifies how a market-regime layer would connect to them once validated.
- It does not fabricate or assume any historical backtest result. All bucket tables, regime performance tables, and validation outcomes referenced above are to be produced by future runs recorded under `research/` with the same reproducibility discipline as `research/stress-convergence/` (fixture hash, spec hash, run ID, result hash).

## Lesson Learned

Market direction and market **state** are not the same thing; a state read needs at least trend, breadth, volatility/risk, rates/liquidity, and cross-asset flow evaluated jointly, and it must be validated with out-of-sample, walk-forward, parameter-sensitivity, and data-snooping controls before it can size a trade — a single historical backtest is not sufficient, matching this project's existing research discipline.

## Rule modification check

No existing hard rule is changed. This document introduces a new **candidate** framework (Market Regime R1-R6, five-axis Market Score, horizon-dependent Stock/Market blend, 10-level validation stack, Rule Confidence Score) that must clear the P0-P1 items in §12 before touching the Buy Intensity or Portfolio Allocation rules.

## Git storage decision

Persist this framework as durable research/methodology scaffolding. It defines the validation contract the project will hold itself to before any market-regime rule can size a real trade, which is material governance content.
