# Observation → P0~P6 Backtest Result — 2026-09-22

## Execution status

- GitHub Actions run: `35664235537`
- Head commit: `ff9308e2942b9f49586d93424efef46c37e9b1ff`
- Result: CI SUCCESS
- Artifact: `historical-pit-p0-p6-35664235537`
- Artifact SHA-256: `4c8766921174f73839a04acd3eb0749d7dfaa7948f765365db23c3747d48b5dc`
- Tests: 10 passed
- Historical series requested/downloaded: 26 / 26
- Historical observations: 155,297
- Asset-level observation rows: 71,295
- Episode rows: 1,216
- Historical span requested: 2000-01-01 → 2026-09-21

## PIT status

This run is **not a strict archival PIT database**.

`pit_status=VENDOR_HISTORY_PROXY` and `pit_archival_revisions=false`.

The run is therefore suitable for connecting and exercising the research pipeline, but it must not be treated as promotion-grade PIT evidence. In particular, the current historical builder uses vendor historical price data and adjusted equity OHLC; future corporate-action/dividend information can affect the adjusted series. A strict PIT release should use action-aware/as-published price vintages or an archival source.

## P0~P5 results

Entry definition is the next available session open after the episode trigger. Reported returns are mean forward returns across evaluable episodes; positive rate is the fraction of episodes with positive forward return. MAE is the worst within-horizon low relative to entry.

### Development

| Gate | Episodes | 5D mean | 5D positive | 20D mean | 20D positive | 20D MAE | 60D mean | 60D positive |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| P0 | 796 | +0.65% | 55.0% | +2.20% | 56.7% | -56.01% | +6.61% | 60.9% |
| P1 | 796 | +0.65% | 55.0% | +2.20% | 56.7% | -56.01% | +6.61% | 60.9% |
| P2 | 780 | +0.62% | 55.1% | +2.09% | 56.5% | -56.01% | +6.42% | 60.9% |
| P3 | 349 | +0.39% | 51.6% | +1.74% | 55.0% | -56.01% | +7.03% | 59.9% |
| P4 | 207 | +0.10% | 48.8% | +0.05% | 49.3% | -50.00% | +5.22% | 58.0% |
| P5 | 74 | +0.08% | 50.0% | +0.46% | 52.7% | -32.32% | +6.80% | 56.8% |

### Validation

| Gate | Episodes | 5D mean | 5D positive | 20D mean | 20D positive | 20D MAE | 60D mean | 60D positive |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| P0 | 120 | +0.38% | 55.0% | +1.06% | 53.3% | -54.08% | +8.95% | 55.0% |
| P1 | 120 | +0.38% | 55.0% | +1.06% | 53.3% | -54.08% | +8.95% | 55.0% |
| P2 | 113 | +0.20% | 54.0% | +0.28% | 52.2% | -54.08% | +9.00% | 54.9% |
| P3 | 53 | -0.21% | 54.7% | -1.25% | 43.4% | -54.08% | +12.70% | 49.1% |
| P4 | 40 | +0.38% | 60.0% | -1.85% | 40.0% | -54.08% | +6.08% | 42.5% |
| P5 | 14 | -0.90% | 42.9% | -5.41% | 35.7% | -54.08% | +2.98% | 50.0% |

### OOS

| Gate | Episodes | 5D mean | 5D positive | 20D mean | 20D positive | 20D MAE | 60D mean | 60D positive |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| P0 | 300 | +1.35% | 59.1% | +2.42% | 52.8% | -43.29% | +10.71% | 58.6% |
| P1 | 300 | +1.35% | 59.1% | +2.42% | 52.8% | -43.29% | +10.71% | 58.6% |
| P2 | 286 | +1.21% | 58.2% | +2.56% | 52.9% | -43.29% | +10.25% | 58.5% |
| P3 | 146 | +1.78% | 62.5% | +3.33% | 58.0% | -43.29% | +12.45% | 57.7% |
| P4 | 112 | +1.74% | 61.8% | +3.89% | 57.7% | -43.29% | +12.42% | 62.2% |
| P5 | 20 | +1.47% | 70.0% | +9.90% | 70.0% | -13.83% | +19.46% | 60.0% |

## Frozen-threshold walk-forward diagnostic

The workflow also evaluated the frozen gate definitions by calendar-year folds; no threshold fitting was performed on the test fold.

| Gate | Year folds | Positive fraction of annual mean 20D returns | Median annual mean 20D | Min | Max |
|---|---:|---:|---:|---:|---:|
| P0 | 27 | 85.2% | +2.29% | -2.85% | +9.89% |
| P1 | 27 | 85.2% | +2.29% | -2.85% | +9.89% |
| P2 | 27 | 81.5% | +2.29% | -3.11% | +9.89% |
| P3 | 27 | 66.7% | +2.46% | -5.50% | +7.50% |
| P4 | 23 | 52.2% | +1.68% | -4.87% | +7.64% |
| P5 | 23 | 56.5% | +2.29% | -9.87% | +35.83% |

## Interpretation constraints

1. The empirical result demonstrates that the end-to-end pipeline now executes on a large historical panel; it does **not** establish a deployable buy-timing rule.
2. P1 is currently almost non-discriminating: in all three splits P1 has the same episode count and outcome metrics as P0. This means its current threshold is not adding information.
3. P3/P4/P5 show materially smaller samples. The OOS P5 sample is only 20 episodes, so the +9.90% 20D mean must be treated as high-variance evidence, not as a stable expected return estimate.
4. Validation P5 is negative (-5.41% mean 20D, 35.7% positive), while OOS P5 is positive. This split difference is a direct reason not to promote P5.
5. The framework remains downside-first: some individual episodes experienced very large adverse excursions. Mean return alone is insufficient.
6. Current attribution is market-transmission-only and can be `INFERRED`; it is not equivalent to verified company/event evidence.
7. P6 is explicitly `DATA_NOT_READY` because archival PIT fundamentals are not connected. No fundamental score was fabricated.

## Next gate

Before using these results to modify live MarketScore/BuyStrength:

- replace the vendor-history proxy with strict PIT/as-published or action-aware historical vintages;
- connect PIT fundamentals and complete P6;
- correct the metric semantics for the current `false_positive_rate` field, which is derived from the 20D positive-return label rather than an independently specified classification target;
- add transaction costs/slippage and execution constraints;
- run sensitivity/falsification tests with frozen thresholds;
- rerun the complete P0→P6 evaluation and only then assess whether the research evidence supports any rule revision.

**Status: pipeline execution GREEN; strict PIT / P6 / promotion status NOT GREEN.**
