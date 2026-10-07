# Crypto Asset Review V0.1

Date: 2026-10-07
Status: PREREGISTERED RESEARCH — does not change the frozen v0.2 rule, the live monitor or buy permission.

Contract: `config/crypto_asset_review_v0.1.json`
Runner: `scripts/crypto/run_asset_review_v0_1.py` (workflow `crypto-asset-review`, weekly and on PRs)

## Why

The v0.2 entry thresholds (Z1 −5%, Z2 −8%, Z3 −12% from the prior 60D high) were set and gated on BTC.
ETH and SOL are now shown in the monitor with the same thresholds, but they move roughly 1.3–2× as much as BTC,
so the same percentage pullback means something different for them. This review asks, per asset:

1. **Frozen fit:** does the unchanged BTC rule pass the existing OOS gate on this asset?
2. **Self-calibrated fit:** does a variant whose depths are scaled to the asset's own volatility pass it?
3. **Screen:** for assets not yet monitored, are they worth adding?

## Self-calibrated variant (asset's own criterion)

`k = σ(asset daily log return) / σ(BTC daily log return)` over the same dates, measured **only on the asset's
first 80% of history** (development segment), rounded to 2 decimals and clipped to [0.5, 3.0].

The frozen classifier is then applied to `drawdown60 / k`, so zone depths become −5k%, −8k%, −12k% and the Z0
no-chase band −2k%. Trend, stabilization, breakout, volume and cooldown rules are unchanged. With k = 1 the
variant reproduces the frozen rule exactly (tested). Walk-forward folds re-measure k on each fold's training rows.

No parameter is fitted to outcomes: k comes from volatility alone, before the OOS window.

## Evaluation

Identical to `CRYPTO_THRESHOLD_VALIDATION_GATE_V0.2.md`: last 20% of each asset's history is OOS, and all
seven conditions must pass (≥20 OOS events, positive median 20D/60D, ≥50% positive 20D/60D, median 20D MAE > −15%,
not >3pp below the simple ≥5% pullback baseline). The baseline stays unscaled for both variants.

History uses the latest contiguous listing segment (gaps > 7 days cut, e.g. a relisting).

## Screen for candidate coins

- ≥ 1,095 days of contiguous Coinbase USD daily history (enough warm-up plus a meaningful OOS window);
- median 90D Coinbase USD volume ≥ $20M (venue liquidity proxy, not global volume);
- no stablecoins / wrapped assets.

Tiers: `ADD_TO_MONITOR_CANDIDATE` (screen + either variant PASS), `WATCH` (screen + best variant ≥ 5/7),
`NOT_RECOMMENDED` otherwise. Within a tier: more checks passed, then shallower worst OOS 20D MAE, then lower
correlation to BTC.

## What a PASS does not mean

Same as the BTC gate: threshold evidence only. Full BUY promotion still requires the PIT permission-layer data,
and capital-preservation checks (max drawdown, worst forward loss) remain primary. Adding an asset to the monitor
or switching it to scaled zones is a separate, explicit decision.
