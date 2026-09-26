# Crypto Threshold Validation Gate V0.2

Date: 2026-09-26
Status: PREREGISTERED EVALUATION CONTRACT

## Purpose

Separate evidence that the frozen BTC entry thresholds have predictive value from the stronger requirement to promote the complete BUY permission layer.

Thresholds are not changed during this evaluation.

## OOS Evidence Gate

The last 20% of chronological history is the fixed OOS set.

The frozen threshold evidence gate requires:

1. OOS primary events >= 20.
2. OOS median 20D forward return > 0.
3. OOS median 60D forward return > 0.
4. OOS positive-return rate >= 50% at 20D.
5. OOS positive-return rate >= 50% at 60D.
6. OOS median 20D MAE > -15%.
7. OOS median 20D return is not more than 3 percentage points below the simple >=5% pullback baseline.

All seven conditions must pass for threshold_validation.status = PASS.

## Walk-forward Evidence

Use expanding chronological folds.

- Thresholds are frozen.
- threshold_retuned must remain false.
- Every non-empty test fold must have measurable primary events.
- Fold-level outcomes are reported individually; no averaging may hide a failed fold.

A walk-forward PASS is evidence of stability, not proof of future performance.

## Full BUY Promotion Gate

Even when the OOS threshold evidence gate passes, the full BUY permission layer remains blocked until the following PIT datasets are complete and validated:

- institutional / ETF flow;
- macro rates / FX;
- derivatives history;
- liquidity / risk proxies;
- regulation / market-structure evidence;
- geopolitical transmission evidence;
- provenance and availability timestamps for every input.

Therefore: threshold_validation PASS does not imply P6 PROMOTE.

## Capital Preservation Rule

A threshold cannot be promoted because of CAGR alone.

The following remain primary risk checks:

- maximum drawdown;
- worst forward loss;
- downside-tail loss;
- survival constraint violations;
- recovery time;
- stress-event behavior.
