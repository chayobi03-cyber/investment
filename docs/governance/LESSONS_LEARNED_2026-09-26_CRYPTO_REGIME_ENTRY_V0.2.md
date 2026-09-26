# Lessons Learned — Crypto Market Regime + Entry V0.2

Date: 2026-09-26

## Lesson

The prior crypto specs had separate risk and timing contracts, but the thresholds were not frozen as one integrated research contract. The next experiment therefore needs a versioned Market Regime + Entry contract and a canonical P0-P6 record.

## Rule changes

1. Freeze seven Market Score axes: Trend 20, Flow/Institutional 20, Macro/Liquidity 20, Breadth/Relative Strength 15, Derivatives 10, Volatility/Risk 10, Regulation/Market Structure 5.
2. Keep Market Gate separate from Asset Opportunity Score and Buy State.
3. Freeze explicit macro, derivatives, volatility, breadth, pullback, stabilization, and breakout thresholds before the next OOS run.
4. Keep BTC as the primary validation asset; ETH/SOL remain secondary and permissioned.
5. Make P0-P6 a canonical decision record with PIT timestamps, provenance, signal, episode, execution, risk, walk-forward, and promotion evidence.
6. Any threshold change requires a new rule version plus fresh OOS and walk-forward evaluation.

## Status

- v0.2 preregistered in `config/crypto_market_regime_entry_v0.2.json`.
- v0.2 contract documented in `docs/investment/CRYPTO_MARKET_REGIME_ENTRY_V0.2.md`.
- canonical P0-P6 schema added at `schemas/crypto_p0_p6_v0.2.schema.json`.
- live trading and automatic orders remain disabled.
- next engineering step: wire the frozen contract into the existing crypto monitor/backtest and run a fresh chronological P0-P6 evaluation.