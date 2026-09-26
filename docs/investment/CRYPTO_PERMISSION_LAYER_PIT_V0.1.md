# Crypto Permission Layer PIT V0.1

Date: 2026-09-26
Status: RESEARCH SPEC — CODED STRUCTURE / NOT VALIDATED / NOT LIVE

## Objective

Extend the frozen crypto entry engine from price-only timing to a point-in-time permission layer.

Rules:
- fail closed when required PIT evidence is unavailable;
- never use a value whose available_at is after decision_timestamp;
- preserve raw evidence, source identity, observed timestamp and availability timestamp;
- never backfill a current regulatory or market-state label into historical dates;
- threshold changes require a new rule version and fresh OOS/walk-forward evaluation.

## Architecture

Cross-asset spot
-> Macro/Liquidity
-> Derivatives
-> Regulation/Market Structure
-> Geopolitical Transmission
-> PIT as-of join
-> Market Score / Regime
-> Crypto Entry State
-> P0-P6

The existing BTC price engine remains responsible for trend, pullback zones, stabilization, breakout, next-open execution and forward outcomes.

The permission layer is responsible for market-state health, hard macro/derivatives blocks, cross-asset confirmation, regime confirmation, freshness and provenance.

## BTC / ETH / SOL cross-asset panel

Initial universe:
- BTC: BTC-USD / BTCUSDT
- ETH: ETH-USD / ETHUSDT
- SOL: SOL-USD / SOLUSDT

Derived features:
- ETH/BTC 20D relative return;
- SOL/BTC 20D relative return;
- BTC/ETH/SOL 20D and 60D momentum;
- 20D cross-asset dispersion;
- percentage of the three assets above MA20;
- percentage above MA50;
- BTC leadership state;
- alt-rotation confirmation.

This three-asset panel is a cross-asset confirmation layer, not a replacement for broad alt-universe breadth.

## Macro / liquidity

Required:
- DXY 20D change;
- U.S. 10Y 10D change;
- U.S. 10Y real yield 10D change;
- WTI 5D change;
- USD/KRW 20D change.

Preferred sources:
- FRED DGS10;
- FRED DFII10;
- FRED DCOILWTICO;
- official FX source with dated observations for USD/KRW;
- DXY source with explicit historical timestamp and provenance.

## Derivatives

For BTC, ETH and SOL retain:
- funding rate;
- open interest;
- basis;
- top-trader long/short position ratio;
- taker buy/sell volume;
- liquidation volume where available;
- mark/index price.

Source hierarchy:
1. Coin Metrics market-level historical archive where coverage exists;
2. Binance exchange-native data for current/recent data and gap-fill;
3. another archive provider only after coverage/methodology/licensing verification.

Binance is not the sole long-history source. Its open-interest statistics and top-trader long/short endpoints document a latest-30-day availability window, while its funding history can be queried with timestamps but still requires coverage validation.

Provider stitching requires source_id, instrument mapping, coverage range, methodology, overlap period and overlap discrepancy statistics. Silent provider splicing is forbidden.

## PIT timestamp contract

Every observation carries:
- observation_timestamp;
- available_at;
- source_id;
- source_record_id where available;
- unit;
- value;
- ingested_at;
- provenance_hash.

Eligibility:
available_at <= decision_timestamp

Forward fill is disabled by default. Any permitted carry-forward must use a series-specific maximum staleness rule.

## Daily canonical representation

One row per asset x series_id x decision_date.

Raw source observations are retained separately. Derived metrics reference the raw observations used.

## Permission outputs

- market_score 0-100;
- raw_regime R1-R6;
- confirmed_regime R1-R6;
- market_gate GREEN/YELLOW/RED;
- macro_block;
- derivatives_block;
- cross_asset_confirmation;
- permission_status;
- blocker_codes;
- evidence_completeness;
- source_coverage.

Missing required permission evidence => DATA_NOT_READY / BLOCKED.

## Research sequence

1. frozen price signal;
2. PIT permission layer;
3. regime decomposition;
4. signal-type decomposition;
5. fixed OOS;
6. walk-forward stability;
7. stress-event review;
8. only then consider a new rule version.

No threshold tuning is permitted before this sequence is complete.

## Current boundary

This version establishes the schema/config/validation layer and the BTC/ETH/SOL spot acquisition adapter.

It does not claim complete historical derivatives coverage, complete historical regulatory labels, validated market scores, or P6 promotion.
