# Investment Opinion Availability & Decision-Gate Audit v1.0

- Audit date: 2026-10-19 (KST)
- Repository: https://github.com/chayobi03-cyber/investment
- Audited base: main at c30f3f0b7e2ed84f4b668b4778d57e51fc1b5312
- Mode: READ-ONLY SYSTEM AUDIT; DOCUMENTATION-ONLY PERSISTENCE
- Final classification: MIXED_FAILURE
- Promotion: DISABLED
- Operational permissions: BUY_ALLOWED=false; EXECUTION_ALLOWED=false
- Strategy/backtest result: NOT_EXECUTED in this audit unless explicitly described as an existing GitHub check result

## 1. Executive Summary

### 1.1 Conclusion

MIXED_FAILURE. Two different issues coexist:

1. Safety blocking is justified. Issue #27 records a material market-data integrity defect on 2026-10-12: the main-branch monitor computed the change from adjacent 5-minute bars while labelling the threshold as 15-minute, and aggregate freshness used the newest timestamp across all instruments. The runtime consequently showed KOSPI -0.377% versus reported session close -3.65%, and DATA_QUALITY=GREEN. Do not relax the data-quality or execution safeguards while this remains unresolved on main.
2. Opinion blocking is structurally confirmed. The main-branch decision contract only returns DATA_NOT_READY, BLOCKED, or RESEARCH_ONLY. It has no opinion class, thesis, confidence, valuation state, downside case, opinion validity, or reassessment trigger. DecisionGateAgent and the schema hard-code BUY_ALLOWED=false and EXECUTION_ALLOWED=false. The orchestrator also allows upstream permission and evidence statuses to drive the final decision status. Thus a supported asset opinion cannot be represented independently in the current machine-readable contract.

The right fix is not to relax a safety gate. It is to add a separate Opinion Engine and return its result alongside independent Permission and Execution results. The B0 comparator must remain research-only, and no live permission or execution state should change in this audit.

### 1.2 Most important findings

| ID | Finding | Status | Consequence |
|---|---|---|---|
| F-01 | No opinion fields or opinion-ready state in the decision schema | CONFIRMED | Final output cannot reliably express buy/hold/wait as an investment view independently of permission |
| F-02 | Hard false buy/execution locks are embedded in code, config and schema | CONFIRMED | Live trading is intentionally impossible in this contract; this is not evidence that an asset is unattractive |
| F-03 | PIT failure fans out to all downstream agents | CONFIRMED | An input-quality failure suppresses the whole decision path instead of preserving independent, supported conclusions |
| F-04 | Market monitor on main confuses bar return horizon and aggregate freshness | CONFIRMED | Market state may be falsely GREEN; no buy-trigger or execution use until remediation is merged and verified |
| F-05 | Draft PR #30 contains remediation tests but is not merged | CONFIRMED | Its passing PR checks do not repair main |
| F-06 | Market Regime V1 says two-observation confirmation, while RegimeAgent immediately copies raw_regime into confirmed_regime | CONFIRMED | Contract/specification mismatch; false transitions and response lag have not been empirically measured |
| F-07 | RiskAgent checks input presence, not numeric risk limits | CONFIRMED | A non-null but severe MDD/MAE/stress-loss input may still pass if concentration_ok is true |
| F-08 | Historical gate pass rates and opportunity delays are not computed by this audit | NOT_TESTED | Do not claim the gates are too strict or quote pass-rate estimates without a replay dataset |

### 1.3 Operating decision now

- Keep BUY_ALLOWED=false, EXECUTION_ALLOWED=false, and PROMOTION=DISABLED.
- Permit a separately labelled research opinion when the evidence for that specific conclusion is sufficient.
- Scope DATA_NOT_READY to the affected conclusion and fields. Example: unavailable or conflicting live quotes should block current entry-price assessment and execution; they need not erase a source-backed long-term business thesis whose evidence is independently valid.
- Do not label an asset attractive at the current price until valuation, portfolio concentration, and data-quality checks have been performed.
- Do not use a research score, B0 experiment, or passing scheduled monitor run as live purchase authorization.

## 2. Evidence Inventory

### 2.1 Directly inspected repository evidence

| Artifact | Direct observation | Audit use |
|---|---|---|
| src/investment_pipeline/decision_gate.py | States are DATA_NOT_READY, BLOCKED, RESEARCH_ONLY. Module-level BUY_ALLOWED and EXECUTION_ALLOWED are False. All-green upstream agents yield RESEARCH_ONLY. | Confirms permission-locked contract and absence of opinion status |
| tests/test_decision_gate.py | Tests assert all-green is still RESEARCH_ONLY and both permissions are false | Shows no current test path where a supported opinion is output independently of permission |
| src/investment_pipeline/multi_asset_subagents.py | DecisionAgent marks non-PASS permission/regime/risk/evidence/source/conflict/hallucination statuses as blockers; PIT failure creates DATA_NOT_READY results for downstream agents | Confirms the all-agent gate and the broad PIT short-circuit |
| tests/test_multi_asset_subagents.py | Test checks that signal_state survives when permission is blocked, while final decision_status is BLOCKED | Signal is preserved as a field, but no separate opinion type/rationale is asserted |
| schemas/multi_asset_decision_v0.1.schema.json | additionalProperties=false; permission fields have const=false; no investment opinion or valuation fields | Confirms opinion is not expressible in the current contract |
| docs/investment/MARKET_REGIME_ENGINE_V1.md | Status is OPERATIONAL RESEARCH SPEC — DATA CONNECTION PENDING; states point-in-time input rules and two-consecutive-observation regime confirmation | Confirms regime contract is not yet validated against a complete connected data pipeline |
| config/market_monitor.json | Return thresholds are named material_abs_pct_15m; max_stale_minutes=30 | Contrasts with main-branch poll implementation |
| scripts/market_monitor/poll.py on main | fetch_chart requests 1d/5m and divides the last bar close by the previous bar close; build_state computes freshness using max timestamp across all symbols | Direct implementation evidence for Issue #27 |
| tests/test_market_monitor.py on main | Existing tests cover state thresholds/alerts/breadth/VIX, but not all issue #27 horizon/freshness regression cases | Explains why a green historical suite does not prove these specific contracts |
| docs/investment/STOCK_SCORE_V1.md | Calls for required D/W/M validation and keeps numeric thresholds unfixed until the data set and validation study exist | Threshold and data dependency are acknowledged; do not invent values |
| docs/portfolio/PORTFOLIO_FACTOR_EXPOSURE_RULE_V1.md | Requires direct plus ETF look-through and factor-overlap aggregation; unavailable FX or holdings data must remain unknown | Portfolio concentration must be calculated from reconciled holdings, not ticker count |
| docs/research/STOCK_METHOD_TEST_CONTRACTS_V1_2026-10-16.md | All methods stay RESEARCH_ONLY; empirical promotion blocked until M1 Data Integrity is GREEN; defines PIT, costs, walk-forward and tail-risk requirements | Preserves frozen research/operational boundary |
| docs/governance/LESSONS_LEARNED_2026-10-16_B0_M1_STOCK_METHODS.md | Says Issue #27 remains OPEN, main is NOT M1-CLEARED, and separates EXPERIMENT_B0_ENGINE from BUY_TRIGGER_B0_NO_BUY | Baseline naming and no-promotion safeguards remain in force |
| docs/strategy/Handoff.md | Issue #27 and #31 are open; requires no-trade execution, PIT checks, D/W/M validation, realistic fill and cost modelling | Existing work items and next steps remain applicable |
| GitHub Issue #27 | Details 2026-10-12 monitor divergence, root causes, and required regression tests | Primary evidence for crash-session quality failure |
| GitHub Issue #31 | Requires deterministic market workflow and HOTL persistence; remains open | Operational workflow/reproducibility is not complete |
| GitHub PR #30 | Draft, open, unmerged; branch fix/market-monitor-horizons-issue-27; has tests/backtest/test-history check runs completed successfully on 2026-10-16 | Remediation exists as an unmerged candidate, not as main-branch behavior |

