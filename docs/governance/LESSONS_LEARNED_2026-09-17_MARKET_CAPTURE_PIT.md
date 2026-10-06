# Lesson Learned — Market Capture PIT Timestamp

Date: 2026-09-17
Scope: market auto-acquisition / point-in-time data integrity

## Finding

A provider event timestamp is not automatically the observation timestamp of an API snapshot.

For the KIS current-price REST snapshot, `stck_cntg_hour` represents provider transaction/last-trade time. It must not be used as the timestamp of the collector's snapshot observation.

## Failure Mode

If `stck_cntg_hour` is used as `observed_at` for minute-level REST polling, repeated polls during periods without a new trade can share the same timestamp. That can:

- collapse distinct snapshots under the uniqueness key;
- make the database appear less frequent than the actual collector;
- distort point-in-time decision reconstruction;
- create false temporal relationships in backtests.

## Rule Revision

For market snapshot acquisition:

1. `observed_at` = collector capture timestamp for the successful source response;
2. `available_at` = downstream availability/persistence timestamp and must satisfy `available_at >= observed_at`;
3. provider event timestamps such as KIS `bsop_date` / `stck_cntg_hour` remain in `raw_payload` as source metadata;
4. no provider event timestamp may replace the collector capture timestamp unless the source explicitly defines it as the snapshot publication time;
5. PIT consumers must use `available_at <= decision_timestamp` as the data availability gate.

## Verification

The KIS collector was corrected to capture `observed_at` at response time and assign `available_at` immediately before persistence. The GitHub Actions Market Collector Check then passed both TypeScript type-check and Deno format validation on the corrected commit.

## Operational Gate

Real-data E2E remains blocked until the correct Investment Supabase project/ref and KIS credentials are connected. No data was written to unrelated connected projects.
