# Lesson Learned — Crypto Entry Timing

Date: 2026-09-26

## Lesson Learned

The first empirical crypto timing run exposed a sample-design issue rather than a strategy conclusion.

A backtest that filters all events by the longest forward horizon before calculating OOS metrics can silently remove recent OOS events. Horizon eligibility must therefore be evaluated independently for 5D, 20D, 60D, 90D, 180D, and 365D outcomes.

The fixed BTC price-timing baseline also produced sparse signals in the recent sample. Future work should improve event coverage through validated state definitions and richer market permission inputs, rather than lowering thresholds simply to increase trade frequency.

The current live BTC state is not an active buy signal. The latest confirmed daily bar remains structurally above MA200 with MA20 > MA50 > MA200, but price has not yet reached the pre-registered 5% pullback zone from the prior 60D high.

## Rule Change

YES

1. Backtest outcome sample eligibility is horizon-specific.
2. OOS reporting must expose outcome sample count (outcome_n) for every horizon.
3. Sparse-event warnings are mandatory before interpreting timing performance.
4. Thresholds must not be loosened merely to manufacture more signals.
5. Live crypto timing remains a two-layer process: confirmed daily structure + current-price trigger monitoring.
6. The in-progress daily candle is excluded from daily decision-state construction.

## Current Validation State

Price-only baseline:
- P0 Data QA: PASS on the current Binance daily sample.
- P1 Signal construction: PASS.
- P2 Episode clustering: PASS.
- P3/P4 outcome construction: CODED; empirical sample is sparse in the current recent window.
- P5 walk-forward: coded, but recent OOS event counts must be interpreted with horizon-specific sample sizes.
- P6 rich permission layer: DATA_NOT_READY.

No live trading rule is promoted by this lesson.