### 2.2 Current branch and CI state

- Main SHA observed through GitHub API: c30f3f0b7e2ed84f4b668b4778d57e51fc1b5312.
- PR #30 head SHA: 6c9ba73cae60c32eded9f25a0024a9d17fd58037; PR remains draft/open and unmerged.
- PR #30 had check runs named tests, backtest, and test-history with conclusion success on 2026-10-16. These are branch checks for that PR, not proof that its changes are on main or that full 2000/2008/2020/2022 equity replays passed.
- Main's recent scheduled monitor/research/backtest/provenance jobs on 2026-10-19 report success. They are scheduled operational jobs and do not establish that the known main-branch monitor defect has been fixed.
- This audit did not execute the local test suite or a historical strategy replay. Test claims above are limited to the observed GitHub check metadata and inspected test code.
- The attempt to fetch a root-level Handoff.md returned not found; the applicable existing handoff is docs/strategy/Handoff.md. No evidence was found that the current repository contains a committed current-price investment opinion contract.

### 2.3 Current market observations used only for case reconstruction

These prices are contextual evidence, not order-ready quotes:

- TSM (NYSE ADR): last completed regular-session close found was USD 412.61 on 2026-10-16; open 421.22, high 421.50, low 410.58. Source: https://nz.finance.yahoo.com/quote/TSM/history/ and https://chartexchange.com/symbol/nyse-tsm/historical/
- USD/KRW: Investing.com’s 2026-10-19 historical table shows a close around KRW 1,328.72 per USD. Source: https://kr.investing.com/currencies/usd-krw-historical-data
- SK hynix: retrieved providers show conflicting 2026-10-19 values/closures in the approximate KRW 1.252M–1.262M range, with daily low around KRW 1.208M and high around KRW 1.268M on one source. Source: https://kr.investing.com/equities/sk-hynix-inc-historical-data and https://stockanalysis.com/quote/krx/000660/history/. Treat the discrepancy as a data-quality issue; do not choose one value as an executable quote without reconciliation.
- TSMC’s Q3 2026 net income was reported at T$763.1B, +69% year over year, on 2026-10-15. Source: https://www.reuters.com/world/asia-pacific/tsmc-q3-profit-jumps-69-record-beating-expectations-2026-10-15/
- Reuters reported the KOSPI closed at 5,554.22, down 7.57%, on 2026-10-15 with foreign selling of about KRW 3.6T. Source: https://www.reuters.com/world/asia-pacific/south-koreas-kospi-triggers-circuit-breaker-tech-led-selloff-2026-10-15/

## 3. Root-Cause Analysis

Status definitions: CONFIRMED means directly supported by inspected implementation/test/issue evidence; PARTIALLY_CONFIRMED means a mechanism or adjacent symptom is proven but the specific historical user-response cause is not; NOT_CONFIRMED means evidence does not support the claim; NOT_TESTED means the required replay/logs are unavailable.

| Candidate cause | Status | Evidence and interpretation |
|---|---|---|
| Latest price/FX/flow data missing or freshness checks fail | PARTIALLY_CONFIRMED | The monitor's freshness calculation is demonstrably unsafe (Issue #27); current TSM quote, FX and Korean equity inputs also require timestamp/source validation. We cannot prove this caused every prior opinion to be withheld. |
| Data-quality issue expands into suppression of the whole asset opinion | CONFIRMED | The PIT-failure branch injects DATA_NOT_READY into all downstream agents. The decision schema has no separate opinion-status output. Necessary for promotion/execution, excessive for independent conclusions supported by other valid evidence. |
| BUY_ALLOWED=false is effectively conflated with inability to produce an opinion | CONFIRMED (contract-level) | The decision contract has no opinion fields and a permanent false permission field. This is not proof that every conversational answer followed this path, but machine-readable output cannot express the requested opinion. |
| EXECUTION_ALLOWED=false suppresses buy/hold/wait opinion | PARTIALLY_CONFIRMED | Execution is hard-locked false, but no explicit if-statement says execution false must erase an opinion. The schema's missing opinion fields and single final gate create the same functional deficit. |
| Regime confirmation or trend checks are overly strict | PARTIALLY_CONFIRMED | The spec requires two observations; implementation immediately copies raw regime to confirmed regime. Data-connected historical evidence and threshold sensitivity are not available to prove too-strict numeric thresholds. |
| Thresholds are absent or cannot be computed | PARTIALLY_CONFIRMED | Stock-score documentation deliberately defers exact thresholds pending data/validation; market regime document says data connection pending. Execution thresholds and expected-return/valuation cutoffs are not part of the decision contract. |
| Required conditions must all pass, making valid windows disappear | PARTIALLY_CONFIRMED | DecisionAgent requires PASS for signal, permission, regime, risk and multiple evidence/source agents before RESEARCH_ONLY. Joint historical pass rate and opportunity duration were not computed. |
| Conservative defaults/fail-closed behavior perpetually produce no decision | CONFIRMED (architecture), NOT_TESTED (frequency) | The locked statuses and broad PIT short-circuit are visible. The percentage of user requests that end in no opinion has not been measured. |
| Pipeline stops before expected return, downside, horizon and concentration are evaluated | CONFIRMED | The output schema has no thesis/valuation/horizon/expected-return fields. RiskAgent only checks presence of MDD/MAE/stress-loss inputs and a concentration_ok boolean; it does not enforce numeric risk thresholds itself. |
| Response emits generic warnings instead of a concrete opinion | PARTIALLY_CONFIRMED | Opinion fields are absent in the API contract, so generic status-only output is possible. Full historical conversation responses and prompt templates were not available for a response-by-response audit. |

