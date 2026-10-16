# Stock Methodology Test Contracts v1 — 2026-10-16

- Status: PRE-REGISTERED RESEARCH CONTRACT / NOT LIVE
- Comparator: EXPERIMENT_B0_ENGINE_2026-10-16
- Frozen source commit: 2394db0bbc21b6ab36f4840b78dc227e4a84445c
- Related issue: https://github.com/chayobi03-cyber/investment/issues/27
- Companion freeze manifest: B0_BASELINE_FREEZE_2026-10-16.md

## 1. Contract purpose and decision boundary

These contracts specify how to test incremental value from stock-investment methods without changing the existing engine or its decision permissions. They are not trading instructions and do not declare any candidate strategy successful.

Mandatory state for every run:
- BUY_ALLOWED=false
- EXECUTION_ALLOWED=false
- PROMOTION=DISABLED
- Decision state remains DATA_NOT_READY, BLOCKED, or RESEARCH_ONLY as appropriate.
- A research PASS is not a live promotion and does not bypass the existing M0–M3 gates.

No performance backtest may be used to support an investment conclusion until M1 Data Integrity is GREEN. Contract writing and offline test-fixture construction may proceed while the empirical strategy backtest remains blocked.

## 2. Global test contract — applies to every method

### 2.1 Run identity and immutable manifest

Every run must record:
- run_id, UTC/KST run timestamp, dataset snapshot IDs and SHA-256 hashes;
- source URLs/source IDs, collected_at, observed_at, published_at and available_at where relevant;
- market calendar/session, exchange timezone, rule/version IDs, code commit, dependency lockfile;
- EXPERIMENT_B0_ENGINE baseline ID and commit;
- universe snapshot, delisted/suspended/security-master treatment;
- train/validation/OOS date ranges, folds, purging/embargo, parameter grid and total trial count;
- execution convention, corporate-action version, fees, taxes, spread, slippage and liquidity assumptions;
- result artifact paths, test report, and blocker codes.

A run without a complete manifest is INVALID, not a negative or positive result.

### 2.2 Universe and survivorship

- Use a point-in-time Korean listed-equity universe with historical membership, delisted names, suspensions and ticker/security-identifier changes represented.
- Do not use the currently configured monitor watchlist as a substitute for the investable cross-sectional universe.
- Keep sector classifications point-in-time when used for ranks or neutralization.
- Keep LOCKED holdings in portfolio risk; never turn them into automatic sell instructions.
- Report KOSPI and KOSPI 200 total-return or price-return benchmarks with the return convention explicitly named. A benchmark's corporate-action convention must match the reported result.

### 2.3 PIT and financial-statement timing

- For market observations, decision_timestamp may use only observations available by that timestamp.
- For fundamentals, join on the actual publication/availability timestamp, not fiscal-period end, observation date, or a subsequently revised database value.
- Preserve original vintage and revision status. Unknown revision history blocks primary-grade use.
- The same-day publication rule must reflect available timestamp precision; date-only availability requires HUMAN_REVIEW on the release date and must not imply intraday availability.

### 2.4 Prices, corporate actions, fills and costs

- EOD signals execute no earlier than the next eligible regular-session bar. Same-close fills are prohibited unless the signal was genuinely available before that close and this is evidenced.
- Distinguish split-adjusted, dividend-adjusted total-return and raw executable prices. Never mix price bases.
- Handle splits, rights issues, distributions, delistings, trading halts and non-tradable sessions explicitly.
- Fees/taxes must come from a versioned, date-appropriate schedule. Spread/slippage must be recorded and sensitivity-tested, not set to zero by default.
- For liquidity, publish participation rate, turnover/capacity constraints and the treatment of price limits/halts. If these cannot be reconstructed, label the affected period DATA_NOT_READY.
- Model cash yield and the opportunity cost of uninvested capital in deployment comparisons.

### 2.5 Validation design

