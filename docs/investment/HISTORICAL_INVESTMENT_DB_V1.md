# Historical Investment DB V1

Historical market observations and investment decisions start in the existing `investment` repository. A separate Git repository is not required at V1.

Git stores code, schemas, rules, decision records, compact snapshots, and validation artifacts. Large raw historical datasets may move later to DuckDB/Parquet/object storage.

Purpose: preserve `market state -> stock state -> investment decision -> subsequent outcome` for retrospective validation of hit rate, return, drawdown, benchmark-relative performance, and regime-specific failure modes.

## V1 logical entities

- `market_snapshot`: point-in-time market/index/FX/rate/volatility observations, five-axis scores, regime, model/data versions, timestamps.
- `stock_snapshot`: point-in-time ticker price/trading observations, foreign/institution flow, sector, long/mid/short/total scores, rank, action, model version.
- `decision_log`: decision ID/time, ticker, decision type, price, position size, regime, score/rank, reason, confidence, review horizon, model version, record origin.
- `outcome_log`: decision ID, evaluation date/horizon, entry/current price, return, benchmark return, alpha, maximum drawdown, hit flag, thesis status.

## Point-in-time integrity rules

1. Historical records are append-only at the logical record level.
2. Past snapshots are not silently recomputed or overwritten with later information.
3. Every decision retains the model/data version used at decision time.
4. Legacy imports retain source reference and are marked as legacy.
5. Guessed values from conversation context are not authoritative historical data.
6. Future outcome values are stored separately from decision-time observations.
7. Look-ahead bias is explicitly prevented in evaluation.

## Storage policy

### V1 — existing `investment` repo
Use Git for schemas, code, rules, decision logs, compact daily snapshots, tests/validation, and lessons learned.

Do not make Git the permanent home of unrestricted raw market history.

### V2 — reassess external data storage
Reassess when data size becomes material, raw daily data reaches sustained hundreds of MB, retention becomes multi-year at broad-universe scale, multiple systems need direct querying, or database-style queries become a primary workload.

A separate Git repository is justified only by a concrete need for lifecycle separation or cross-project reuse.

## Implementation order

1. Schema and integrity rules
2. Snapshot writer
3. Decision logger
4. Daily panel integration
5. First verified daily records
6. High-confidence legacy backfill
7. Outcome calculation
8. Framework-performance reporting
