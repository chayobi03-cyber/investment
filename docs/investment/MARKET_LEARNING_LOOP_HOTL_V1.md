# Market Learning Loop & HOTL Governance V1

- Status: PROPOSAL — schema and runtime integration are not yet deployed
- Date: 2026-10-13
- Owner: Investment system / decision-control plane
- Scope: Market monitor, market-regime analysis, entry-timing forecasts, post-hoc evaluation, root-cause analysis, and human-approved rule governance

## 1. Objective

Create a durable closed loop that improves the consistency of market analysis without allowing the system to silently rewrite its own live decision rules.

**Observe → Freeze the as-of view → Record forecast and permission → Settle outcomes → Evaluate error → Diagnose causes → Test countermeasures → Human review → Shadow release → Approved promotion or rollback.**

A failed forecast is a learning sample, not an instruction to change a threshold. Every proposed change must identify the evidence, explain the failure mode, demonstrate a measurable benefit, and pass the same or stricter risk controls as the current rule set.

## 2. Existing baseline and gap

The current market monitor in **scripts/market_monitor/poll.py** collects quotes, derives compact market states, detects state deltas, and writes the latest object to **runtime/market_state.json**. The GitHub Actions workflow persists that current-state file on the **runtime/market-state** branch and uploads an artifact with a seven-day retention period.

The repository also contains a **Historical DB v1** module in `src/investment_pipeline/history/`. It provides append-only CSV files for market snapshots, stock snapshots, decisions and outcomes, plus a live-review adapter. That is useful reusable groundwork, but it is a file-backed store rather than a relational DB; current tests exercise it with temporary directories, and the market monitor does not yet persist its run envelope into that store or a dedicated history branch.

The gap is therefore **not "no history code exists"**. The gap is that live market-monitor observations, versioned horizon semantics, forecast records, matured outcomes, diagnoses, evaluations and HOTL governance events are not yet connected into one persisted lifecycle. Extend/reuse the Historical DB v1 contracts for a low-cost bootstrap instead of duplicating its existing market/stock/decision/outcome semantics. Keep the PostgreSQL proposal in `db/proposals/` as a future migration target after the data contract and usage patterns are proven.

Do not repurpose the latest-state file as the source of truth. Treat it as an operational cache and ingest eligible run envelopes into an independent append-only ledger with idempotency and durable branch/storage semantics.

## 3. Non-negotiable invariants

1. **Point in time:** Every decision input must have **available_at <= analysis_asof**. A later publication, corrected value, or revised history cannot leak into a past decision.
2. **Immutable history:** Do not overwrite prior market snapshots, forecasts, outcome measurements, diagnoses, evaluations, or human decisions. Corrections create a new revision linked to the prior record.
3. **No synthetic certainty:** Missing or stale data remain missing and carry a reason code. Null is never silently converted to zero, neutral, or a positive status.
4. **Forecast/action separation:** A forecast is not a permission, and a permission is not an execution. Store each separately.
5. **Fail closed:** Incomplete PIT evidence, stale required data, schema violations, or unresolved material conflicts lead to **DATA_NOT_READY** or **BLOCKED**, not a best-guess BUY.
6. **Human-on-the-loop:** Agents may collect, evaluate, explain, and propose. Activation of a rule, threshold, weight, or decision-policy change requires an explicit human governance event.
7. **No live self-modification:** Model or rule changes never become active because an LLM says they are better or because an in-sample metric improved.
8. **Reproducibility:** Each run pins code SHA, configuration version, rule-set version, prompt/template version where applicable, data manifest hash, and calculation version.
9. **Idempotency:** Retrying a job with the same idempotency key must not create duplicate logical runs or forecasts.
10. **Decision-plane isolation:** Code-generation agents stay outside the decision plane. Data-quality, PIT, regime, permission, signal-decomposition, risk, evidence-quality, conflict, hallucination, and final DecisionGate controls remain independent gates.
11. **Separation of horizons:** Intraday alerts, trading-session horizons, and calendar-day stress horizons are different units and must never be mixed in evaluation metrics.