- Use chronological walk-forward evaluation, not random row splits.
- Minimum: three distinct OOS folds where verified history supports them. If adequate history is unavailable, do not claim OOS validation.
- Training, validation, and test boundaries must be frozen before inspecting OOS outcomes.
- Purge overlapping forward labels by at least the maximum forward outcome horizon; add an embargo of five trading sessions unless a stricter, pre-registered dependency-based embargo is required.
- Any threshold selection uses train/validation only. OOS outcomes cannot select the best parameter after the fact.
- If the candidate grid contains multiple variants, disclose all trials and apply a predeclared multiple-testing control; do not report only the winner.
- Report aggregate and per-fold, calendar-year, market-regime, sector, and liquidity-bucket results.
- Run base, stressed-cost, and parameter-sensitivity variants. Keep B0 and each benchmark on the exact same valid observations and execution assumptions.

### 2.6 Mandatory metrics

Capital survival first:
- maximum drawdown (MDD), 95% expected shortfall/CVaR, worst forward return, stress loss, recovery duration and time underwater;
- survival-constraint breach count and loss probability/depth/duration.

Signal and implementation:
- horizon-wise net forward returns, hit rate, rank IC/monotonicity where relevant, false-positive/false-negative rates, lead time;
- MAE/MFE, failed breakout rate, chase-entry frequency where relevant;
- turnover, capacity, cash drag, costs, and capital deployed.

CAGR is supplementary. A higher CAGR cannot offset an M1 failure, survival breach, materially worse tail risk, or execution impossibility.

## 3. M1 Data Integrity contract — mandatory first gate

Issue #27 remains OPEN. The method contracts below are NOT eligible for empirical promotion until this section passes in code and CI.

| ID | Regression condition | Required result |
|---|---|---|
| M1-01 | Same source has 5-minute bars; final two bars differ from the 15-minute move and daily move | Emit separately named 5m, validated 15m, and prior-session close-to-close returns. No horizon aliasing. |
| M1-02 | A required 15-minute window has missing, duplicated, out-of-order, or insufficiently spaced bars | Mark the affected horizon invalid; no substituting a 5-minute return or silently bridging the gap. |
| M1-03 | Verified prior regular-session close differs materially from the last 5-minute close | Daily return must use the verified prior close and retain both endpoint timestamps and price basis. |
| M1-04 | USD/JPY is fresh but KOSPI/KOSDAQ/Korean leaders are stale | Per-instrument and required-group quality is stale/AMBER/RED; a fresh unrelated symbol cannot promote aggregate quality to GREEN. |
| M1-05 | Required critical instrument missing, failed, or has no trustworthy source timestamp | DATA_NOT_READY/BLOCKED or AMBER/RED according to the existing contract; BUY_TRIGGER must not promote. |
| M1-06 | Headline/last price conflicts with bid/ask, high-low range, prior close, quote time or another trusted source beyond a predeclared tolerance | Mark quote conflict; require reconciliation; keep buy and execution locks false. |
| M1-07 | Market closed, holiday, delayed open, DST/session-boundary or timezone conversion fixture | Apply session-aware freshness rules; do not classify normal closed-market age as live-session freshness or invent a new session close. |
| M1-08 | Split/dividend/corporate-action fixture | Signal return and executable fill use consistent, documented price bases; no artificial return spike. |
| M1-09 | Future/revised fundamentals or macro observations inserted after the decision timestamp | Earlier signal/score remains unchanged; unavailable vintages block primary use. |
| M1-10 | Any upstream Data QA/PIT status is DATA_NOT_READY or BLOCKED | Decision gate remains fail-closed; BUY_ALLOWED=false, EXECUTION_ALLOWED=false, PROMOTION=DISABLED. |

Acceptance: all mandatory M1 regression tests pass in CI with stored test output; no unresolved critical quote/provenance/freshness blocker; a deliberate negative fixture must prove that invalid data cannot create GREEN or a buy trigger. A successful unit test alone does not establish source-level validity without provenance evidence.

