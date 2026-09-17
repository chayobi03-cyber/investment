# Lessons Learned — 2026-09-08 Walk-Forward Validation Harness

## What changed

The repository's frozen specs (`MARKET_DECISION_FRAMEWORK_RESEARCH_2026-09-08.md`, `MARKET_REGIME_ENGINE_V1.md`) had required point-in-time out-of-sample and walk-forward validation ("Experiment A: score monotonicity") since 2026-09-08, but no code implemented it — only `normalize_point_in_time` existed (point-in-time normalization, not evaluation). Added `src/investment_pipeline/walkforward.py`, `tests/test_walkforward.py`, `scripts/run_walkforward_validation.py`, and `docs/investment/WALKFORWARD_VALIDATION_METHODOLOGY_V1.md`.

## Findings

1. **Bucketing can leak the future even when the score itself doesn't.** Using full-sample quantile edges to bucket an otherwise point-in-time score still lets a decision at date `t` be influenced by observations after `t`, because the bucket boundary shifts. Fixed by recomputing quantile edges from an expanding window at each date.
2. **A pooled full-sample IC can hide a regime flip.** A relationship that is strongly positive in the first half of history and strongly negative in the second half can average to a near-zero, ambiguous full-sample rank IC — which would pass a naive "does each fold match the full-sample sign" check almost by accident. Fold-to-fold sign agreement (do the folds agree with *each other*, not with the pooled average) is a stricter and more honest consistency check, and is what actually operationalizes "정합성" (consistency) as an explicit, testable property rather than a single backtest number.
3. **The State layer / Outcome layer separation from the Market Decision Framework (§9) needed a concrete implementation**, not just a naming convention: `attach_forward_outcomes` is intentionally a separate function from anything that touches score construction, so a future score can never accidentally consume its own evaluation target.
4. **No real market/stock data is connected yet** (`data/` does not exist in this repository). The harness is therefore validated only against synthetic fixtures with a known, hand-constructed ground-truth relationship. It must not be run against fabricated numbers as if they were a real validation result — `scripts/run_walkforward_validation.py` refuses to run without `data/processed/normalized_factors.csv` produced by the real data pipeline.

## Rule Update

`Before any score/rank column produced by the data pipeline is connected to BuyStrength/Action, it must be run through run_experiment_a (walk-forward score monotonicity) and reach at least NOT_FALSIFIED_CANDIDATE on the frozen historical panel, in addition to the existing completeness gate. NOT_FALSIFIED_CANDIDATE is necessary, not sufficient — Levels 6-10 of the validation protocol (parameter sensitivity, transaction costs, cross-market validation, multiple-testing correction, shadow operation) still apply before live use.`

## Next Gate

Unchanged from `LESSONS_LEARNED_2026-09-08_DATA_PIPELINE.md`: connect the approved KRX/OpenDART credentials, collect the ten-name raw dataset, run the data pipeline, then run `scripts/run_walkforward_validation.py` against the resulting `normalized_factors.csv` to produce the first real (non-synthetic) Experiment A report before any Stock Score / Market Score is used to size a trade.
