# Historical Investment Daily Operation V1

## Purpose

Persist each daily market-review result as an immutable historical record so that the project can later compare:

`market state -> stock state -> decision -> outcome`

## Daily input bundle

The ingestion layer accepts three explicit inputs:

- market CSV: one or more point-in-time market snapshots
- stock CSV: point-in-time stock observations and scores
- optional decisions JSON: explicit investment decisions made from that day's evidence

No missing value is silently inferred. Data and model versions must be supplied by the caller.

## Canonical command

```bash
PYTHONPATH=src python scripts/ingest_daily_review.py \
  --market data/input/market.csv \
  --stock data/input/stock.csv \
  --decisions data/input/decisions.json \
  --model-version stock-score-v1 \
  --data-version 2026-09-09
```

## Storage

Default root: `data/history`

- `market_snapshots.csv`
- `stock_snapshots.csv`
- `decisions.csv`
- `outcomes.csv`
- `daily_ingest_manifest.json`

## Integrity rules

1. Records are append-only.
2. Stable IDs make retries idempotent.
3. Reusing an ID with changed content is a hard conflict.
4. `model_version` and `data_version` are retained with the record.
5. Outcome records are separate from decision-time records to prevent look-ahead contamination.
6. `record_origin=legacy` is required for imported historical conversation records.

## Scope boundary

This component persists and evaluates records. It does not invent market data, estimate missing values, or replace upstream KRX/US/FX data-source validation.

## Next integration

Connect the existing daily market-review/data collection pipeline to produce the three input files automatically. Until that adapter is validated, no live record is fabricated merely to exercise the store.
