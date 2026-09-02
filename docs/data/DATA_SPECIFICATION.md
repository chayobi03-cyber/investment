# Data Specification v0.1

## Required data layers

- Market: OHLCV, adjusted prices, volume, market value, beta, volatility.
- Fundamentals: revenue, earnings, free cash flow, leverage, returns on capital, balance sheet.
- Valuation: earnings, book, cash-flow and enterprise-value multiples.
- Macro: rates, inflation, FX, volatility and credit conditions.
- Portfolio: weights, exposures, sector/factor concentration, cash, turnover and liquidity.

## Integrity requirements

1. Point-in-time availability: only information known at the decision timestamp may be used.
2. Look-ahead bias: zero violations.
3. Survivorship bias: universe construction must preserve delisted/failed constituents where applicable.
4. Corporate actions: splits, dividends and mergers must be handled explicitly.
5. OHLC consistency: low <= open/close <= high.
6. Outlier handling: flag first; never silently delete. Real market shocks must remain evidence.
7. Cross-series checks: suspicious discontinuities require independent confirmation.
8. Provenance: source, timestamp, retrieval time, adjustment status and transformation history must be recorded.
9. Reproducibility: identical inputs and code version must reproduce identical research outputs within declared numerical tolerance.

## Current data QA finding

Initial market-data sampling exposed suspicious values that must be quarantined before any performance claim is accepted. Example: a SPY monthly record contained a low near 69 while surrounding open/close values were near 686. A BIL price-level discontinuity around 2017 also requires corporate-action verification. These are QA findings, not assumptions about market behavior.

## Gate

M1 is GREEN only after all critical series pass integrity checks or have documented, independently verified adjustment handling.
