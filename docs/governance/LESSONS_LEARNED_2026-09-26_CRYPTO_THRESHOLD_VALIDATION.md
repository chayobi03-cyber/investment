# Lessons Learned — Crypto Threshold Validation

Date: 2026-09-26

## Empirical result

Frozen crypto-market-regime-entry-v0.2 was executed on 3,000 completed BTC-USD daily observations with no threshold retuning. Data QA/PIT passed and the chronological runner, OOS split, and expanding walk-forward completed successfully.

The full sample produced positive median returns at 20D and 60D, but the fixed final 20% OOS failed the preregistered threshold evidence gate: only 12 primary events, 20D median return -2.93%, and 20D positive rate 20%.

Walk-forward results also changed materially by period: WF02 was positive while WF03 and WF04 were negative at 20D. This indicates regime dependence / instability rather than a single consistently reliable timing threshold.

## Rule revision

1. Do not use v0.2 price thresholds as a live BUY trigger.
2. Keep v0.2 thresholds frozen for research; do not retune them against the failed OOS sample.
3. Maintain `BUY_ALLOWED=false` until both threshold evidence and the full permission layer pass.
4. Next experiment must decompose the same thresholds by regime and signal type before considering new thresholds.
5. Enrich the historical permission layer with PIT flow, macro/rates/FX, derivatives, liquidity/risk, regulation/market structure, and geopolitical transmission data.

## Git state

Validation report and lesson are committed. The investment repo remains fail-closed for live crypto BUY decisions.