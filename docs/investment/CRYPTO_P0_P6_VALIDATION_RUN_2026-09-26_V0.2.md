# Crypto P0-P6 Validation Run — 2026-09-26

Rule version: crypto-market-regime-entry-v0.2
Workflow run: 36218936649
Artifact digest: sha256:ffdfc49e751474f8ad264441fd517b65a0124d0e4053d0fe2502b203c64b6fe2
Status: THRESHOLD_EVIDENCE_FAIL / FULL_BUY_BLOCKED

## Data

- 3,000 completed BTC-USD daily candles.
- History: 2018-07-10 through 2026-09-25.
- Data QA/PIT: PASS.
- Signal source: `src/investment_pipeline/crypto_entry.py`.
- Frozen threshold source: `config/crypto_market_regime_entry_v0.2.json`.
- No threshold retuning.

## Full chronological sample

- Primary events: 90.
- 20D median forward return: +1.42%.
- 20D positive-return rate: 52.27%.
- 60D median forward return: +8.88%.
- 60D positive-return rate: 57.95%.

These full-sample results are descriptive only and are not sufficient for promotion.

## Fixed OOS: final 20%

- Primary events: 12.
- 20D outcome observations: 10.
- 20D median forward return: -2.93%.
- 20D positive-return rate: 20.0%.
- 20D worst forward return: -9.81%.
- 20D median MAE: -6.98%.
- 60D median forward return: +2.12%.
- 60D positive-return rate: 50.0%.
- 60D worst forward return: -18.53%.
- 180D median forward return: -19.73% (n=10).
- 365D median forward return: -39.50% (n=9).

## Threshold evidence gate

Result: FAIL.

Failed checks:
- minimum OOS events >=20: FAIL (12).
- OOS 20D median >0: FAIL.
- OOS 20D positive rate >=50%: FAIL (20%).

Passed checks:
- OOS 60D median >0.
- OOS 60D positive rate >=50%.
- OOS 20D median MAE > -15%.
- OOS 20D median not more than 3 percentage points below simple >=5% pullback baseline.

## Walk-forward

| Fold | Period | Events | 20D median | 20D positive | 60D median | 60D positive |
|---|---|---:|---:|---:|---:|---:|
| WF01 | 2022-08-18 to 2023-06-13 | 7 | -2.40% | 42.9% | +3.45% | 57.1% |
| WF02 | 2023-06-14 to 2024-04-08 | 16 | +1.85% | 68.8% | +16.04% | 68.8% |
| WF03 | 2024-04-09 to 2025-02-02 | 13 | -3.60% | 30.8% | -0.88% | 38.5% |
| WF04 | 2025-02-03 to 2025-11-29 | 10 | -2.93% | 20.0% | +2.12% | 50.0% |
| WF05 | 2025-11-30 to 2026-09-25 | 2 | not measurable | not measurable | not measurable | not measurable |

Interpretation: the same fixed rule behaves differently across chronological regimes. The failure is not a simple lack of historical observations; it is a stability problem concentrated in the later folds.

## Promotion decision

1. `threshold_validation`: FAIL.
2. P6: BLOCK.
3. `BUY_ALLOWED`: false.
4. Automatic orders: disabled.
5. No threshold has been changed after seeing OOS results.

## Next research requirement

Do not tune Z1/Z2/Z3, stabilization, or breakout thresholds yet.

First run a fixed-threshold decomposition by market regime and signal type, then add the missing PIT permission layer: institutional/ETF flow, macro/rates/FX, derivatives history, liquidity/risk, regulation/market structure, and geopolitical transmission.

Only after that evidence is available should a new rule version be considered.