## 4. B0 and reference baselines

- EXPERIMENT_B0_ENGINE: frozen existing engine at commit 2394db0bbc21b6ab36f4840b78dc227e4a84445c. It remains a comparator, not an approved signal.
- B1: KOSPI buy-and-hold and KOSPI 200 buy-and-hold; name price-return vs total-return series.
- B2: fixed calendar DCA with a frozen contribution schedule and explicit cash-interest/opportunity-cost treatment.
- B3: one simple time-series trend comparator using 200-day SMA.
- B3-M: monthly 10-month SMA variant as a separate test, not an after-the-fact replacement for B3.
- B0_NoBuy permission state in the existing Buy Trigger Engine is different from EXPERIMENT_B0_ENGINE. The baseline name must not change permission behavior.

Reference baselines are computed only once input data and costs are validated. Where the existing engine depends on the quarantined market monitor, comparisons can be specified but performance outputs remain BLOCKED until M1 passes.

## 5. Method-specific contracts

Every method is a standalone candidate. No candidate's output is added to a production Stock Score during this phase.

### C1 — Cross-sectional momentum / relative strength

Hypothesis: medium-term leadership contains incremental information about relative forward returns after controlling for market/sector conditions and executable cost.

Frozen primary definition:
- Compute 20-, 60-, and 120-trading-day total returns separately.
- Compute same-horizon relative strength versus KOSPI and the point-in-time sector return.
- Rank only within the eligible point-in-time universe and use a monthly rebalance.
- Treat the 20D, 60D, and 120D variants as separate registered trials; do not select the winner using OOS.

Primary metrics: cross-sectional rank IC, top-minus-bottom portfolio net return where shorting is not assumed unless permitted, decile monotonicity, turnover, MDD, 95% ES and sector concentration.

Pass criteria: net rank IC is positive with a 95% block-bootstrap confidence interval excluding zero in aggregate OOS; the direction is consistent in at least two-thirds of OOS folds; top-rank net results remain positive after stressed costs; and there is no survival-constraint breach or material tail-risk deterioration versus B0. If the required cross-sectional universe or survivorship history is unavailable, status is DATA_NOT_READY.

Falsification: rank ordering is non-monotonic, effect disappears after costs, is explained by one sector/calendar regime, or the result depends on an OOS-selected lookback.

### C2 — Quality / profitability

Hypothesis: financial strength improves candidate quality and/or limits severe downside independently of price momentum.

Inputs (each availability-timestamped and tested independently): cash-flow profitability, ROIC/ROE with sector context, operating margin and trend, leverage/interest coverage, accrual or one-off earnings flags, and investment/capital-intensity context. Do not proxy the full construct with ROE alone.

Primary comparison: B0 plus one predeclared quality composite versus B0, with equal-weight or otherwise predeclared factor construction. Fundamentals must be sector-aware and PIT-valid.

Primary metrics: downside-tail loss, worst forward returns, forward return distribution, quality-rank monotonicity, distress/impairment incidence, turnover and capacity.

Pass criteria: no future-publication/revision leakage; a positive incremental OOS result on the predeclared primary metric after costs in at least two-thirds of folds; no increase in survival breaches; and no materially worse MDD/95% ES. Use a 95% block-bootstrap interval and disclose sector/year decomposition.

Falsification: apparent benefit vanishes under actual publication lags, depends on restated values, is only an industry-composition effect, or worsens tail losses without compensating predeclared improvement.

### C3 — Value / valuation discipline

Hypothesis: valuation discipline can distinguish a good company from a good entry price and reduce value traps when used with, rather than in place of, quality and risk controls.

Inputs: sector-appropriate earnings/cash-flow/book-value multiples and FCF yield; exclude or separately define invalid multiples for sectors/business models where the denominator is not economically meaningful. Use PIT prices, PIT financial statements, and contemporaneous shares/market capitalization.

