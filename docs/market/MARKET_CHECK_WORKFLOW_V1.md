# Market Check Workflow V1 — Deterministic Execution Contract

- **Status:** ACTIVE AS A RESEARCH WORKFLOW; executable orchestration/automatic persistence are not yet verified end-to-end
- **Version:** `market-check-workflow-v1.0`
- **Timezone:** `Asia/Seoul` (KST)
- **Decision posture:** capital preservation; research-only; fail-closed
- **Related incident:** [Issue #27 — invalid return horizon and cross-instrument freshness](https://github.com/chayobi03-cyber/investment/issues/27)

## 1. Purpose and invocation

This file is the canonical contract for every user request equivalent to:

- “오늘 시장”, “오늘 시장 확인/분석”
- “현재 시장 점검”, “아침 시장 점검”, “장중 시장 확인”, “장 마감 분석”
- “시장 상황 확인”, “시장 분석해보자”

These requests all invoke **the same workflow and same required fields**. The words “아침/장중/마감” select the session phase, not a different analytical standard. “간단히” may shorten presentation only; it must not skip validation, source timestamps, or safety gates.

Run a fresh observation for the current KST time. Never reuse a prior run as if it were current. If live values cannot be verified, return the available verified evidence and explicitly mark the run `DATA_NOT_READY` or `RESEARCH_ONLY`; do not ask the user to supply market data merely because a browser/source failed.

## 2. Non-negotiable decision controls

Every run must report these fields explicitly:

- `BUY_ALLOWED=false`
- `EXECUTION_ALLOWED=false`
- `PROMOTION=DISABLED`
- `DECISION_MODE=RESEARCH_ONLY` unless the required data itself is unavailable, in which case `DATA_NOT_READY`
- `REGIME_ENGINE=UNCONFIRMED` unless the calibrated, validated R1–R6 engine has actually run and its evidence is available

The market review is not trade execution authority. A lower price, one green candle, a positive headline, or one source's “risk-on” label is never sufficient to enable a buy. Stock-level entry consideration always requires separate Daily/Weekly/Monthly (`D/W/M`) checks for trend, support/resistance, position versus recent highs, momentum, and relative strength. Preserve any previously recorded account or asset restrictions; do not infer that a holding can be sold or averaged down.

## 3. Deterministic run sequence

Execute in this order. Do not omit a step because one source is unavailable.

### Step 0 — Freeze the run identity

Capture once at the start:

- `run_asof_kst`: current timestamp with timezone
- `session_phase`: `PREOPEN`, `INTRADAY`, `POSTCLOSE`, or `NON_TRADING_DAY`
- `market_date`: the relevant Korean exchange session date, not simply the calendar date
- `workflow_version`, `source_policy_version`, and available data/config versions
- `run_id`: stable unique identifier for the observation

Use the same `run_asof_kst` for all freshness checks and derived calculations in the run. Record retrieval time separately from the source's observation/publication time.

### Step 1 — Retrieve evidence in fixed order

1. **Korean index and session reference:** KOSPI, KOSDAQ, KOSPI 200 where available; latest price, prior regular-session close, open/high/low, session timestamp.
2. **Breadth:** advancing/declining issues, unchanged count, and index constituents/sector breadth when a trustworthy source provides them. Never substitute watchlist breadth for exchange-wide breadth without labeling it as a proxy.
3. **Investor flows:** foreign and institutional net cash flows; derivatives/futures only when the source exposes the instrument, direction, unit, and timestamp. Distinguish provisional intraday flows from finalized close data.
4. **Domestic leadership:** Samsung Electronics, SK hynix, plus configured watchlist names; compare each with KOSPI over the same return horizon. Do not compare a daily return with a five-minute return.
5. **Cross-asset context:** USD/KRW, US 2Y/10Y rates/yields (latest valid timestamp), Brent and WTI, gold, USD/JPY, US equity/semiconductor indices, and futures where a current valid quote exists.
6. **Catalysts:** latest relevant official releases and credible reporting on central banks, inflation, credit, geopolitics, energy, earnings, and policy. Separate confirmed events from interpretation.
7. **Technical context:** index D/W/M structure and provisional reference levels, only from verified OHLC/close history.

Use this source precedence: official exchange/issuer/government or central-bank publication for finalized facts; a timestamped market-data source for current quotes; independent corroboration for decision-critical price changes; news sources for context/catalysts. A search snippet or undated cached page is not proof of a live quote. When sources conflict, retain both observations, identify the conflict, and downgrade the affected field; never silently choose the value that makes the narrative smoother.

### Step 2 — Preserve raw observations before interpreting

For every observation retain, when available:

`field`, `instrument`, `value`, `unit`, `currency`, `source_name`, `source_url`, `source_observed_at`, `source_published_at`, `retrieved_at`, `market_date`, `session`, `return_horizon`, `quality_status`, `notes`.

Never silently replace nulls with zero, carry forward values as current, mix local and UTC timestamps, or mix adjusted and unadjusted prices. Keep observed facts separate from derived values and analyst interpretation.

### Step 3 — Calculate each return only against the matching baseline

- **Session / daily move:** current price or latest session close versus the verified prior regular-session close.
- **5-minute move:** latest valid observation versus the observation nearest to, but not later than, the target time five minutes earlier.
- **15-minute move:** same method using a 15-minute target horizon.
- **D/W/M returns:** session close versus the prior relevant daily/weekly/monthly close, using exchange sessions rather than calendar-day offsets.
- **Relative strength:** security return minus the index return over the exact same start/end timestamps and horizon.

For intraday horizons, retain both endpoint timestamps and endpoint ages. If an endpoint is missing, too old, outside the source's permitted tolerance, or from a different session, mark that horizon unavailable; do not substitute the previous bar and relabel it 5m/15m/daily. No price interpolation or cross-session comparison unless explicitly specified by a tested calculation contract.

### Step 4 — Validate data quality per instrument and field

Assign a status to each field, then compute group status. Do not compute overall status from a single global “newest timestamp”.

- `GREEN`: source, units, baseline, observation timestamps, and requested horizon are all verified and within the field/session-specific freshness policy.
- `AMBER`: usable with a disclosed caveat (for example, delayed/provisional data, only one source, or a non-critical required dimension missing).
- `RED`: contradictory or invalid baseline, wrong/mislabeled return horizon, material timestamp/session mismatch, or unusable critical input.
- `DATA_NOT_READY`: required evidence is missing or fails validation such that today's market state cannot be responsibly established.

Freshness is evaluated independently for each symbol/field and required group. During the Korean session, do not let a fresh FX observation conceal stale KOSPI/KOSDAQ/leader quotes. Before/after a market session, a verified last regular-session close remains a valid *last close*, but must not be described as a live quote. Every field must be labeled with whether it represents live, delayed, finalized, provisional, or last-session data.

**Fail-closed gate:** critical index returns or timestamps invalid → no claim of a validated intraday direction; investor-flow data unavailable → flow direction is “unconfirmed”; exchange-wide breadth unavailable → breadth is “unconfirmed”; conflicting critical sources → disclose conflict and block any stronger inference. An aggregate `GREEN` is prohibited while any critical group is `RED` or `DATA_NOT_READY`.

### Step 5 — Produce a fixed market-state vector

Always report these dimensions in this order, using `POSITIVE`, `NEGATIVE`, `MIXED`, or `UNCONFIRMED` plus the measured evidence:

1. Korean index structure (KOSPI/KOSDAQ/KOSPI 200)
2. Market breadth
3. Foreign/institutional flows
4. Domestic leaders and relative strength
5. Rates/liquidity
6. FX
7. Energy/commodities
8. Overseas equity/semiconductor context
9. Confirmed macro/geopolitical/earnings catalysts
10. D/W/M structure and relevant price references

Do not invent a numerical Market Score or claim a calibrated R1–R6 state if the validated engine has not run. If the evidence points in different directions, the aggregate must be `MIXED/UNCONFIRMED`, not forced into a clean bullish/bearish label. Distinguish an observed correlation from a proven cause.

### Step 6 — Apply the same scenario and action gates

Output the following cases when data supports them:

- **Continuation/downside:** verified index deterioration with corroborating breadth, flow, leadership, or cross-asset evidence. State which conditions would invalidate this scenario.
- **Stabilization attempt:** deterioration slows or a prior reference is reclaimed, but breadth/flows or D/W/M confirmation is incomplete. Label as watch-only, not a buy signal.
- **Recovery confirmation:** improvement persists across the index, breadth, leadership and relevant risk context, and the evidence survives the required observation window. Re-evaluate candidates only; no automatic BUY.

Support/resistance from a single session's low/high is a *reference*, not automatically a durable level. Every scenario must contain observed evidence, what would confirm it, what would invalidate it, and what evidence is missing.

### Step 7 — Evaluate candidates only after the market review

Do not automatically turn a market check into an order or a stock-level buy call. When a specific candidate is requested, run the separate `D/W/M` checklist and risk/permission checks. Until PIT, source provenance, and required data-quality gates pass, the candidate remains `DATA_NOT_READY`, `BLOCKED`, or `RESEARCH_ONLY`. Maintain `BUY_ALLOWED=false` and `EXECUTION_ALLOWED=false`.

### Step 8 — Persist and create the HOTL evaluation record

Build a structured record containing:

- run identity and workflow/config versions
- raw observation references and source URLs
- derived metrics with formula, baseline, and endpoint timestamps
- field/group quality outcomes and missing-data reasons
- market-state vector and scenario gates
- prediction/hypothesis made at this timestamp
- next evaluation checkpoints and the observed outcomes
- conclusion: `HIT`, `PARTIAL`, `MISS`, or `NOT_EVALUABLE`
- root cause and corrective action, if a miss or data defect occurred

Use the repository's `scripts/record_live_market_review.py` only with the structured JSON format accepted by the current Historical DB adapter, and inspect its returned manifest/receipt. A Markdown report alone does **not** prove database persistence. If the recorder, required schema, database, or runtime is unavailable, state `PERSISTENCE=NOT_RUN` and keep the report as research-only; do not claim a completed DB transaction. Do not update historical observations in place to make an earlier prediction look correct.

## 4. Required response format

Every market-check response uses these headings in order:

1. **Run status** — KST as-of, session phase, `DATA_QUALITY`, `DECISION_MODE`, persistence status.
2. **One-line conclusion** — evidence-backed; explicitly qualitative if the calibrated regime engine was not run.
3. **Market-state table** — the 10 dimensions from Step 5, current values/moves, source timestamps, quality and citation/source link.
4. **What is driving the move** — observed evidence, plausible mechanism, confidence and alternative explanations.
5. **Key levels and D/W/M context** — mark provisional levels as provisional.
6. **Scenario gates** — downside, stabilization, recovery; confirmation and invalidation conditions.
7. **Action / permissions** — watch, wait, or reassess; never infer authority to trade.
8. **Missing data and caveats** — explicit, not buried.
9. **HOTL checkpoint** — what to compare on the next run and what prior hypothesis will be scored.
10. **Record receipt** — database/artifact link and run ID only if actually persisted.

Cite external factual claims close to the claim. Prefer source links with explicit timestamps. Do not fill the report with long generic explanations when actual values are available.

## 5. Determinism and reproducibility contract

- Identical raw input snapshots + identical workflow/config versions must yield identical formulas, quality states, market-state vector and persisted record keys.
- Live runs can differ only when inputs, relevant as-of time, source publication, or version change; record which one changed.
- Missing data has an explicit null/status and reason. No zero-fill, silent fallback, or analyst-edited override.
- Keep the pre-session hypothesis immutable; outcomes and lessons append as separate records.
- Thresholds are not tuned during the daily run. Any threshold change requires a separately versioned proposal, backtest/falsification and approval.
- Narrative judgement can summarize evidence, but must not override the quality gate or decision permissions.
- Keep raw observations, derived measures, assessment, and user-facing narrative as separate layers.

## 6. Known implementation blocker

The current `scripts/market_monitor/poll.py` has a confirmed integrity defect documented in [Issue #27](https://github.com/chayobi03-cyber/investment/issues/27): `change_pct` uses adjacent 5-minute bars, although the output/config refers to a 15-minute threshold; data freshness is based on the newest timestamp across all instruments, allowing a fresh unrelated symbol to hide stale critical Korean-market observations. Until the remediation and regression tests pass, the compact monitor's `RISK`, `TREND`, `DATA_QUALITY`, and return fields are **not authoritative for an entry decision**.

## 7. Acceptance criteria for executable automation

The workflow is not considered fully automated merely because this document exists. Mark the executable workflow complete only after:

1. A single entry point resolves KST as-of/session phase and calls the same ordered data collection.
2. Return calculations use correct, explicit horizons and verified baselines.
3. Per-instrument/per-field/session freshness and group aggregation are covered by tests.
4. Regression tests cover the 2026-10-12 selloff discrepancy and the “fresh USD/JPY hides stale Korean quotes” case.
5. Missing/conflicting inputs force the defined fail-closed statuses.
6. Structured output validates against a versioned schema and can be persisted through Historical DB with a verifiable receipt.
7. Re-running against a frozen fixture produces byte-stable or canonical-JSON-equivalent derived results and record keys.
8. The run preserves `BUY_ALLOWED=false` and `EXECUTION_ALLOWED=false`.
9. End-to-end tests and CI are green before the monitor issue is closed or the market engine is promoted.

## 8. Lesson learned

A market conclusion is only as reliable as its data horizon, baseline and timestamp. A fresh timestamp from an unrelated instrument cannot certify stale market data, and a last-bar move cannot stand in for a daily or 15-minute return. The workflow therefore validates provenance and matching horizons before interpretation, and never lets a data-quality defect increase permission to act.
