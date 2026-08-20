# Risk Contract v0.1

## Objective

Preserve capital and reduce the probability and magnitude of permanent impairment while targeting durable long-term compounding.

## Initial research constraints

- Target long-term CAGR research band: 7–10%
- Maximum portfolio drawdown: 20%
- Stress drawdown research ceiling: 30%
- Single security maximum weight: 5%
- Single sector maximum weight: 20%
- Minimum liquid cash / cash-equivalent allocation: 15%
- Leverage: 0 by default
- Forced-liquidation risk: 0

## Priority order

1. Probability of ruin / catastrophic loss
2. Maximum drawdown
3. Stress loss
4. Recovery time
5. Volatility
6. Sortino / downside-adjusted return
7. Calmar
8. CAGR

## Gate rules

- A failed upstream gate blocks downstream strategy promotion.
- Backtest performance cannot override data-integrity failures.
- Risk limits are hard constraints unless explicitly changed in a versioned contract revision.
- All assumptions used in a backtest must be recorded.
