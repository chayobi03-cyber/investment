# Capital Preservation Investment Research Roadmap v0.1

## Objective

Research an investment system for capital tiers of KRW 10M, 50M, and 100M that prioritizes avoidance of catastrophic permanent loss and durable risk-adjusted compounding.

## Milestones

- M0 Risk Contract: define capital tiers, drawdown limits, position limits, liquidity rules, leverage rules, and promotion gates.
- M1 Data Integrity: establish provenance, point-in-time rules, corporate-action handling, outlier detection, and reproducibility requirements.
- M2 Portfolio Risk Engine: calculate return, volatility, covariance/correlation, drawdown, risk contribution, and stress loss.
- M3 Asset Allocation Backtest: compare baseline allocations across all three capital tiers.
- M4 Position Sizing: add position-level risk budgets and concentration controls.
- M5 Entry/Exit/Rebalance: test investment lifecycle rules.
- M6 OOS/Stress/Monte Carlo: validate robustness and failure modes.
- M7 Paper Portfolio: compare simulated execution with research results.
- M8 Governance: establish decision provenance, review, and auditability.
- M9 Capital Ramp: validate staged capital promotion.

## Promotion principle

No milestone may be promoted while an upstream gate is not GREEN. A high CAGR does not override a failed data-integrity or risk gate.