Primary metrics: valuation-rank monotonicity, net forward return by bucket, value-trap/distress rate, MDD, 95% ES and time-to-recovery.

Pass criteria: positive incremental OOS performance on the registered primary metric after costs, stable signs across at least two-thirds of folds, and no material deterioration in tail metrics/survival. Results must persist when value is tested separately and when conditional on quality; do not give duplicate full credit to highly correlated valuation ratios.

Falsification: cheapness is concentrated in structurally impaired issuers, post-release restatements create the apparent effect, sector normalization removes it, or the result depends on a single crisis/rebound period.

### C4 — Low-risk / volatility-aware sizing

Hypothesis: sizing by downside risk, liquidity and portfolio overlap can improve capital survival without assuming that lower volatility guarantees higher returns.

Frozen primary comparison: equal-risk budget using point-in-time 60D/120D realized and downside volatility plus correlation/overlap diagnostics, versus the B0 portfolio sizing rule. Parameters are fixed before OOS.

Required risk dimensions: direct security concentration, shared issuer/sector/theme exposure, ETF constituent look-through where evidenced, correlation, liquidity and stress contribution. Unknown ETF look-through is UNKNOWN, not zero. LOCKED positions remain risk-bearing and non-tradable.

Primary metrics: 95% ES reduction, MDD, stress loss, time underwater, risk concentration, turnover and cost.

Pass criteria: at least 10% relative reduction in OOS 95% ES against B0 on comparable exposure/capital; MDD must not worsen by more than 1 percentage point; no survival constraint may be violated; the effect must persist under stressed costs and at least two-thirds of folds. These are registered minimum-effect thresholds, not claims about realized results.

Falsification: risk estimate lags a volatility regime shift, concentration remains hidden by ETF wrappers, portfolio turnover erases the benefit, or risk reduction is achieved only by excessive persistent cash drag without the registered survival benefit.

### C5 — Time-series trend / exposure filter

Hypothesis: reducing risk exposure during persistent broad-market downtrends can lower tail losses and improve survival, with an explicit trade-off in whipsaw and missed rebound risk.

Registered variants: daily 200-day SMA and monthly 10-month SMA are separate comparators; no post-OOS replacement. Signal acts on portfolio-level exposure/permission in the research simulator, not an automatic sale order for LOCKED positions.

Primary metrics: MDD, 95% ES, stress loss, recovery duration, false regime switches, upside capture, whipsaw frequency and cash opportunity cost.

Pass criteria: at least 10% relative OOS reduction in 95% ES or a 2 percentage-point reduction in MDD; neither tail metric may materially worsen; upside capture may decline by no more than 10 percentage points versus the same benchmark; all costs and cash yield are included; result direction is consistent in at least two-thirds of folds.

Falsification: repeated whipsaw overwhelms avoided losses, results are dominated by a single selected threshold, delayed data changes exposure retrospectively, or rebound loss breaches the registered capture limit.

### C6 — Breakout / volume / CAN SLIM-SEPA-style entry setup

Hypothesis: a defined price-base breakout plus abnormal traded value improves entry quality over the existing D/W/M trend, support/resistance, recent-high, momentum and relative-strength checks.

Registered primary setup: close above a predeclared 55-session high with traded value at least 1.5 times its trailing 20-session average, confirmed only on data available by that close and filled no earlier than the next eligible session. A 20-session breakout and alternate volume multipliers are sensitivity trials, not substitutes chosen after seeing OOS.

Primary metrics: failed-breakout rate, entry MAE/MFE, net forward return, chase-entry frequency, gap/limit-up fill failure, turnover, costs and tail loss.

Pass criteria: versus the same D/W/M-only control, reduce failed-breakout rate or adverse MAE by at least 10% relative, with no more than a 5 percentage-point increase in chase-entry frequency; net results remain positive after stressed costs; MDD/95% ES do not materially worsen. Use block bootstrap for uncertainty and disclose all registered variants.

