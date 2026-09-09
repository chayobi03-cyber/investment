# Historical Investment DB V1

Historical market observations and investment decisions start in the existing `investment` repository. A separate Git repository is not required at V1.

Git stores code, schemas, rules, decision records, compact snapshots, tests/validation, and lessons learned. Large unrestricted raw history may move later to DuckDB/Parquet/object storage.

Purpose: preserve `market state -> stock state -> investment decision -> subsequent outcome` for retrospective validation of hit rate, return, drawdown, benchmark-relative performance, and regime-specific failure modes.

## V1 logical entities

- `market_snapshot`: point-in-time market/index/FX/rate/volatility observations, five-axis scores, regime, model/data versions, timestamps.
- `stock_snapshot`: point-in-time ticker price/trading observations, foreign/institution flow, sector, long/mid/short/total scores, rank, action, model/data versions.
- `decision_log`: decision ID/time, ticker, decision type, price, position size, regime, score/rank, reason, confidence, review horizon, model/data version, record origin, source reference.
- `outcome_log`: decision ID, evaluation date/horizon, entry/current price, return, benchmark return, alpha, maximum drawdown, hit flag, thesis status, model version.

## Storage implementation V1

`src/investment_pipeline/history/` provides dataclasses plus `HistoricalStore`, backed by four append-only CSV files under `data/history/`:

- `market_snapshots.csv`
- `stock_snapshots.csv`
- `decisions.csv`
- `outcomes.csv`

The writer is intentionally small and deterministic so it can be connected to the daily panel without introducing a database service dependency.

## Point-in-time integrity rules

1. Historical records are append-only at the logical record level.
2. A repeated record ID with the exact same payload is an idempotent replay; the writer does not append a duplicate row.
3. A repeated record ID with a different payload is rejected as an immutable-record conflict.
4. Past snapshots are not silently recomputed or overwritten with later information.
5. Every decision retains the model/data version used at decision time.
6. Legacy imports retain source reference and are marked as `legacy`.
7. Guessed values from conversation context are not authoritative historical data.
8. Future outcome values are stored separately from decision-time observations.
9. Outcome evaluation must use only information available after the recorded decision time; look-ahead bias is explicitly prohibited.

## Storage policy

### V1 — existing `investment` repo
Use Git for schemas, code, rules, decision logs, compact daily snapshots, tests/validation, and lessons learned.

Do not make Git the permanent home of unrestricted raw market history.

### V2 — reassess external data storage
Reassess when data size becomes material, raw daily data reaches sustained hundreds of MB, retention becomes multi-year at broad-universe scale, multiple systems need direct querying, or database-style queries become a primary workload.

A separate Git repository is justified only by a concrete need for lifecycle separation or cross-project reuse.

## Implementation order

1. Schema and integrity rules — DONE
2. Snapshot writer — DONE
3. Decision logger — DONE
4. Daily panel integration
5. First verified daily records
6. High-confidence legacy backfill
7. Outcome calculation
8. Framework-performance reporting