### 3.1 Root cause summary

The primary design defect is **single-plane decision output**: the system exposes permission state as the decision, rather than emitting a supported opinion and then attaching constraints. The primary safety defect is different: the market monitor can report a false green state from a wrong return horizon and cross-instrument freshness aggregation. Fixing one does not justify weakening the other.

A secondary risk-control gap is the current RiskAgent implementation. Supplying non-null MDD, MAE and stress_loss is enough for PASS unless concentration_ok is false; numeric limits are not evaluated in that class. The current global buy lock prevents this from authorizing a live order today, but the implementation must not be promoted under the assumption that it validates loss limits.

## 4. Case Reconstruction

### 4.1 Case 1 — TSMC NYSE ADR, two shares, 3+ year horizon

#### Historical conclusion versus available proof

The prior user-context summary says the prior answer viewed TSMC fundamentals/growth positively but returned BUY_ALLOWED=false and EXECUTION_ALLOWED=false. The exact old response transcript and its calculations were not available in the repository evidence collected for this audit. Therefore, the exact root cause of that answer is NOT_TESTED; the architecture's inability to formalize an independent opinion is CONFIRMED.

The correct conclusions are distinct:

- Long-term business quality: recent earnings evidence is positive, including reported Q3 2026 net income growth of 69% year over year and strong AI-related demand.
- Current valuation/entry attractiveness: NOT_READY from the evidence collected here. A price decline alone is not a valuation model; forward estimates, a normalized cash-flow/earnings range, and an explicit margin-of-safety framework were not calculated.
- Portfolio suitability: NOT_COMPUTABLE because a current multi-account holdings snapshot with semiconductor ETF look-through and factor-weight totals was not available.
- Immediate execution: NOT_ALLOWED under the frozen operating contract; recent TSM last-close data is not a verified order-time bid/ask quote, and real account cash, fees, FX spread and order terms were not loaded.

#### As-of calculation (not an executable quote)

Using the 2026-10-16 close USD 412.61 and 2026-10-19 FX close KRW 1,328.72/USD:

- Two-share gross value: USD 825.22, approximately KRW 1,096,486 before fees, FX spread and tax.
- A 5% / 10% / 15% / 20% fall in the USD share price would reduce that two-share position by approximately KRW 54,824 / 109,649 / 164,473 / 219,297, holding FX constant.
- A ±5% FX move would change the KRW value of the same USD 825.22 position by about KRW 54,824, holding the ADR price constant.
- The close fell about 7.30% from USD 445.12 on 2026-10-13 to USD 412.61 on 2026-10-16, and about 15.07% from USD 485.80 on 2026-10-05. These are observed historical price changes, not proof that valuation became cheap.
- Do not reuse the USD/KRW rate as an order-time rate. At order time, reconcile the FX timestamp, order currency, conversion direction and broker spread.

#### Minimum conditions for considering a first tranche

Do not invent a fixed price or percentage threshold before valuation work. A first tranche review is only meaningful after:

1. TSM quote and USD/KRW data are current, timestamped, and reconciled to independent sources; the actual order quote includes bid/ask.
2. A preregistered valuation range and downside assumptions exist, based on current available financials/forward estimates; the current price-to-value condition is explicitly stated.
3. Direct and ETF look-through semiconductor exposure across accounts is reconciled; Samsung Electronics' LOCKED status must not be treated as zero risk.
4. The available-cash snapshot, position cap and maximum tolerable KRW loss are known.
5. The Permission Engine has a valid, non-conflicting market/data state. It may return false and keep the proposed opinion visible.
6. Execution is separately checked at order time, including fees, FX spread, order type, market hours and price limits.

No evidence collected here proves those conditions all passed in the prior TSMC response. It would be incorrect to say the only blocker was price or the only blocker was data.

#### Required opinion/permission/execution output

| Field | Current audit result |
|---|---|
| Investment opinion | OPINION_PROVISIONAL — long-term candidate; do not classify current entry price as attractive until valuation and exposure are calculated. If forced to choose an action now: WAIT / first-tranche review after evidence reconciliation. |
| Opinion confidence | Low-to-medium: recent financial performance is sourced; valuation, current quote and total portfolio exposure are incomplete |
| Current price state | NOT_READY for entry-price judgement; observed close is available, but current valuation and order quote are not |
| BUY_ALLOWED | false — frozen global research lock; additionally, permission evidence is not established as passed |
| EXECUTION_ALLOWED | false — frozen execution lock and no order-time/account checks |
| Specific blockers | Promotion disabled; no opinion schema; no validated current valuation; no reconciled semiconductor look-through; no order-time quote/cash/fee/FX check |
| Allowed transition | Only after valuation range, price threshold and downside case are preregistered; quotes reconcile; portfolio limit passes; the separate execution contract later passes an explicitly approved promotion |
| Reassessment | At the next verified US regular-session quote after current valuation and holdings refresh; immediately if quote sources conflict or the investment thesis is impaired |
| Thesis invalidation | Material deterioration in process/technology competitiveness, customer demand or capital economics; sustained margin/cash-flow erosion versus a documented baseline; Taiwan geopolitical disruption beyond the predeclared stress budget |
| Downside sensitivity | KRW 54.8k–219.3k for 5%–20% USD price declines on two shares at fixed FX; not a probability forecast and excludes fees/FX variation |
| Unknowns | Valuation range, analyst-estimate vintage, full portfolio weights, semiconductor ETF constituents, max KRW loss budget, broker fee/spread, live bid/ask |

