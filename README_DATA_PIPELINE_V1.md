# Investment Data Pipeline V1

## Scope

Initial universe: the ten fixed KRX names in `src/investment_pipeline/pipeline.py`.

Pipeline:

```text
KRX EOD + KRX investor flow + KRX sector/classification + OpenDART
        ↓
raw source tables (point-in-time metadata retained)
        ↓
data completeness gate
        ↓
raw factors
        ↓
historical percentile normalization using data available at t only
        ↓
normalized factor table
```

This is intentionally upstream of `StockScore V1`. A ranking is not published until critical data completeness is GREEN.

## Source connection

KRX is configuration-driven because the approved KRX Open API product and payload contract depend on the API application. Set:

```bash
export KRX_API_BASE_URL="<approved KRX Open API base URL>"
export KRX_API_KEY="<key>"
export OPENDART_API_KEY="<key>"
```

OpenDART uses its official API endpoints for company information, disclosures and full financial statements. See the official developer guide: https://opendart.fss.or.kr/guide/ .

## Raw table contracts

`data/raw/krx_eod.csv`

Required: `ticker, as_of, open, high, low, close, volume`

`data/raw/krx_flow.csv`

Required: `ticker, as_of, foreign_net, institution_net`

`data/raw/krx_sector.csv`

Required for the first factor layer: `ticker, as_of, sector_code, sector_return_20d, sector_return_60d, sector_breadth`

`data/raw/opendart_financials.csv`

Required when financial factors are enabled: `ticker, available_at, revenue_growth, op_income_growth, roe, debt_ratio, per, pbr`

For financial facts, `available_at` must be the filing/publication availability timestamp, not a later data-vendor revision timestamp.

## Run

From repository root:

```bash
PYTHONPATH=src python scripts/run_data_pipeline.py --raw-dir data/raw --out-dir data/processed
```

Outputs:

- `data/processed/data_completeness.json`
- `data/processed/raw_factors.csv`
- `data/processed/normalized_factors.csv`

No missing value is silently replaced by a fabricated proxy.

## Validation before use

A `_score` column from `normalized_factors.csv` must not be connected to BuyStrength/Action until it passes the walk-forward validation gate. See `docs/investment/WALKFORWARD_VALIDATION_METHODOLOGY_V1.md` and run:

```bash
PYTHONPATH=src python scripts/run_walkforward_validation.py --score-col <col> --price-col close
```
