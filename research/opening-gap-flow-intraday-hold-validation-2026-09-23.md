# Opening Gap → Foreign Flow → Intraday Hold Validation — 2026-09-23

## Status

**RESEARCH / FULL RULE VALIDATION = DATA_NOT_READY**

The proposed three-part entry rule is:

`Opening Gap → Foreign Net Flow Confirmation → Intraday Hold Confirmation`

The available historical P0~P6 artifact can only partially test the first component and a coarse daily close-vs-open proxy. It contains **no foreign-flow history and no intraday bars**, so the full rule must remain unvalidated and must not be promoted to P0~P6 operational logic.

## 1. Evidence used

- Historical artifact: GitHub Actions run `35664235537`
- Artifact: `historical-pit-p0-p6-35664235537`
- Artifact SHA-256: `4c8766921174f73839a04acd3eb0749d7dfaa7948f765365db23c3747d48b5dc`
- Episodes: 1,216
- Development / validation / OOS: 796 / 120 / 300
- Historical source state: `VENDOR_HISTORY_PROXY`
- Strict archival PIT: false
- P6 fundamentals: `DATA_NOT_READY`

## 2. What can be tested now

### Opening gap

For each episode with a next-session entry open:

`gap_pct = (entry_open / trigger_close - 1) × 100`

The dataset contains `entry_open` for the 1,216 event rows. Forward-return evaluation is limited by horizon availability.

### Daily hold proxy

The first `asset_rows` record contains daily OHLC only. Therefore the only available hold proxy is:

`daily_close_hold = entry_day_close >= entry_day_open`

This is **not** equivalent to intraday hold because the path between the open and close is unobserved.

## 3. Partial diagnostic

The following is a descriptive stratification only. The gap cutoffs are **not preregistered thresholds** and are not eligible for rule promotion.

| Gap screen | Split | 20D evaluable | Mean 20D | Positive rate | Daily-close-hold |
|---|---|---:|---:|---:|---:|
| gap >= 1% | Development | 177 | +0.94% | 50.3% | 50.8% |
| gap >= 1% | Validation | 28 | +1.29% | 60.7% | 50.0% |
| gap >= 1% | OOS | 89 | +3.65% | 58.4% | 43.8% |
| gap >= 2% | Development | 77 | +2.17% | 57.1% | 59.7% |
| gap >= 2% | Validation | 13 | +4.65% | 76.9% | 69.2% |
| gap >= 2% | OOS | 39 | +3.69% | 53.8% | 35.9% |
| gap >= 3% | Development | 29 | -1.05% | 48.3% | 48.3% |
| gap >= 3% | Validation | 7 | +8.33% | 85.7% | 71.4% |
| gap >= 3% | OOS | 18 | +6.13% | 61.1% | 44.4% |
| gap >= 5% | Development | 6 | -3.62% | 50.0% | 33.3% |
| gap >= 5% | Validation | 1 | +7.36% | 100.0% | 100.0% |
| gap >= 5% | OOS | 7 | -2.05% | 42.9% | 42.9% |

### Gap + daily-close-hold proxy

Using an illustrative `gap >= 1%` plus positive entry-day close-vs-open proxy:

| Split | 20D evaluable | Mean 20D | Positive rate |
|---|---:|---:|---:|
| Development | 90 | +2.87% | 58.9% |
| Validation | 14 | +2.60% | 71.4% |
| OOS | 39 | +6.06% | 64.1% |

## 4. Interpretation

1. The evidence does **not** justify selecting a gap threshold. Results are unstable as the gap cutoff increases and validation/OOS samples become very small.
2. The daily close-vs-open proxy is insufficient to establish an intraday hold effect. It contains no path information and can miss early rejection/recovery patterns.
3. There is zero historical `foreign_flow`, `foreign_net_flow`, or equivalent PIT flow field in the current artifact.
4. There are zero intraday bar fields; `asset_rows` contains only `date/open/high/low/close`.
5. Therefore the proposed three-part rule cannot yet be tested as a causal entry filter. Any apparent positive result from the current dataset would be a test of a **different, reduced rule**.

## 5. Lesson learned

### New rule for research governance

**Do not promote an entry rule when one of its defining components is absent from the historical evidence layer.**

For the proposed rule, the minimum PIT evidence contract is:

- `previous_close`
- `session_open`
- `gap_pct`
- foreign net flow with source, unit, timestamp, and PIT availability
- intraday bars at a fixed frequency
- explicit intraday-hold definition and timestamp window
- forward 5D / 20D / 60D outcomes
- MAE / post-entry drawdown
- explicit prediction and realized labels for FP/FN metrics
- development / validation / OOS + walk-forward evaluation
- thresholds frozen before the final rerun

### Required comparison

The full validation should compare, using the same universe and outcome definition:

1. price-only baseline
2. price + opening gap
3. price + opening gap + foreign flow
4. price + opening gap + foreign flow + intraday hold

A component earns promotion only if its incremental contribution survives OOS and walk-forward checks without relying on post-hoc threshold selection.

## 6. Governance decision

**Current status:**

`RESEARCH → DATA_NOT_READY → no rule promotion`

No live MarketScore / BuyStrength change follows from this study.

## 7. Next acquisition target

Extend the historical observation layer with:

`OHLCV + foreign_flow + intraday_1m_or_5m + PIT availability/provenance`

Then preregister the gap, flow, and hold definitions and rerun the full P0~P6 evaluation.