The appropriate system behavior is not to output BUY_ALLOWED=false and stop. It is to preserve the provisional long-term opinion, explicitly say current entry attractiveness is not evaluated, and keep permissions false.

### 4.2 Case 2 — SK hynix add-buy / sell review

#### Known transaction fact from user context

- A single share was reportedly bought at KRW 1,271,000 and sold at KRW 1,302,000 the following day.
- Gross price difference: KRW 31,000, or approximately +2.44% on the entry price, before fees and any applicable tax.
- This one completed trade is not evidence of a repeatable trading edge and does not validate any entry rule.

Third-party historical pages report a steep move around the episode: the 2026-10-15 closing price is shown near KRW 1,262,000 (-11.06%) and 2026-10-16 near KRW 1,272,000 (+0.79%) by one source. Providers retrieved for 2026-10-19 do not agree on the displayed/current closing value (roughly KRW 1.252M–1.262M). These cross-source differences need reconciliation before using an exact current entry price.

#### Alternatives using the historical KRW 1,271,000 entry as a sensitivity anchor

| Choice | Initial capital, assuming unchanged price | Share of the then-mentioned KRW 25M cash | Loss at -10% | Loss at -20% |
|---|---:|---:|---:|---:|
| Buy 1 share | KRW 1.271M | 5.08% | KRW 127,100 | KRW 254,200 |
| Buy 5 shares immediately | KRW 6.355M | 25.42% | KRW 635,500 | KRW 1,271,000 |
| Buy 1 share per day for 5 sessions | About KRW 6.355M if price is unchanged; actual cost depends on each fill | About 25.42% if unchanged | Cannot be calculated without the five entry prices; a flat-price approximation equals five-share lump sum | Cannot be calculated without the five entry prices; a flat-price approximation equals five-share lump sum |

The KRW 25M cash figure was reported at the time; it is not verified as the current available balance. These calculations compare size under an explicit unchanged-price assumption; they are not purchase instructions or a claim about future drawdown probability.

#### Trade-off

- One share: limits immediate capital at risk and preserves optionality, but still adds to the same semiconductor factor and can be a poor entry if the shock continues.
- Five shares immediately: increases exposure and drawdown sensitivity in one step. A 10% decline consumes KRW 635,500; a 20% decline consumes KRW 1.271M, before costs.
- One share daily: can reduce dependence on one intraday price if entry prices vary, but it does not guarantee a lower average cost, reduce underlying sector concentration, or prevent accumulating throughout a persistent downtrend. The schedule should stop automatically when a preregistered data/risk gate fails; it must not continue buying just because the calendar says so.
- The observed +2.44% gross exit is an outcome, not evidence that the entry decision was well-calibrated at the time. Evaluate using the ex-ante signal and alternative paths, not only the realized trade.

#### Current structured judgement

| Field | Current audit result |
|---|---|
| Investment opinion | WAIT / incremental-buy review only after exposure and data reconciliation |
| Opinion confidence | Low: transaction prices are known from user context; current factor weights, fundamentals, technical D/W/M state and exact quote are incomplete |
| Current price state | DATA_NOT_READY for execution due cross-provider price discrepancy |
| BUY_ALLOWED | false |
| EXECUTION_ALLOWED | false |
| Specific blockers | Frozen locks; market/quote-integrity gate; no verified current multi-account position and ETF look-through; no predeclared maximum position/sector stress budget |
| Allowed transition | Reconcile close/quote sources and timestamps; verify current holdings and cash; compute total Korean semiconductor exposure and -10%/-20% stress; require an explicitly defined signal and max position |
| Reassessment | Next verified KRX session, after source reconciliation; sooner after another market-wide shock or a company-specific thesis change |
| Thesis invalidation | Long-term earnings/capacity economics worsen beyond a documented baseline; competitive/technology position degrades; portfolio stress exceeds the approved survival budget |
| Downside sensitivity | Use share-count × executable price × chosen shock; the 1-/5-share historical-anchor figures above show exposure scaling, not forecast |
| Unknowns | Current holdings and account-level sellability; whether semiconductor ETFs overlap; current quote consensus; risk budget; D/W/M technical structure; costs and exact execution timestamps |

### 4.3 Case 3 — Market selloff and quote-quality warning

Issue #27 records the following mismatch for the 2026-10-12 close:

| Instrument | Monitor result | Reported session result | Absolute mismatch |
|---|---:|---:|---:|
| KOSPI | -0.377% | -3.65% | 3.273 percentage points |
| KOSDAQ | -0.435% | -4.83% | 4.395 percentage points |
| Samsung Electronics | -0.299% | -4.39% | 4.091 percentage points |
| SK hynix | -0.496% | -4.52% | 4.024 percentage points |

The same monitor reported DATA_QUALITY=GREEN and freshness_min around 0.152 because the freshest timestamp came from USD/JPY, although critical Korean observations were much older. Root cause confirmed in main: the return field uses the last two 5-minute bars, and aggregate freshness uses the maximum timestamp over the universe.

This is a justified hard block for market-trigger promotion and orders. It is not a reason to discard an independently supported long-term thesis. During a crash, the output should show two separate statements:
- Market-wide permission: BLOCKED / BUY_ALLOWED=false because the critical market quote state is unresolved or stress state is severe.
- Asset opinion: preserve a supported HOLD / WAIT / RISK_REDUCTION_REVIEW opinion only if the asset's own price/fundamental/portfolio inputs meet the relevant evidence requirements; otherwise mark only the affected sub-question DATA_NOT_READY.

#### Re-entry after data repair

Required before market permission is reconsidered:
1. Merge and verify PR #30 or equivalent remediation on main.
2. Emit distinctly named 5-minute, validated 15-minute and prior-session close-to-close returns; preserve both endpoint timestamps and price basis.
3. Validate freshness per instrument, required group and market session. A fresh FX symbol cannot mask stale indices/leaders.
4. Reconcile headline/last price, bid/ask, range, prior close, timestamp and trusted independent reference within a preregistered tolerance.
5. Run the regression fixtures from Issue #27 and Issue #31 in CI.
6. Recompute breadth, foreign/institutional flows and cross-asset risk on the same as-of clock; do not treat RSI, a one-day bounce or a single oversold reading as confirmation.
7. Keep BUY_ALLOWED=false and EXECUTION_ALLOWED=false until independent permissions and the later promotion contract are satisfied.

