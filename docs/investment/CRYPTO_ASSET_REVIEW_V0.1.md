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

## First run — 2026-10-07 (Coinbase data to 2026-10-06)

Run: `crypto-asset-review` #37551191363 (artifact `crypto-asset-review-37551191363`).

| Asset | Rule fit | History | 90D USD vol (Coinbase) | Vol×BTC | Corr | k | Frozen | Scaled | OOS events F/S | OOS med 20D F/S | Worst 20D MAE F/S |
|---|---|---|---|---|---|---|---|---|---|---|---|
| BTC | NEITHER | 3000d | $410M | 1.00 | 1.00 | 1.00 | 4/7 | — | 11 / — | −1.8% / — | −10.2% / — |
| ETH | NEITHER | 3000d | $182M | 1.33 | 0.83 | 1.30 | 6/7 | 6/7 | 10 / 9 | +11.0% / +9.4% | −18.1% / −17.0% |
| SOL | NEITHER | 1938d | $65M | 1.85 | 0.71 | 1.89 | 4/7 | 1/7 | 5 / 6 | +14.5% / −3.1% | −20.0% / −24.2% |
| XRP | NOT_RECOMMENDED | 1182d | $64M | 1.62 | 0.66 | 1.66 | 0/7 | 0/7 | 1 / 2 | — | — |
| LINK | NOT_RECOMMENDED | 2659d | $12M | 1.67 | 0.67 | 1.66 | 4/7 | 4/7 | 9 / 8 | +2.4% / +6.4% | −19.8% / −19.8% |
| BCH | NOT_RECOMMENDED | 3002d | $2M | 1.62 | 0.73 | 1.61 | 4/7 | 4/7 | 18 / 17 | +1.4% / +3.4% | −24.2% / −25.0% |
| LTC | NOT_RECOMMENDED | 3000d | $7M | 1.41 | 0.76 | 1.40 | 1/7 | 0/7 | 5 / 6 | −10.1% / −14.3% | −36.4% / −33.9% |
| DOGE | NOT_RECOMMENDED | 1952d | $11M | 1.73 | 0.72 | 1.75 | 0/7 | 0/7 | 2 / 3 | −13.3% / −19.6% | −23.8% / −23.8% |
| DOT, ADA, AVAX, SUI | NOT_RECOMMENDED | 1238–2029d | $3–14M | 1.6–2.2 | 0.61–0.73 | — | 0/7 | 0/7 | ≤1 | — | — |

Reading:

- **No asset passes, BTC included.** Every OOS window (last 20%, ≈240–600 days) holds fewer than the 20 primary
  events the gate requires, so `minimum_oos_events` fails everywhere. This matches the existing BTC result
  (`THRESHOLD_OOS_FAIL`); the gate is underpowered per asset, not contradicted.
- **ETH fits the frozen rule better than BTC does:** 6/7 with only the event-count check failing (10 < 20);
  OOS median 20D +11.0%, worst 20D MAE −18.1%. Volatility scaling (k = 1.30) does not improve it.
- **SOL:** frozen 4/7 on 5 events; scaling (k = 1.89) makes it worse (1/7). Deeper, volatility-scaled zones are
  **not** supported for SOL. Keep the frozen display; treat SOL signals as weaker evidence than ETH.
- **Self-calibration verdict:** the scaled variant never beats the frozen rule by a check; no reason to switch.
- **Candidates:** none qualifies. XRP is the only one passing the liquidity screen (Coinbase relisting cut its
  history to 1,182 days) but has 1–2 OOS events. LINK and BCH have the best rule fit (4/7) but fail liquidity
  ($12M / $2M Coinbase volume). No coin is added to the monitor.