## 4. Target architecture

- **Collector:** Existing market monitor and future market/sector/asset collectors. Capture source timestamps and failures, not just final labels.
- **Envelope validator:** Verify the run schema, hashes, required fields, temporal invariants, and hard decision flags before persistence.
- **History store:** Reuse the existing Historical DB v1 file-backed adapter for the first controlled write path, with the market-run envelope/ledger stored durably and idempotently. Keep the proposed PostgreSQL schema as a migration path once a dedicated investment database is selected. Normalized data should use typed columns in relational storage; large raw downloads remain in content-addressed artifacts referenced by URI and SHA-256.
- **Forecast ledger:** Save the forecast exactly as emitted at the decision timestamp, including probability/expected-return fields where available, horizon definition, rule version, uncertainty, and permission state.
- **Outcome settler:** Join forecasts to later realized data only after their due horizon. Use adjusted prices/total-return methodology appropriate to the asset; retain source and calculation versions.
- **Evaluation engine:** Produce direction/calibration, event detection, risk and path metrics, segmented by regime and horizon.
- **Root-cause analyst:** Generate ranked hypotheses with direct evidence references and confidence. Distinguish confirmed defects, plausible causes, and unknown causes.
- **Countermeasure lab:** Convert a diagnosis into a falsifiable hypothesis, baseline, target metric, holdout plan, acceptance criteria, and rollback criteria.
- **HOTL governance gate:** A person reviews the evidence and decides reject/defer/shadow-approve/release/rollback. Each decision is append-only and attributable.
- **Monitor/UI:** Show exceptions, state deltas, matured outcomes, root-cause candidates, unresolved data, and human decisions. Default to delta-first summaries; detailed evidence is opened by ID.

## 5. Canonical data objects

| Object | Grain | Why it exists |
|---|---|---|
| Market run | One collection/analysis attempt | Freeze timestamp, input digest, code/config versions, quality and result |
| Evidence observation | One source × series × observation timestamp × revision | Preserve provenance, publication/availability timestamps and raw value/hash |
| Dimension score | One run × dimension | Record Trend, Breadth, Risk, Macro/Rates-Liquidity, Cross-Asset, Energy, FX and Geopolitics independently |
| Forecast | One run × subject × target × horizon × model/rule version | Freeze what was predicted, confidence and permission at that time |
| Outcome | One forecast × evaluation-calculation version | Record realized return, benchmark excess, MAE/MFE, target/event result, and data sufficiency |
| Diagnosis | One identified error/incident | Separate cause category, evidence, causal hypothesis, counterfactual and confidence |
| Countermeasure | One proposed intervention | Pin the proposed change and its falsifiable test and rollback conditions |
| Evaluation | One dataset window × test type × candidate | Preserve in-sample, OOS, walk-forward, regression and shadow results |
| Rule version | One immutable configuration/rule payload | Content hash, parent, diff and rationale; status is derived from governance events |
| Governance event | One approval/rejection/defer/activation/rollback decision | Auditable human authority, reason, evidence and tested artifact references |

The SQL proposal is in **db/proposals/market_learning_loop_v1.sql**; the machine-readable run contract is **schemas/market-run-envelope-v1.schema.json**.

## 6. Forecast and outcome contract

### Horizon registry

Keep these as different horizon units:

- **Intraday monitor:** source observation interval, such as a 15-minute poll; used for alert/state-transition diagnostics, not mislabeled as a daily forecast.
- **Trading-session evaluation:** initial default candidates are 1, 5, 20, 60, 120 and 252 trading sessions. These can support price/market-regime and entry-timing studies.
- **Calendar-day stress evaluation:** 1, 7, 30, 90 and 365 calendar days for stress-event timing/cost-of-delay analysis.
- **Custom horizon:** permitted only when horizon_value, horizon_unit, start convention, end convention, and settlement logic are recorded.

Do not merge a five-trading-session outcome with a five-calendar-day outcome. The horizon registry must be versioned and each forecast must pin the chosen definition.

### Minimum outcome fields