## 5. Gate Feasibility Matrix

"Feasibility" and "empirical frequency" are different. A rule can be logically satisfiable but still fail frequently in real markets; no observed pass-rate estimates are produced without replaying point-in-time data.

| Gate / condition | Purpose | Current rule/input status | Feasibility category | Frequency / duration | Required next validation |
|---|---|---|---|---|---|
| Opinion Engine | Answer asset attractiveness and suitable action | Not separately implemented in decision schema | Requires redesign regardless of market state | NOT_COMPUTABLE | Contract test: valid asset evidence must yield an opinion even if permission is false |
| PIT/provenance | Block look-ahead, missing series and unverifiable claims | Availability/provenance checks exist; age/staleness semantics are incomplete in DataPITAgent | Realistically satisfiable once source contract is complete; currently incomplete | NOT_COMPUTABLE | Per-series PIT/freshness fixtures, missing-value/source-id checks and replay |
| Market quote quality | Prevent wrong horizon/stale data from producing GREEN | Main fails Issue #27 contract; PR #30 is a draft | Safety-critical; normal pass frequency unknown | NOT_COMPUTABLE | Merge candidate remediation, run regression tests against frozen snapshot |
| Regime composite | Summarize trend/breadth/risk/macro/cross-asset | Market Regime V1 states data connection pending; weights are research baselines | Computable if all required series exist; empirical validity unproven | NOT_COMPUTABLE | Same-timestamp historical vector, correlation clustering, walk-forward and regime sensitivity |
| Regime persistence | Avoid false transient transitions | V1 says two consecutive observations; current agent directly confirms raw state | Specification/implementation mismatch | NOT_COMPUTABLE | Transition fixtures, false-transition count and response-lag measure |
| Permission | Block buys under bad market/macro/geopolitics/data | Market RED or DATA_NOT_READY blocks; global buy lock always false | Research PASS may be possible; live permission intentionally unavailable | Code-level live BUY_ALLOWED=true frequency = 0 under current constant; market permission pass rate NOT_COMPUTABLE | Separate simulated permission decision from immutable live kill switch; measure joint conditions |
| Risk | Quantify MDD/MAE/stress loss/concentration | RiskAgent checks missing inputs; it does not apply numeric maximums | Structurally incomplete | NOT_COMPUTABLE | Implement versioned risk-limit rules and test severe but non-null values |
| Evidence/source quality/conflict/hallucination | Prevent unsupported/fabricated claims | Multiple agents exist; each status can block final decision | Rare or frequent pass unknown | NOT_COMPUTABLE | Source completeness and conflict-resolution replay; report individual and joint pass rates |
| Portfolio concentration | Aggregate direct and look-through factor exposure | Policy specifies method; audited holdings/constituents unavailable for these cases | Data-dependent, currently unverified | NOT_COMPUTABLE | Reconcile account ledger, LOCKED holdings, currency provenance and PIT ETF constituents |
| Execution | Verify live quote, cash, FX, fees, order form and session | Hardcoded false; no corresponding execution fields in v0.1 schema | Live execution intentionally disabled; actual execution feasibility NOT_TESTED | Code-level EXECUTION_ALLOWED=true frequency = 0 under current constant | Later separate execution contract and human approval; do not change during opinion fix |
| HOTL/persistence | Record approval, fill, realized result and corrective action | Issue #31 OPEN; document notes persistence requirement | Requires workflow integration | NOT_COMPUTABLE | Stable run key, immutable initial hypothesis, append-only outcome and receipt tests |

### 5.1 Conditions that can realistically pass versus those that cannot yet be evaluated

- Realistically satisfiable in ordinary markets once connected: source timestamps/provenance, complete regime axes, a valid asset signal, price/FX quote reconciliation, portfolio-ledger reconciliation.
- Rare but valid by purpose: severe-stress override and hard data-quality blocks. Do not weaken these for convenience.
- Unknown frequency: simultaneous PASS for market regime, signal, risk, evidence, retrieval, source quality, conflict and hallucination controls. No joint-rate estimate exists.
- Structurally difficult: PIT failure currently fans out to all downstream agents; no separate opinion status exists; live permission and execution are hard-coded false.
- Requires redesign regardless of observed frequency: numeric risk thresholds, regime confirmation parity, opinion/permission/execution output separation.

### 5.2 Current test/replay metrics

All empirical gate rates and strategy metrics below are NOT_COMPUTABLE from this audit run:

- Opinion-ready / opinion-provisional coverage.
- BUY_ALLOWED=true and EXECUTION_ALLOWED=true rates under any proposed promoted architecture.
- DATA_NOT_READY and BLOCKED proportions by asset and gate.
- Individual-gate and all-gates-joint pass rates.
- Number and duration of valid opportunities, detection lead time and delay after conditions pass.
- Entry MDD, MAE, 95% CVaR/expected shortfall, stress loss, recovery duration, turnover, cash drag and avoidable re-entry trades.
- Net performance after fees, taxes, spreads, slippage, FX and execution timing.
- Relative performance against price/total-return benchmarks and cash.
- Results across 2000, 2008, 2020, 2022 and 2025–2026 across rising, range-bound, falling, low-volatility and fast-rebound environments.

Required missing inputs include point-in-time universe/history (including delisted securities), price/volume and corporate actions, breadth and sector data, investor flows, rates/FX/volatility/credit data, source publication/availability timestamps, holdings/ETF constituents, versioned costs, and a realistic order/fill convention. Do not substitute current constituents or revised fundamentals into historical decisions.

## 6. Decision Architecture

### 6.1 Required independent outputs

