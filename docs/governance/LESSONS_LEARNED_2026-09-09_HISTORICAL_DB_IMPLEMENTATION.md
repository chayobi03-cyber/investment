# Lessons Learned — Historical Investment DB Implementation

Date: 2026-09-09

## Finding

The historical investment layer should begin as a small append-only application interface inside the existing `investment` repository. A database service or second Git repository is unnecessary at V1.

## Implemented rule

Historical records use stable logical IDs and immutable payloads:

- same ID + same payload: idempotent replay, no duplicate row
- same ID + different payload: reject as immutable-record conflict
- new ID: append

Decision-time observations and later outcomes remain separate record types.

## Reusable rule

Every decision record must retain the model version and data version used at the time of the decision. Legacy imports must retain origin/source references. Later outcome information must never mutate the original decision-time record.

## Next implementation gate

Connect the store to the daily market/stock panel only after the daily record schema is populated with verified point-in-time data. Do not backfill uncertain conversational estimates as authoritative observations.

## Storage reassessment trigger

Reconsider DuckDB/Parquet/object storage when retained raw data becomes materially large, multi-year broad-universe history dominates repository size, or direct analytical database queries become a primary workload.