For each matured forecast, capture:
- Reference price/index and timestamp, realized endpoint price/index, and adjustment/return methodology.
- Realized return and benchmark excess return, where applicable.
- Maximum adverse excursion (MAE) and maximum favorable excursion (MFE) during the evaluation window.
- Hit/miss or event classification, measurement window, data-quality state, source evidence IDs, and calculation version.
- **COMPLETE**, **INSUFFICIENT_DATA**, or **INVALIDATED** status. Unavailable outcome data stay unresolved; they are not counted as zero returns or forecast misses.

Outcome calculations must be deterministic and independently testable. LLM-generated text is explanatory metadata, never the numerical source of truth.

## 7. Scorecard: measure more than direction accuracy

Measure by forecast type, horizon, asset class, regime, and rule version; always show sample size and data coverage beside metrics.

- **Forecast quality:** directional accuracy, precision/recall, confusion matrix, calibration, Brier score or log loss where probabilities exist.
- **Event detection:** false-positive rate, missed-event rate, lead time, warning duration and repeat-alert frequency.
- **Investment utility:** realized/benchmark-excess return, MAE/MFE, downside quantiles, maximum drawdown and transaction-cost sensitivity where relevant.
- **Operational integrity:** freshness, PIT violations, missing-required-series rate, duplicate rate, schema rejection rate, job failure/retry rate, unresolved outcome rate and time-to-settlement.
- **Robustness:** walk-forward/OOS degradation, parameter sensitivity, regime-stratified behavior and performance after costs.

An overall accuracy number must never conceal a high-cost miss in a severe-stress regime. Weighted/risk-sensitive metrics must be reported next to unweighted metrics, not instead of them.

## 8. Root-cause taxonomy

Every diagnosis selects one primary cause and may attach secondary contributors:

- **DATA_MISSING_OR_STALE:** required input absent, stale, failed or misclassified.
- **PIT_OR_REVISION_LEAKAGE:** data availability/revision timing is inconsistent with the decision clock.
- **SOURCE_OR_ADJUSTMENT_ERROR:** provider semantics, currency, unit, split/dividend adjustment or benchmark mapping is wrong.
- **FEATURE_OR_NORMALIZATION:** calculation, scaling, percentile window, correlation handling or sign convention is wrong.
- **THRESHOLD_OR_STATE_TRANSITION:** cutoffs, persistence rule or stress override produce false or delayed transitions.
- **REGIME_OR_CROSS_ASSET:** regime/sector/asset interaction or causal linkage was missed.
- **HORIZON_OR_SETTLEMENT:** label window, endpoint or outcome calculation is misdefined.
- **MODEL_OR_CALIBRATION:** forecasting method is biased, overconfident or unstable OOS.
- **EXECUTION_OR_COST:** timing, slippage, liquidity or cost assumptions explain a result gap.
- **CONFLICT_OR_REASONING:** conflicting evidence, unsupported inference or explanation drift.
- **PROCESS_OR_HUMAN_OVERRIDE:** a manual override or operational process changed the decision path.
- **UNKNOWN_OR_INTERACTION:** current evidence cannot isolate one cause.

A post-hoc correlation is not proof of causality. Record counterfactuals and competing hypotheses. Use controlled ablation, matched episodes, walk-forward experiments or other explicit tests before calling a proposed mechanism confirmed.

## 9. Countermeasure validation and release policy

A countermeasure must contain:
1. Diagnosis IDs and the precise evidence/forecast/outcome records it addresses.
2. A falsifiable hypothesis stating what behavior should change and why.
3. Baseline metric, target metric, minimum sample/coverage, and maximum tolerated degradation on risk guardrails.
4. A time-based or episode-based OOS/walk-forward test plan, sensitivity analysis and competing-baseline comparison.
5. Shadow-mode monitoring and a rollback condition.
6. An immutable diff/hash, owner, expiry/review date and human decision.

Lifecycle is event-derived: **PROPOSED → OFFLINE_TEST → SHADOW → HUMAN_APPROVED → ACTIVE**, or **REJECTED / DEFERRED / ROLLED_BACK**. These labels describe governance state; they must not be inferred from generated text.