| Layer | Output | What it can block | What it must not erase |
|---|---|---|---|
| L1 Opinion Engine | OPINION_READY / OPINION_PROVISIONAL / DATA_NOT_READY, plus BUY_REVIEW / STAGGERED_BUY_REVIEW / HOLD / WAIT / REDUCE_REVIEW / SELL_REVIEW / ABSTAIN | The affected opinion field when thesis-critical evidence is missing or contradictory | Independently supported claims outside the unavailable data scope |
| L2 Permission Engine | BUY_ALLOWED=true/false with reason codes | New-buy permission for market, data-quality, risk-budget, portfolio and strategy violations | L1 opinion text and confidence; a blocked buy can coexist with WAIT/HOLD |
| L3 Execution Gate | EXECUTION_ALLOWED=true/false with order blockers | Specific order transmission on stale quotes, invalid cash, fee/FX uncertainty, out-of-session or unapproved order | L1 and L2 explanations |
| L4 HOTL | APPROVE / REJECT / DEFER; actual order/fill and outcome receipts | Human approval and external execution | Immutable prior opinion, source snapshot, code/config/rule versions, post-trade evaluation |

The existing operational hard lock remains external to the opinion schema. Promotion is a separate, explicit, reviewed process; neither opinion output nor a backtest PASS can change permission by itself.

### 6.2 Opinion quality must be scoped

Examples of valid output:
- Long-term business thesis: provisionally favorable; current entry valuation NOT_READY; BUY_ALLOWED=false.
- Asset attractiveness favorable, but current price above the preregistered value range: WAIT; BUY_ALLOWED=false; reason PRICE_NOT_IN_ENTRY_ZONE.
- Thesis favorable, but semiconductor exposure exceeds the approved factor budget: HOLD / WAIT; BUY_ALLOWED=false; reason FACTOR_CONCENTRATION_LIMIT.
- Price is down substantially, but valuation estimate is unavailable: current-price attractiveness NOT_READY, not "cheap."
- Data-quality conflict affects live execution but long-term public filings remain valid: preserve the long-term thesis and block order-time judgement.
- Thesis evidence itself is missing, contradictory or stale: OPINION status DATA_NOT_READY; do not fabricate a favorable or unfavorable action.

### 6.3 Minimum structured opinion contract

Add a versioned contract (do not silently mutate v0.1). Suggested fields:

- opinion_status, opinion_class, asset/instrument, investment_horizon, as_of, valid_until
- thesis_summary, supporting_evidence_refs, counter_evidence, thesis_invalidation_conditions
- valuation_method/version, value_range and price_state; null plus blocker when not computed
- expected_return_range only when model/data support it; assumptions and horizon mandatory
- downside_scenarios with shock assumptions, absolute currency loss and percent loss; mark missing inputs explicitly
- confidence level and confidence rationale
- reassessment_at / reassessment_triggers
- BUY_ALLOWED, permission_blocker_codes
- EXECUTION_ALLOWED, execution_blocker_codes
- source/data-quality state and unresolved_items
- code/config/data snapshot IDs, source timestamps, model/calculation version and HOTL receipt reference

Keep the v0.1 schema intact until migration, compatibility tests and versioned rollout are approved.

## 7. Backtest and Replay Plan

### 7.1 Freeze first

- Freeze the current main commit and call it BASELINE_B0_OPINION_AUDIT_2026-10-19. Do not relabel or mutate EXPERIMENT_B0_ENGINE_2026-10-16.
- Preserve BUY_TRIGGER_B0_NO_BUY as the no-buy permission state. The two identifiers must not be combined.
- Keep the live locks false in all A–D experiment runs.
- Freeze the dataset manifest, source/vintage hashes, exchange calendar/session, code/config versions, cost assumptions and decision timestamps before replay.

### 7.2 Required replay universe and regimes

Use point-in-time series for 2000 tech bust, 2008 financial crisis, 2020 crash/rebound, 2022 rate/asset repricing and verified available parts of 2025–2026. If an asset or input has no valid history, report coverage gaps rather than substituting a proxy silently. Include uptrend, range-bound, sustained selloff, low volatility and sharp rebound windows.

Minimum inputs: point-in-time asset universe and security master; close/adjusted/raw price bases; bar timestamps; volume/liquidity; sector and breadth; available-at investor flows; fundamentals/filing publication time; FX/rates/volatility/credit series; holdings and PIT ETF look-through; source quality/conflict data; costs and fills.

### 7.3 Experiments

| Variant | Change | Invariants |
|---|---|---|
| Baseline | Existing decision output and current gates | Frozen code/config; BUY_ALLOWED=false; EXECUTION_ALLOWED=false; PROMOTION=DISABLED |
| Experiment A | Add opinion generation independent of permission | Same risk, data and execution gates; no promotion |
| Experiment B | Keep independent long-term opinion when live-market data is bad, while blocking price-timing/permission/execution fields | Any affected current-price conclusion stays DATA_NOT_READY; no quote repair by imputation |
| Experiment C | Add explicit reassessment triggers and maximum review age per input type | No fixed max-wait value chosen without data; trigger and expiry semantics tested first |
| Experiment D | Classify hard versus advisory conditions and separate independent evidence dimensions | All existing safety-critical conditions remain hard; no threshold/weight changes without separate research |

### 7.4 Required measurements

1. Opinion coverage and status mix, by instrument and evidence grade.
2. BUY_ALLOWED and EXECUTION_ALLOWED frequencies, including exact blocker-code attribution.
3. Per-gate and joint pass rates; duration of valid windows.
4. Signal-to-opinion and opinion-to-permission latency; opportunities missed because data was stale or a gate reset improperly.
5. Entry MDD, MAE, MFE, worst forward return, 95% expected shortfall, stress loss, time underwater and recovery duration.
6. Turnover, cash drag, opportunity cost, fees/taxes/spread/slippage, price-limit/halting effects and capacity.
7. Benchmark comparison on identical timestamps and return conventions.
8. Calibration of opinion confidence and the rate of thesis invalidation / opinion revision.
9. Sensitivity to parameter variation, source selection and data gaps; all tried variants must be counted.
10. Survival and tail-risk breaches; positive CAGR cannot offset a critical integrity failure.

Use chronological train/validation/OOS and walk-forward folds. Freeze thresholds before examining OOS, preserve negative cases, and apply a preregistered multiple-testing control. No backtest metrics are produced in this report.

### 7.5 Acceptance and failure interpretation

A higher opinion coverage rate is not automatically success. Experiment A/B passes only if it produces a grounded, scoped opinion where evidence suffices, preserves explicit unknowns, and never increases permissions. A–D fails if any future data leaks, a stale/conflicting quote is used for live timing, a numeric risk violation passes, or a research result changes the live locks.

## 8. Rule Change Proposal

### Proposal R-01 — Separate Opinion from Permission and Execution

