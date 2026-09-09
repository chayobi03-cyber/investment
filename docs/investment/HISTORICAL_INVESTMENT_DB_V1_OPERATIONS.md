# Historical Investment DB V1 — Operations

## Purpose

The history system preserves the sequence:

`market state -> stock state -> decision -> future outcome`

The historical store is append-only. A record ID is immutable: repeating the same record is a no-op; changing an existing record under the same ID is rejected.

## Input contracts

### Market CSV

Required:

- `as_of`

Optional columns map directly to `MarketSnapshot`: `source_timestamp`, `kospi`, `kosdaq`, `usdkrw`, `jpykrw`, `sp500`, `nasdaq`, `vix`, `us10y`, `axis_1` ... `axis_5`, `regime`.

### Stock CSV

Required:

- `as_of`
- `ticker`

Optional columns map to `StockSnapshot`: `name`, `close`, `volume`, `foreign_net`, `institution_net`, `sector_code`, `long_score`, `medium_score`, `short_score`, `composite_score`, `rank`, `action`, `data_completeness`.

### Decision JSON

Either a JSON array or an object with a `decisions` array. Each element must match `DecisionLog` fields.

## Commands

```bash
PYTHONPATH=src python -m investment_pipeline.history.cli market \
  --input data/input/market.csv \
  --model-version stock-score-v1 \
  --data-version 2026-09-09

PYTHONPATH=src python -m investment_pipeline.history.cli stock \
  --input data/input/stock_scores.csv \
  --model-version stock-score-v1 \
  --data-version 2026-09-09

PYTHONPATH=src python -m investment_pipeline.history.cli decisions \
  --input data/input/decisions.json

PYTHONPATH=src python -m investment_pipeline.history.cli outcomes \
  --decisions data/history/decisions.csv \
  --prices data/input/price_history.csv \
  --model-version outcome-v1
```

## Safety rules

1. Do not write fabricated values just to make a daily record complete.
2. Keep decision-time data separate from future outcomes.
3. Preserve model and data versions for every decision/snapshot.
4. Mark imported historical records with `record_origin=legacy` where applicable.
5. Do not treat a later financial disclosure as available at an earlier decision timestamp.
6. Outcome evaluation uses future observations only; the entry observation is the decision timestamp, followed by the requested future trading observations.
7. Missing outcome horizons remain missing until sufficient future observations exist.

## Current V1 boundary

This layer is the historical persistence/evaluation system. Market/FX/news data acquisition remains upstream and must feed the explicit input contracts. It is intentionally not replaced with guessed or silently substituted live values.