Promotion gate:
- PIT/Data Integrity passes.
- The same forecast and outcome definitions are used for baseline and candidate.
- Tests include OOS/walk-forward and relevant stress episodes.
- Risk guardrails, false-negative analysis and operational checks pass.
- No unresolved high-severity evidence conflict exists.
- A human explicitly authorizes activation.
- The previous version and tested artifact are pinned, and rollback can restore that exact version.

In V1, default **BUY_ALLOWED=false** and **EXECUTION_ALLOWED=false**. Research evidence cannot grant execution authority. Any later change to that invariant is a separate, explicitly reviewed governance decision, not an ordinary learned threshold update.

## 10. Token and compute efficiency

- Persist structured numeric facts once; use stable IDs and hashes to reference evidence rather than repeating full source text in every agent prompt.
- Use **delta-first** processing: evaluate only changed dimensions, newly matured outcomes, breached guards, and unresolved cases. Run periodic complete reconciliation to detect missed events.
- Separate deterministic computation from LLM explanation. Use code/SQL for normalization, labels, return/MAE/MFE, metrics, integrity and gate results.
- Pass each agent a scoped work packet: question, relevant IDs, required evidence, permitted outputs, constraints and maximum output size.
- Use bounded JSON output contracts and stable taxonomy codes; keep prose conclusions short and evidence-linked.
- Cache by content hash and version. If inputs/code/config/model/prompt have not changed, do not recompute expensive narrative analysis unnecessarily.
- Start with one root-cause analysis per material error cluster, not one agent call for every polling tick. Deduplicate incidents by episode and evidence fingerprint.
- Summarize old periods into versioned aggregates, but retain canonical raw evidence/artifact references for audit and re-analysis.
- Measure cost per completed evaluation and per accepted improvement alongside model-token usage.

## 11. Reliability, monitoring and recovery

- **Idempotent writes:** unique idempotency/input keys; **INSERT ... ON CONFLICT DO NOTHING** for immutable records. Never use an upsert that silently overwrites an earlier decision.
- **Explicit state machine:** **DATA_NOT_READY**, **BLOCKED**, **RESEARCH_ONLY**, **SHADOW**, and governance-approved states are distinct. Missing data cannot be represented as **GREEN**.
- **Temporal QA:** all values used for a run are checked against the run's decision timestamp, not the current wall clock.
- **Lineage:** every forecast links to one run, versioned rule set, calculation version, and input digest; every outcome links to its forecast and evidence.
- **Replay:** retain input manifests and calculation versions so a historical run can be reproduced without replacing the original.
- **Failure handling:** bounded retries for transient collection failures; no retry loops for schema/invariant failures; dead-letter/quarantine records include error code and input hash.
- **Drift checks:** alert on missingness/freshness drift, calibration deterioration, regime-specific miss clusters, source schema changes, and silent changes in output distributions.
- **Backup and retention:** database snapshots plus periodic content-addressed exports; periodically prove restore and replay. Retention applies to large raw payloads only under an explicit policy; decision/evaluation/audit records are retained.
- **Security:** dedicated investment database/schema. No service-role/secret key in browser or logs. No public Data API grants. RLS enabled on all tables as defense in depth; ingestion uses a restricted server-side identity with insert/select only.

## 12. Initial acceptance criteria

The V1 contract and store are not considered production-ready until tests show that:

- Replaying one envelope does not create duplicate logical runs.
- A metric with **available_at > analysis_asof** is rejected.
- Missing/stale required evidence never becomes zero or GREEN.
- A forecast cannot have live buy/execution flags set in V1.
- Outcomes cannot be settled before the defined horizon and cannot mix horizon units.
- Recalculation creates a new calculation-version record without altering the prior result.
- A candidate that passes in-sample but fails OOS/walk-forward remains ineligible.
- A rule cannot become active without an explicit human release event.
- Every active version has a tested prior version and a working rollback path.
- Failure paths and migrations have automated tests, not just happy-path tests.

## 13. Delivery plan

