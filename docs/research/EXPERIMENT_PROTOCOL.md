# Experiment Protocol v0.2

## Baseline universe

Initial asset classes:

- Equity: SPY or a validated broad-market equity proxy
- Intermediate bonds: IEF or validated proxy
- Long-duration bonds: TLT or validated proxy
- Gold: GLD or validated proxy
- Cash: BIL or validated cash proxy

Do not infer that the current tickers are optimal. They are research instruments only.

## Baseline portfolios

### P0 — Equity benchmark

100% equity.

### P1 — Conservative

50% equity / 25% intermediate-or-long bond bucket / 10% gold / 15% cash.

### P2 — Balanced

60% equity / 20% bond / 10% gold / 10% cash.

### P3 — Defensive

40% equity / 30% bond / 15% gold / 15% cash.

## Capital tiers

- T1: KRW 10,000,000
- T2: KRW 50,000,000
- T3: KRW 100,000,000

## Harness boundary

The initial 4 x 3 matrix is an implementation-validation harness using synthetic deterministic returns. It exists to prove case coverage, arithmetic, risk calculation plumbing, and capital-scaling behavior. It is explicitly **not** a strategy backtest and must not be interpreted as investment performance.

## Experimental matrix

4 portfolios x 3 capital tiers = 12 initial cases.

Every case must report:

- CAGR
- Volatility
- Maximum drawdown
- Worst calendar/rolling period
- Recovery time
- Sortino
- Calmar
- Turnover
- Estimated transaction cost
- Stress loss
- Risk contribution
- Capital in KRW at each loss threshold

## Stress scenarios

- Equity -10%
- Equity -20%
- Equity -30%
- Equity -50%
- Broad risk-off: equity -30%, bond -10%, gold +5%
- Later phases: volatility x2, correlation shock toward 1, rate shock, and FX shock where relevant.

## Validation order

Data QA -> baseline calculation -> stress engine -> historical data validation -> historical backtest -> out-of-sample validation -> robustness/Monte Carlo -> paper portfolio.

A strategy cannot be selected because of CAGR alone. No strategy return claim is admissible while M1 data integrity remains blocking.
