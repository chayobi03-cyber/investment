# Investment Gates v0.2

| Gate | Condition | Status |
|---|---|---|
| M0 | Risk Contract defined and versioned | GREEN |
| M1-A | Data acquired with provenance | GREEN for current development sample |
| M1-B | Critical data integrity verified | YELLOW / BLOCKING |
| M2-A | Return, volatility, covariance, drawdown engine | GREEN for deterministic fixture validation |
| M2-B | Stress engine + capital-tier matrix | GREEN for deterministic fixture validation |
| M3 | Asset-allocation backtest | BLOCKED until M1-B GREEN |

## Promotion rule

Promotion requires every upstream gate to be GREEN. A blocked gate cannot be bypassed by human judgment or a high simulated return.

## Current blocking findings

- Suspicious SPY monthly low near 69 against surrounding prices near 686.
- BIL price-level discontinuity around 2017 requiring corporate-action verification.
- The current 12-case matrix and stress matrix use synthetic fixtures for engine validation only; they are not investment performance results.

## Validation evidence

- Deterministic unit tests validate portfolio weighting, volatility, stress-loss arithmetic, and QA issue classification.
- Capital matrix harness covers exactly 4 portfolios x 3 capital tiers = 12 cases.
- Stress harness covers 12 cases x 5 defined scenarios = 60 deterministic results.
- GitHub Actions run 32087687088 passed the deterministic-test stage with 6 tests passing. Later harness changes require a new CI confirmation before the gate can be treated as fully current.

These findings require source-level confirmation or documented adjustment treatment before results are considered auditable.