- **P0 — Contract and governance:** run-envelope schema, validators, DB proposal, taxonomy, hard gates. No live behavior change.
- **P1 — Storage integration:** connect the fixed market monitor to the existing Historical DB v1 / append-only run ledger; persist one pre-open baseline plus material state/quality transitions with idempotency, then import any existing runtime snapshot with **LEGACY_SNAPSHOT** provenance. Establish a single-writer and branch-retention policy before enabling scheduled writes.
- **P2 — Forecast ledger:** freeze daily/EOD and entry-timing forecasts with the existing D/W/M checks, timestamps, rules and permissions.
- **P3 — Outcome settlement:** schedule trading-session/calendar-day labels, MAE/MFE and data sufficiency checks.
- **P4 — Evaluation and diagnostics:** scorecard, error clustering, root-cause evidence bundles and countermeasure experiments.
- **P5 — HOTL control:** review screen, immutable decisions, shadow mode, promotion/rollback and audit reports.
- **P6 — Expansion:** sector/stock/ETF/crypto/FX/gold adapters via the same contracts, with independent horizon registries and risk guards.

## 14. Current deployment boundary

The existing Historical DB v1 implementation is currently append-only CSV on a local filesystem. It is not yet a demonstrated durable market-monitor history service: the current scheduled monitor does not ingest into it, and no tracked `data/history` series was found on the main branch. The planned durable bootstrap therefore needs an explicit history branch or another persistent target, single-writer control, replay/idempotency tests and documented backup/retention. Do not claim daily accumulation until the scheduled write path has run successfully and a record can be read back.

The SQL file is a proposal only; it has not been applied. The connected Supabase projects are already associated with other systems, so do not apply this schema to them. A dedicated investment relational database remains a later migration decision; confirm organization/cost, test in an isolated development environment, run security/performance advisors and validate permissions before applying it.

The current DecisionGate and upstream M0/M1/M2 controls remain authoritative. This learning loop supplies evidence for improvement; it does not bypass them.


## 15. First incident seed: monitor return-horizon and freshness failure

Seed the learning loop with the open P1 incident documented in [investment Issue #27](https://github.com/chayobi03-cyber/investment/issues/27). On the 2026-10-13 07:28 KST monitor snapshot, KOSPI was reported at -0.377% while the reported 2026-10-12 regular-session close was -3.65%. KOSDAQ was reported at -0.435% versus -4.83%; Samsung Electronics at -0.299% versus -4.39%; SK hynix at -0.496% versus -4.52%. The snapshot nevertheless carried DATA_QUALITY=GREEN and RISK=GREEN.

Initial diagnosis from the incident:
- fetch_chart() divided the last two 5-minute closes and exposed that result as generic change_pct; this did not represent either a validated 15-minute move or a daily close-to-close return.
- The configured threshold was described as a 15-minute threshold but consumed the generic last-bar return.
- Global freshness was calculated using the newest timestamp among all symbols. A fresh USD/JPY observation therefore masked materially older KOSPI/KOSDAQ/leader observations.
- The bad upstream semantics propagated to market state/alerting and could suppress risk warnings.

Required countermeasure and regression evidence:
1. Make every return field explicit (5m, validated 15m, current-session versus prior regular-session close-to-close) and pin the calculation/horizon version.
2. Calculate each measure only from timestamp-compatible bars and preserve the observation/reference timestamps.
3. Evaluate freshness per series and required group using session-aware rules; a fresh unrelated series must never clear a stale critical series.
4. Reproduce both the close-to-close divergence and the fresh-USD/JPY/stale-Korea scenario in deterministic tests.
5. Confirm that required input gaps produce DATA_NOT_READY or BLOCKED and never produce an authorized buy or execution signal.

The incident must remain linked to its original run, evidence, diagnosis, countermeasure, evaluation and governance events. Do not mark the root cause as remediated merely because a patch was committed: require test results and a subsequent verified shadow/production observation. Until that remedy has independently passed, the affected monitor fields remain non-authoritative for buy timing, matching the current incident's stated safety posture.
