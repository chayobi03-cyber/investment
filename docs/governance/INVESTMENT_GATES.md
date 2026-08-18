# Investment Gates v0.1

| Gate | Condition | Status |
|---|---|---|
| M0 | Risk Contract defined and versioned | GREEN |
| M1-A | Data acquired with provenance | GREEN for current development sample |
| M1-B | Critical data integrity verified | YELLOW / BLOCKING |
| M2-A | Return, volatility, covariance, drawdown engine | IN PROGRESS |
| M2-B | Stress engine | PENDING |
| M3 | Asset-allocation backtest | BLOCKED until M1-B GREEN |

## Promotion rule

Promotion requires every upstream gate to be GREEN. A blocked gate cannot be bypassed by human judgment or a high simulated return.

## Current blocking findings

- Suspicious SPY monthly low near 69 against surrounding prices near 686.
- BIL price-level discontinuity around 2017 requiring corporate-action verification.

These findings require source-level confirmation or documented adjustment treatment before results are considered auditable.
