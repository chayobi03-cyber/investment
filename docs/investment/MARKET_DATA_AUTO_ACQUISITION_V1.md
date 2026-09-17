# Market Data Auto Acquisition V1

Date: 2026-09-17
Status: IMPLEMENTATION DESIGN — acquisition layer only; no live order execution

## 1. Objective

Replace the current daily `yfinance` monitor transport with a timestamp-preserving acquisition layer that can automatically collect:

- Korea intraday market/leader data
- US/global market proxy data
- FX / rates / oil / volatility / credit macro inputs
- geopolitical event metadata for later transmission validation

The acquisition layer must preserve `observed_at`, `available_at`, source identity and revision status so that the BUY Trigger Engine remains point-in-time safe.

## 2. Recommended Architecture

```text
Supabase Cron
    |
    +--> Edge Function: market-collector
            |
            +--> KIS adapter
            |      - KOSPI/KOSDAQ index
            |      - Korea leaders / watchlist
            |      - domestic FX and overseas equity observations where supported
            |      - REST snapshot + optional WebSocket collector on long-lived worker
            |
            +--> Alpaca adapter (US fallback / connected market-data path)
            |      - SPY / QQQ / SOXX / TSM / AVGO / AMD etc.
            |      - minute bars / latest trade / snapshot
            |
            +--> FRED / Treasury / EIA adapter
            |      - rates / credit / VIX / oil / broad dollar / macro
            |
            +--> GDELT event adapter (discovery only)
                   - event metadata and publication/observation timestamps
                   - never converted directly into a buy score
            |
            v
      raw market observations
            |
            v
      normalized / derived factors
            |
            v
      permission engine -> alert only
```

## 3. Scheduler Decision

Use **Supabase Cron + Edge Function** as the primary scheduler for periodic snapshots.

Reason:

- Supabase Cron can invoke an Edge Function periodically, including every minute.
- Cron execution history is stored in Postgres and can be monitored.
- Secrets can be kept in Supabase Vault rather than in source code.
- GitHub Actions remains the CI/test/deployment layer, not the live data collector.

Recommended collection frequency:

- Korea session: 1 minute snapshots during market hours
- US session: 1 minute snapshots during the required monitoring window
- Daily macro: after the authoritative source publishes
- Event discovery: every 15 minutes

The four decision checkpoints remain 08:30 / 09:30 / 10:30 / 14:30 KST, but they consume stored observations instead of creating a new ad-hoc request at the checkpoint.

## 4. Source Hierarchy

### A. Korea live / intraday

**Primary candidate: Korea Investment & Securities Open API (KIS).**

KIS provides REST and WebSocket interfaces and publishes official Python examples for domestic real-time trade/quote data. Domestic real-time trade uses WebSocket TR `H0STCNT0`; real-time quotes use `H0STASP0`.

Use KIS credentials only through secrets. Do not commit app keys or app secrets.

### B. US equities

**Primary candidate: Alpaca market data API where credentials/subscription permit.**

The Basic plan provides live IEX equity data and 30 WebSocket symbol subscriptions. SIP provides consolidated all-exchange coverage but requires the higher subscription tier.

For the market engine, the distinction must be stored as `feed=iex|sip`; IEX data must never be labeled as consolidated US market data.

KIS overseas-stock WebSocket is an additional candidate if the project's KIS account supports the required instruments. It can reduce provider count, but coverage must be verified before replacing Alpaca.

### C. Rates / oil / macro

Use authoritative daily sources where the signal is inherently daily:

- U.S. Treasury daily yield curve for Treasury rates
- FRED/ALFRED for VIX, HY OAS, Treasury series, broad dollar and other macro histories
- EIA/FRED for Brent/WTI spot series

For backtests, use ALFRED real-time periods/vintages where revision risk matters.

### D. Geopolitical events

Use GDELT as an automated discovery stream because it updates on a 15-minute cadence and provides structured event/mention records.

GDELT is **not** the canonical truth source for a war or geopolitical claim. Store it as event discovery/evidence metadata, then require source verification before promotion into a transmission state.

## 5. Why not continue with yfinance

The current monitor uses `yfinance` daily bars even at intraday checkpoints. That produces a mislabeled architecture: the workflow timestamp changes, but the underlying observation is still daily.

`yfinance` may remain a diagnostic/research fallback, but it must not be the canonical source for the live monitor or PIT validation dataset.

## 6. Canonical Observation Schema

Every acquired observation must include:

```text
observation_id
source_id
provider
instrument_type
symbol_or_series
market
market_session
observed_at
available_at
timezone
raw_value
unit
feed
revision_status
source_version
collector_version
retrieved_at
quality_status
error_code
```

For bars:

```text
open
high
low
close
volume
trade_count
vwap
```

For quotes:

```text
bid_price
bid_size
ask_price
ask_size
```

No record is accepted without `observed_at <= available_at` and a non-null `source_id`.

## 7. Data QA / Fail-Closed Rules

1. Missing critical Korea or US market data -> `DATA_BLOCKED` for the affected decision.
2. Missing rates/oil/FX data -> retain raw observation state but block any escalation rule that explicitly depends on that cluster.
3. Provider feed changes -> create a new `source_version`; never overwrite historical provenance silently.
4. Duplicate timestamp/instrument records -> deterministic idempotency key; changed content with same key is a hard conflict.
5. Clock/session mismatch -> reject the observation instead of silently converting timezones.
6. IEX must be labeled as IEX, never promoted to `US_CONSOLIDATED`.
7. GDELT event discovery cannot directly raise B2/B3/B4.
8. No order API is exposed from the acquisition function.

## 8. Storage

Recommended separation:

```text
raw_market_observations
raw_event_observations
normalized_market_factors
derived_market_state
permission_decisions
collector_runs
source_health
```

The raw layer is append-only. Derived/normalized tables can be rebuilt from raw observations using the recorded rule/source versions.

## 9. Collector Health

Every run writes:

```text
run_id
started_at
completed_at
collector_version
source_id
requested_count
accepted_count
rejected_count
latency_ms
status
error_summary
```

A health failure is itself observable and must be included in the next market review.

## 10. Implementation Sequence

1. Add provider-neutral observation schema and source registry extension.
2. Build KIS domestic REST snapshot adapter for KOSPI + Samsung + SK hynix + required leaders.
3. Add minute persistence to Supabase.
4. Add Alpaca US snapshot/minute-bar adapter and explicit `feed` field.
5. Add FRED/Treasury/EIA daily collector with publication/available timestamps.
6. Add GDELT discovery collector without score linkage.
7. Rework `auto_market_monitor_v1.py` to read canonical stored observations rather than call yfinance.
8. Start automatic collection and verify one full Korea session.
9. Only after clean collection, generate the P0-P3 PIT backtest dataset.

## 11. Promotion Gate

The acquisition layer is not considered production-ready until all are demonstrated:

- one complete Korea trading session captured automatically;
- no critical timestamp/session defects;
- retry/idempotency tested;
- raw-to-derived lineage reproducible;
- source/feed labels preserved;
- one automatic failure correctly produces `DATA_BLOCKED`;
- historical PIT dataset and live dataset use the same source semantics where applicable.

## 12. Research Boundary

This document defines **data acquisition**, not a trading strategy.

The BUY Trigger Engine remains frozen and separate:

`Market state -> Permission -> BuyStrength -> Action`

No accuracy, expected return or B3/B4 live promotion is implied by successful data collection.
