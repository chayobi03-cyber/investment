# Live Market Review Adapter V1

## Purpose

Convert the structured output of the daily market review directly into the existing Historical DB contract. The adapter is the boundary between upstream market/review acquisition and append-only historical persistence.

## Input contract

```json
{
  "as_of": "2026-09-09",
  "model_version": "market-review-v1",
  "data_version": "2026-09-09",
  "market": {
    "source_timestamp": "...",
    "kospi": 0,
    "kosdaq": 0,
    "usdkrw": 0,
    "jpykrw": 0,
    "sp500": 0,
    "nasdaq": 0,
    "vix": 0,
    "us10y": 0,
    "axis_1": 0,
    "axis_2": 0,
    "axis_3": 0,
    "axis_4": 0,
    "axis_5": 0,
    "regime": "..."
  },
  "stocks": [],
  "decisions": []
}
```

`market` is required. `stocks` and `decisions` may be empty. Unknown values remain null/empty; the adapter never fills them by inference.

## Execution

```bash
PYTHONPATH=src python scripts/record_live_market_review.py \
  --input data/input/live_market_review.json \
  --root data/history
```

The result is written to `market_snapshots.csv`, `stock_snapshots.csv`, and `decisions.csv` under the Historical DB root, with `live_review_manifest.json` recording the write counts and versions.

## Idempotency

IDs are deterministic when the input does not provide one. Replaying the same review is a no-op. Reusing an ID with different content remains an immutable-record conflict and is rejected by the HistoricalStore.

## Boundary rule

The adapter persists what the upstream review produced. It does not become a market-data source, valuation engine, or narrative generator. This keeps acquisition/data-quality failures visible and preserves decision-time provenance.