Falsification: volume does not confirm after excluding auction/erroneous prints, the apparent gain disappears at next-session execution, price-limit/gap cases cannot be filled realistically, or selected variants fail multiple-testing control.

### C7 — Capital deployment: lump sum vs fixed DCA vs risk-gated staging

Hypothesis: deployment policy trades off market exposure, drawdown path, and regret/cash risk. DCA is a timing-risk comparator, not a promised source of alpha.

Compare:
- full lump-sum exposure at the eligible decision time;
- fixed periodic DCA with predeclared calendar/amount;
- risk-gated staged deployment with predeclared tranche count, spacing, cash reserve and invalidation rule.

Keep the same investable starting capital, eligible investment universe, benchmark, costs, cash yield and terminal measurement date.

Primary metrics: terminal wealth and annualized return (secondary to risk), interim/peak-to-trough drawdown, 95% ES, probability/depth/duration of loss, cash drag, time to target exposure and left-behind rebound.

Pass criteria: staged or DCA policy is considered useful only if it improves a predeclared risk/path metric without breaching the return-opportunity-cost budget and remains feasible after costs. It is not required to beat lump sum in every rising market. No policy may force purchases when M1 fails or when the permission layer is blocked.

Falsification: fixed DCA keeps buying during an active hard block, staging reduces exposure too late to change downside and misses rebound, results rely on an unregistered crisis start date, or cash drag exceeds the predeclared budget.

### C8 — Multifactor combination (locked behind single-factor evidence)

Hypothesis: combining independently useful factors can improve robustness beyond the strongest standalone factor without duplicated exposure or unstable weights.

Entry criteria: only standalone methods that passed their own contracts may be combined. Register a correlation-cluster map and a fixed weighting rule before the combination test. Do not double-count market regime in Stock Score and BuyStrength/permission.

Primary comparison: combined candidate against B0 and each passed single-factor candidate; all use the same point-in-time universe and cost assumptions.

Pass criteria: incremental net OOS benefit versus the best passed single factor on the registered primary metric, no material tail-risk/survival deterioration, stability across folds/regimes, and multiple-testing control across all tried combinations.

Falsification: gains are explained by one factor, one sector or one period; correlated copies inflate the score; fitted weights are unstable; or the combination does not outperform the best standalone candidate.

## 6. Experimental sequence and promotion gates

1. Fix B0 manifest and preserve its source commit.
2. Close and verify M1 regression requirements, beginning with Issue #27.
3. Validate data completeness, PIT/vintage, corporate actions, calendar/session and execution-cost assumptions.
4. Reproduce B0 outputs as parity control.
5. Compute B1/B2/B3 reference baselines.
6. Run C1–C7 separately; keep all parameters frozen.
7. Test C8 only after at least two standalone methods pass.
8. Produce a cold-audit report with run manifests, failed tests, artifacts and all registered trials.
9. Obtain independent review and explicit promotion approval.

Promotion gates remain separate: evidence-ready → baseline parity → incremental value → robustness → paper/shadow → independent promotion review. Passing this document's criteria never flips BUY_ALLOWED or EXECUTION_ALLOWED.

## 7. Required artifacts and status labels

Each experiment produces:
- contract version and run manifest;
- input/source-vintage hashes and validity report;
- test output and fold-by-fold metrics;
- sensitivity and stressed-cost report;
- falsification result;
- machine-readable status: PASS, FAIL, DATA_NOT_READY, BLOCKED or RESEARCH_ONLY;
- artifact path and reproducible run identifier.

Never collapse missing evidence into zero, and never label a test “passed” if it was not executed.

## 8. Lesson learned from this contract

Data integrity is upstream of every strategy claim. A frozen comparator is useful only if its exact source version is immutable and its defects are disclosed. “B0” is overloaded in the current system, so the experiment baseline and the Buy Trigger No Buy state must use distinct identifiers. No live thresholds or decision permissions are changed by this contract.
