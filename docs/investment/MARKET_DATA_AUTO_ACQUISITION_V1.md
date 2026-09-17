# Market Data Auto Acquisition V1

Date: 2026-09-17
Status: IMPLEMENTATION — code ready; deployment binding pending

## Objective

Replace the current daily `yfinance` monitor transport with a timestamp-preserving acquisition layer for intraday market-permission checks and later PIT/OOS validation.

## Architecture

```text
Supabase Cron (1 minute)
        |
        v
Edge Function: collect-market-observations
        |
        +--> KIS Open API
        |      -> unified domestic stock snapshots
        |
        +--> later: Alpaca / US market
        +--> later: FRED / Treasury / EIA
        +--> later: GDELT event discovery
        |
        v
Supabase raw market observations
        |
        v
Market Regime / BUY Permission
```

Supabase Cron is the preferred scheduler because it supports minute-level recurring jobs, can invoke Edge Functions, and records job execution history. citehttps://supabase.com/docs/guides/cron

## Implemented now

### KIS collector

`supabase/functions/collect-market-observations/index.ts`

Verified against the official KIS developer examples:

- endpoint `/uapi/domestic-stock/v1/quotations/inquire-price`
- TR ID `FHKST01010100`
- market selector `UN` for integrated domestic market
- default universe is the project's existing ten-stock research universe
- credentials are read only from Edge Function secrets
- each run gets a UUID and each observation stores PIT `observed_at` and `available_at`
- `observed_at` is the collector capture timestamp for that KIS snapshot
- KIS `bsop_date` / `stck_cntg_hour` are provider event metadata preserved inside `raw_payload`; they do not define the snapshot observation timestamp
- `available_at` is assigned after the symbol requests complete and immediately before persistence, so downstream decisions cannot treat a not-yet-stored observation as available
- partial provider failure is reported; missing observations are never imputed
- retries are idempotent through the database identity key

KIS officially documents REST and WebSocket access. The WebSocket domestic KRX trade stream is `H0STCNT0`, while unified/NXT streams are separately identified in current KIS documentation. The V1 collector intentionally starts with REST snapshots because they are easier to deploy, replay, and audit. citehttps://apiportal.koreainvestment.com/docshttps://github.com/koreainvestment/open-trading-api/blob/main/examples_user/domestic_stock/domestic_stock_functions_ws.py

### Raw storage

`supabase/schema/market_observations_v1.sql`

The table stores source/feed identity, market session, timestamps, OHLCV/quote fields, revision status, rule version, and the original KIS payload.

RLS is enabled and direct `anon`/`authenticated` table access is revoked. The collector writes with the server-side Supabase secret key only.

### Scheduler

`supabase/cron/market_collector_v1.sql`

The schedule is intentionally split around the Korea session boundary:

- `23:30-23:59 UTC` = `08:30-08:59 KST`, weekdays, preserving the existing pre-open checkpoint;
- `00:00-05:59 UTC` = `09:00-14:59 KST`, weekdays, continuous 1-minute acquisition;
- `06:00-06:35 UTC` = `15:00-15:35 KST`, weekdays, closing window.

Database timezone remains UTC. The pre-open block is a separate Cron job so the collection starts exactly at 08:30 KST rather than collecting the entire prior UTC hour.

## Secrets / deployment

Required Edge Function secrets:

```text
KIS_APP_KEY
KIS_APP_SECRET
MARKET_COLLECTOR_SECRET
KIS_SYMBOLS (optional)
```

The function uses the current `SUPABASE_SECRET_KEYS` environment when available, falling back to `SUPABASE_SERVICE_ROLE_KEY` for compatibility. Supabase recommends server-side secret keys only in controlled environments and never in browser/client code. citehttps://supabase.com/docs/guides/functions/secretshttps://supabase.com/docs/guides/getting-started/api-keys

Cron-side secrets should be stored in Supabase Vault, not committed to Git. citehttps://supabase.com/docs/guides/database/vault

## Current blocker

The connected Supabase accounts currently expose a `Northstar` project and a separate `GeoAPT` project. The `Northstar` database contains the family-app tables rather than the investment market-data schema, so the collector has **not** been deployed into that project. No schema mutation was made against the wrong project.

Deployment therefore waits for the correct Investment Supabase project/ref binding and its KIS credentials.

## Promotion gate

Acquisition GREEN requires:

1. correct Investment Supabase project bound;
2. `market_observations` schema applied;
3. Edge Function deployed;
4. KIS secrets configured;
5. one successful real observation inserted;
6. repeated runs prove idempotency and timestamp correctness;
7. Cron history shows successful scheduled collection;
8. an induced source failure produces `DATA_BLOCKED` rather than imputation.

Only after acquisition GREEN should the canonical stored data replace the current live monitor input.

## Next implementation

1. Bind the correct Investment Supabase project.
2. Deploy KIS collector and apply schema.
3. Run one real end-to-end Korea session and verify timestamps/duplicates.
4. Add KOSPI index/breadth collector.
5. Add US/global and macro collectors.
6. Switch `auto_market_monitor_v1.py` from `yfinance` to canonical stored observations.
7. Build the P0-P3 PIT backtest dataset.

The BUY Trigger Engine remains frozen and is not promoted by this change. No live orders are created by the acquisition layer.