**FINDING**  
The v0.1 contract does not represent an investment opinion independently.

**EVIDENCE**  
DecisionGateAgent has only DATA_NOT_READY/BLOCKED/RESEARCH_ONLY. The schema has no opinion fields and enforces both permission flags as false. Tests assert these locks and do not require a user-facing opinion field.

**ROOT_CAUSE**  
The gate owns both readiness and final decision semantics; a blocked permission status becomes the only visible conclusion.

**COUNTERMEASURE**  
Add a versioned opinion contract and separate L1/L2/L3 outputs. Keep existing permission/execution locks and frozen B0 baseline unchanged.

**TEST**  
Valid thesis evidence + permission BLOCKED => opinion still emitted, BUY_ALLOWED=false, EXECUTION_ALLOWED=false. Missing thesis-critical evidence => OPINION status DATA_NOT_READY. Stale quote + valid public filings => long-term opinion may remain but current entry/ execution data remains NOT_READY.

**ACCEPTANCE_CRITERIA**  
100% of deterministic contract fixtures preserve the independent opinion and permission results exactly; schema validation passes; no research-only result can flip either locked permission.

**ROLLBACK_CONDITION**  
Any opinion/permission coupling reappears, blockers disappear, or research state can affect live permissions. Roll back the new adapter/schema version while keeping the old v0.1 contract and locks.

**FILES / CI / ISSUE**  
src/investment_pipeline/decision_gate.py; src/investment_pipeline/multi_asset_subagents.py; schemas/multi_asset_decision_v0.1.schema.json (do not mutate silently; create v0.2); tests/test_decision_gate.py; tests/test_multi_asset_subagents.py; new output-contract tests; GitHub Issue #35.

### Proposal R-02 — Scope data failures to the affected conclusion

**FINDING**  
PIT failure fans out DATA_NOT_READY to all downstream agents.

**EVIDENCE**  
The orchestrator PIT failure branch returns DATA_NOT_READY for signal, permission, regime, risk, evidence, retrieval, source quality, conflict and hallucination outputs.

**ROOT_CAUSE**  
The data gate is treated as a whole-pipeline short circuit rather than a scoped evidence dependency.

**COUNTERMEASURE**  
Define an input dependency matrix per output field. Keep the hard execution/market timing block for critical missing data, but allow L1 to evaluate only those independent conclusions whose own sources pass. A failed input is never imputed or treated as zero.

**TEST**  
- Missing TSM live bid/ask + valid filing/financial evidence: thesis can be returned, price state DATA_NOT_READY, both permissions false.
- Missing core financials/fundamental vintage: thesis opinion DATA_NOT_READY.
- Future available_at or absent source provenance: no downstream claim may use that row.
- Quote conflict: data quality AMBER/RED; buy and execution stay false.

**ACCEPTANCE_CRITERIA**  
Zero look-ahead leaks; zero stale/conflicting inputs contributing to an executable price; all scoped readiness fields map to explicit blocker codes; no failed critical data is imputed.

**ROLLBACK_CONDITION**  
Any field receives a value whose required input did not pass its dependency gate, or an execution permission becomes true on a quote-integrity failure.

**FILES / CI / ISSUE**  
multi_asset_subagents.py; PIT/source quality tests; schema v0.2; Issue #35 and Issue #31.

### Proposal R-03 — Complete numeric risk-limit evaluation

**FINDING**  
RiskAgent only checks whether MDD/MAE/stress-loss fields are non-null and whether concentration_ok is false.

**EVIDENCE**  
A non-null set of severe risk values may produce PASS because no numeric threshold is checked in the class. concentration_ok defaults true.

**ROOT_CAUSE**  
Input presence is mistaken for risk assessment.

**COUNTERMEASURE**  
Make thresholds explicit, versioned and separately validated per strategy/asset; missing thresholds mean DATA_NOT_READY. Do not invent limits during this audit and do not promote until limits have a risk-owner approval.

**TEST**  
Boundary tests for each approved threshold; severe losses outside limits block permission; absent threshold version blocks permission; false concentration result blocks; default behavior never assumes concentration is acceptable when the required value is missing.

**ACCEPTANCE_CRITERIA**  
100% of limit boundary and missing-limit fixtures match the versioned specification. Every permission outcome records threshold version, measured values, comparison and blocker code.

**ROLLBACK_CONDITION**  
An unversioned threshold enters production, missing limit defaults to pass, or prior approved risk contracts are changed without validation.

**FILES / CI / ISSUE**  
src/investment_pipeline/multi_asset_subagents.py; tests/test_multi_asset_subagents.py; tests for risk limits; config/schema versioning; issue linked from #35.

### Proposal R-04 — Reconcile regime confirmation contract

**FINDING**  
The current RegimeAgent sets confirmed_regime equal to raw_regime immediately.

**EVIDENCE**  
The code path has no prior-state input or persistence counter, while MARKET_REGIME_ENGINE_V1.md describes two consecutive observations for a transition except the stress override.

**ROOT_CAUSE**  
The implementation does not enforce the documented state transition rule.

**COUNTERMEASURE**  
Implement versioned persistence state or explicitly mark confirmed_regime unavailable until the required history is provided. Do not adjust score weights or thresholds.

**TEST**  
Single-sample regime flip does not confirm; second consecutive eligible observation confirms; R6 stress override follows separately specified conditions; stale or missing observations do not advance persistence.

**ACCEPTANCE_CRITERIA**  
Code, schema, docs and replay use the same state-transition table; false-transition and confirmation-lag metrics are reported before promotion.

**ROLLBACK_CONDITION**  
Raw state is silently labelled confirmed without the required evidence, or a changed threshold is introduced within the persistence fix.

**FILES / CI / ISSUE**  
multi_asset_subagents.py; tests/test_multi_asset_subagents.py; MARKET_REGIME_ENGINE_V1.md; new regime transition tests.

### Proposal R-05 — Merge and prove market monitor remediation

**FINDING**  
Main's monitor still has wrong return horizons and cross-instrument freshness behavior.

**EVIDENCE**  
Issue #27 is open; main poll.py uses adjacent 5-minute bars, the freshness maximum is global, and PR #30 remains draft/unmerged.

**ROOT_CAUSE**  
A remediation candidate has not been promoted to main and all required acceptance checks have not been re-confirmed on main.

