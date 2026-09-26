# Crypto Derivatives Archive V0.1

Date: 2026-09-26
Status: RESEARCH SPEC — COVERAGE PLAN / NOT YET INGESTED

## Goal

Build a long-horizon derivatives PIT store for BTC, ETH and SOL without pretending that exchange-native analytics APIs provide uninterrupted historical coverage.

## Canonical instruments

Primary research instrument:
- Binance USD-M perpetual for BTC, ETH and SOL.

Secondary context:
- Binance continuous futures/basis where available;
- other major exchange markets only when the metric is genuinely cross-exchange comparable.

## Required daily features

| Feature | Required | Research use |
|---|---|---|
| 8h funding rate | yes | crowding / carry |
| 24h OI change | yes | leverage expansion |
| 1d basis | preferred | futures premium |
| Top-trader L/S positions | preferred | directional crowding |
| Taker buy/sell | preferred | aggressive flow |
| Liquidations | preferred | forced deleveraging |
| Mark/index price | yes | derivative/spot dislocation |

## Archive hierarchy

### Layer A — exchange-native

Use Binance APIs for:
- current observations;
- recent history;
- exact contract semantics.

Do not assume long-run coverage for OI statistics or top-trader ratios. Binance documentation states those analytics endpoints expose only the latest 30 days.

### Layer B — historical archive

Use Coin Metrics market-level history as the preferred archive where the requested market and metric have coverage.

Required archive discovery before ingestion:
- market identifier;
- coverage start/end;
- metric support;
- frequency;
- exchange timestamp;
- database timestamp;
- contract/margin semantics.

Coin Metrics exposes catalog endpoints for discovering market coverage and time ranges and time-series endpoints for market open interest, funding rates and liquidations.

### Layer C — gap fill

A secondary provider may fill a gap only when:
- the underlying economic definition is equivalent;
- instrument mapping is explicit;
- timestamps are compatible;
- overlap validation passes;
- licensing permits research use.

Never silently concatenate two vendors.

## Stitching protocol

For every provider transition store:
- source_id;
- provider_market_id;
- canonical_market_id;
- contract_type;
- margin_asset;
- quote_asset;
- coverage_start;
- coverage_end;
- methodology_version;
- overlap_start/end;
- overlap_n;
- mean_abs_discrepancy;
- max_abs_discrepancy;
- transition_status.

Transition_status:
- PASS;
- REVIEW;
- BLOCKED.

## PIT publication policy

The source observation timestamp is not the same thing as decision eligibility.

Each row retains:
- observation_timestamp;
- exchange_time where available;
- database_time where available;
- available_at;
- ingested_at.

For backtest use:

available_at <= decision_timestamp

A later database retrieval time must not be used as a substitute for the economic publication time. When source publication semantics are uncertain, use a conservative lag and mark the series as REVIEW until verified.

## Backfill strategy

1. Discover coverage for BTC/ETH/SOL before downloading.
2. Download archive data in chronological partitions.
3. Hash every raw file/partition.
4. Normalize to canonical metric names.
5. Validate duplicates, gaps, timestamps and units.
6. Preserve source timestamps.
7. Add available_at using source-specific publication rules.
8. Run overlap checks against Binance on overlapping dates.
9. Promote only validated partitions into the PIT store.

## Minimum history target

Target:
- BTC: 2020-present where derivatives coverage is valid;
- ETH: earliest valid perpetual coverage available from the archive;
- SOL: earliest valid perpetual coverage available from the archive.

Do not create artificial pre-listing observations.

## Promotion gate

Derivatives permission becomes eligible for P0/P6 only when:
- BTC required fields have validated long history;
- ETH/SOL coverage is explicit;
- provider transitions are documented;
- PIT timestamps pass look-ahead tests;
- missingness is measured;
- overlap checks pass;
- no current-only metric is backfilled into historical dates.

Until then:
DERIVATIVES_DATA_NOT_READY -> permission BLOCKED
