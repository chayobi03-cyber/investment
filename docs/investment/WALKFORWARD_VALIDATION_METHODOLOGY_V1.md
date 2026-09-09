# Walk-Forward / Point-in-Time Validation Methodology V1

Date: 2026-09-08
Status: RESEARCH TOOLING BASELINE — implements existing validation protocol, does not itself authorize live use of any score.

## 1. Objective

Operationalize the validation gate that `docs/research/MARKET_DECISION_FRAMEWORK_RESEARCH_2026-09-08.md` (§10-11) and `docs/investment/MARKET_REGIME_ENGINE_V1.md` (§8) already require but had not implemented in code:

`Level 3 (historical simulation) → Level 4 (out-of-sample) → Level 5 (walk-forward) → Experiment A (score monotonicity)`

No Market Score, Stock Score, or FX/JPY trigger may be connected to BuyStrength/Action before it passes this gate (see handover §13 "Immediate Open Work"). This module is the reusable engine that gate runs on.

## 2. Core principle — "predict the past from more of the past"

A rule is only informative if it would have worked without seeing the future. Concretely, for every historical anchor date `t`:

1. **State layer** — the score at `t` may use only observations with `available_at <= t` (already enforced upstream by `investment_pipeline.factors.normalize_point_in_time`).
2. **Outcome layer** — the thing being predicted is the *already-realized* return/drawdown over `(t, t+h]`, computed only for evaluation, never fed back into the score (`attach_forward_outcomes`).
3. **Bucket edges must also be point-in-time.** Bucketing a point-in-time score using full-sample quantile edges is a subtler leak: the *boundary* would still depend on post-`t` data even though the score itself doesn't. `expanding_quantile_bucket` recomputes quantile edges from an expanding window ending at `t`.
4. **Consistency, not a single number.** A relationship that only shows up once, pooled across all history, is not distinguishable from noise or from a single dominant episode (Market Decision Framework §12, falsification rule #7: "performance depends on one narrow historical episode"). `walk_forward_stability` re-estimates the score→outcome relationship inside several expanding-window out-of-sample folds and reports whether folds *agree with each other* (`fold_sign_agreement`, `monotonic_fold_fraction`), not just whether each fold happens to agree with the full-sample average.

This is implemented in `src/investment_pipeline/walkforward.py`:

```text
attach_forward_outcomes      -> Outcome layer (fwd_return_Nd, fwd_max_drawdown_Nd)
expanding_quantile_bucket    -> point-in-time bucket edges (no look-ahead in bucketing)
rank_information_coefficient -> Spearman rank IC, score vs. outcome
monotonicity_report          -> per-bucket mean/median/hit-rate/std
walk_forward_folds           -> expanding-window fold boundaries
walk_forward_stability       -> per-fold IC + monotonicity + fold-to-fold agreement
run_experiment_a             -> orchestrates all of the above per horizon, with falsification_status
```

## 3. What `run_experiment_a` reports, per horizon (5d/20d/60d/120d by default)

- `bucket_stats` — mean/median/hit-rate/std of forward return per point-in-time quantile bucket.
- `monotonic_full_sample` — whether bucket means are monotonic across the full sample (Experiment A's original test).
- `full_sample_rank_ic` — Spearman rank IC, score vs. forward outcome, pooled.
- `walk_forward` — per-fold IC/monotonicity plus:
  - `fold_same_sign_as_full_sample` — fraction of folds whose IC sign matches the pooled full-sample IC sign.
  - `fold_sign_agreement` — fraction of folds agreeing with the *majority sign among folds themselves*. This catches regime flips that a pooled full-sample IC can average away (e.g. a relationship that is strongly positive in the first half of history and strongly negative in the second half can produce a near-zero, sign-ambiguous full-sample IC while still being unstable fold-to-fold).
  - `monotonic_fold_fraction` — fraction of folds where the bucket ordering itself stayed monotonic.
- `falsification_status` — one of:
  - `INSUFFICIENT_DATA` — not enough point-in-time history to bucket reliably.
  - `FALSIFIED_NO_STABLE_SEPARATION` — full-sample bucket means are not monotonic (Market Decision Framework §12 rule #1).
  - `FALSIFIED_UNSTABLE_ACROSS_FOLDS` — full-sample result does not survive walk-forward re-estimation (§12 rule #3), including the fold-to-fold sign-agreement check above.
  - `NOT_FALSIFIED_CANDIDATE` — survived this gate. This is a necessary, not sufficient, condition for promotion; Levels 6-10 (parameter sensitivity, transaction costs, cross-market validation, multiple-testing correction, shadow operation) still apply before any live use.

## 4. How to run it

Prerequisite: the KRX/OpenDART data pipeline (`README_DATA_PIPELINE_V1.md`) must have produced `data/processed/normalized_factors.csv` with a GREEN completeness gate. This harness must never run against hand-entered or fabricated numbers — that would defeat its purpose.

```bash
PYTHONPATH=src python scripts/run_walkforward_validation.py \
    --processed-dir data/processed \
    --score-col return_20d_score \
    --price-col close \
    --out data/processed/walkforward_report.json
```

Any `_score` column produced by `normalize_point_in_time` (Trend/Momentum, Valuation, etc.) can be validated this way once real data is connected. For the Market Score/Regime engine (`MARKET_REGIME_ENGINE_V1.md`), the same harness applies once the market-level state vector (Trend/Breadth/Risk/Macro/Cross-Asset) has its own point-in-time panel — that data connection is separate, currently pending (handover §13 P2).

## 5. What this does NOT do

- It does not fetch or fabricate market data. It only validates a score that already exists in a point-in-time panel.
- It does not decide today's action. Passing this gate answers "would this score have been informative historically," not "what should I do right now." Today's action still requires: current data pull → current score → current regime → BuyStrength → risk constraint, per the existing decision chain in `MARKET_REGIME_ENGINE_V1.md` §1 and the handover's standard session checklist (§15).
- It does not replace Levels 6-10 of the validation protocol (parameter sensitivity, transaction costs, cross-market validation, multiple-testing/data-snooping correction, shadow operation). A `NOT_FALSIFIED_CANDIDATE` result is evidence, not a promotion.
- It does not optimize thresholds against the data it is validating. `n_buckets`, `n_folds`, `min_train_periods`, and the horizon list are specified by the caller ex ante; changing them after seeing results and re-reporting only the favorable run is exactly the data-snooping failure mode the framework's Level 9 exists to catch. Record every specification tried (Market Decision Framework §12 rule #8, and the market-framework lessons-learned rule "record every tested parameter/specification").

## 6. Test coverage

`tests/test_walkforward.py` covers, on synthetic data (never on this repository's real market snapshots):

- forward return / forward max-drawdown arithmetic against a hand-computed price path,
- that bucket edges at date `t` are unaffected by injecting a future outlier observation,
- rank IC correctness on a perfectly monotonic and a perfectly inverse relationship,
- that `walk_forward_folds` produces strictly expanding, non-overlapping, in-order folds and returns no folds when history is too short,
- that a genuinely stable score→outcome relationship reports `NOT_FALSIFIED_CANDIDATE`,
- that a relationship whose sign flips partway through history is reported as *less* fold-consistent than the stable case and is caught as `FALSIFIED_UNSTABLE_ACROSS_FOLDS`.