**COUNTERMEASURE**  
Review PR #30 against current main, resolve merge-base drift, verify its required-series/freshness behavior and regression fixtures, then merge only after its review and CI acceptance. Keep permission locks false.

**TEST**  
The Issue #27 2026-10-12 discrepancy fixture; fresh USD/JPY with stale Korean indices/leaders; missing prior session close; missing/out-of-order 15-minute bars; timezone, holiday and session-boundary fixtures; headline-vs-bid/ask conflict; matching source timestamp/price basis.

**ACCEPTANCE_CRITERIA**  
Separate 5m/15m/session-daily returns; per-series/group freshness; stale critical inputs never produce aggregate GREEN; all targeted CI checks pass on the merged main commit.

**ROLLBACK_CONDITION**  
Any regression permits stale/missing/conflicted required series to produce GREEN or to promote BUY_TRIGGER. Revert the monitor implementation while keeping trading locks false.

**FILES / CI / ISSUE**  
scripts/market_monitor/poll.py; config/market_monitor.json; tests/test_market_monitor.py; .github/workflows/market-monitor.yml and/or collectors-ci.yml; Issue #27; Draft PR #30; Issue #31.

## 9. Acceptance Criteria

### 9.1 Functional

- A supported Opinion Engine result is available independently of permission and execution.
- L1 distinguishes insufficient evidence for the thesis from insufficient data for today's price or order.
- Permission blockers are specific, versioned, and visible; they do not erase the investment view.
- Execution checks real order-time inputs, but this audit does not implement live order transmission.
- HOLD/WAIT/REDUCE_REVIEW is a valid successful opinion; absence of a buy signal is not an output failure.
- The output includes evidence, counter-evidence, confidence, downside assumptions, invalidation and reassessment triggers.

### 9.2 Safety

- BUY_ALLOWED=false, EXECUTION_ALLOWED=false, PROMOTION=DISABLED remain fixed throughout this documentation/audit branch.
- Future available_at, missing provenance, stale/conflicted required quotes, missing risk limits, or invalid fill timing cannot pass the relevant gate.
- EXPERIMENT_B0_ENGINE remains a research comparator, and BUY_TRIGGER_B0_NO_BUY remains a no-buy permission state. No alias or auto-promotion is allowed.
- Locked holdings remain in factor/stress exposure and do not create automated sell permission.
- Thresholds/weights are not changed unless a separate preregistered experiment validates them.

### 9.3 Empirical

- Report, rather than presuppose, gate pass rates and opportunity duration.
- Run the exact same data, evaluation timestamps, fees and fill assumptions for Baseline and A–D.
- Keep the current report's backtest performance fields NOT_COMPUTABLE until PIT and M1 are GREEN.
- Do not adopt numerical target coverage or "desired buy rate" before baseline measurement. The success criteria are evidence quality, no unsafe promotions, decision-quality improvement and acceptable tail risk—not more buys.

## 10. Final Questions and Answers

1. **Main cause of repeated missing opinions?** Confirmed contract-level cause: the final decision output encodes readiness/permission only and has no separate opinion fields. PIT failure also suppresses downstream outputs. Historical response-by-response causal attribution remains partially untested.
2. **Necessary safety block or overblocking?** Mixed. Market quote quality and execution blocks are necessary under Issue #27. Erasing independent thesis/valuation analysis because an execution quote or permission gate fails is structural overblocking.
3. **Can current structure detect normal-market buy opportunities?** It can compute research signal/regime fields for supplied inputs, but the current API does not express a full asset opinion; permissions are locked false, the market monitor defect remains on main, and no validated historical joint-pass frequency is available. Operationally, it is not currently approved for live buy-opportunity execution.
4. **When can an opinion be generated?** When evidence adequate for the requested conclusion is sourced, PIT-valid, consistent and sufficiently complete. An opinion can be provisional if only non-critical aspects such as live execution quotes or portfolio snapshots remain unresolved; the affected fields must remain unknown.
5. **When can BUY_ALLOWED become true?** Not on this branch. Only after approved versioned permission/risk contracts, the M1 data-quality gate, point-in-time replay/OOS/robustness, portfolio risk, and explicit promotion approval. No numerical gate thresholds are inferred here.
6. **When can an order execute?** Only after permission is separately true under an approved contract and the order-time quote/bid-ask, market/session, available cash, order amount/type/limits, FX, spread, fees/tax and account holdings are verified, with required HOTL approval. Current EXECUTION_ALLOWED remains false.
7. **Are these conditions empirically validated?** Some unit contracts exist, and PR #30 has successful test/backtest/test-history checks on its unmerged branch. Main remains unpatched for Issue #27. Full historical joint-gate, strategy OOS and opportunity-delay metrics are not computed in this audit.
8. **First fix and new risk introduced?** First add opinion/permission/execution separation and a versioned contract while preserving all locks. The new risk is false confidence or unsupported provisional opinions; control it with scoped dependencies, evidence/counter-evidence, explicit confidence and tests proving that opinion output never mutates permissions.
9. **When should buys remain disallowed after improvement?** Conflicted/stale critical market data, unresolved quote/FX, missing risk limits, excessive factor concentration, failed thesis/value conditions, incomplete order inputs, unacceptable downside budget, unapproved human review or disabled promotion.
10. **Next action?** Work Issue #35 (opinion contract) and Issue #27/#30/#31 (data integrity and workflow) as separate scoped changes. First reconcile/merge the quote-horizon fix; in parallel design v0.2 output contract and tests. Run point-in-time replay only after M1 is GREEN. Keep all live locks false until independent promotion review.

## 11. Git / Artifact Plan

- Audit report: docs/investment/INVESTMENT_OPINION_GATE_AUDIT_V1_2026-10-19.md
- Handoff: docs/governance/HANDOFF_INVESTMENT_OPINION_GATE_AUDIT_2026-10-19.md
- Opinion/permission separation: GitHub Issue #35
- Market monitor horizon/freshness: Issue #27 and draft PR #30
- Deterministic workflow/HOTL persistence: Issue #31
- Do not merge directly to main during audit; keep documentation on a review branch and submit a PR.
- Expected code/testing work in later implementation: versioned v0.2 contract, Opinion Engine and output schema, risk-limit implementation, regime persistence tests, quote-quality regression fixtures and CI.
- No operational code, thresholds, buy permissions, or execution permissions were changed by this audit.
