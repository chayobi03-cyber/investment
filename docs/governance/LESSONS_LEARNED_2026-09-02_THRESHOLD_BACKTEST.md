# Lesson Learned — 2026-09-02 Threshold Backtest

## Finding

The first Stress Convergence threshold set was not primarily limited by numeric levels. The larger failure mode was the confirmation topology.

The 2011 risk-off episode could satisfy Energy + Inflation + Credit + VIX even without a confirming Policy/Rates transmission or systemic financial-conditions deterioration.

## Rule update

For future investment early-warning models:

`Claim → Indicator → Threshold → Trigger → Independent Confirmation → Falsifier → Action Level → Backtest → Calibration`

must explicitly include a **confirmation topology** in addition to threshold values.

A raw count such as `N axes breached` is not sufficient where indicators belong to the same causal family.

## New control rule

For Stress Convergence specifically:

1. Inflationary convergence requires Policy/Rates confirmation plus Credit confirmation.
2. Non-inflationary systemic shocks use a separate Credit + Market Stress + Financial Conditions leg.
3. Persistence must be quantified by indicator frequency.
4. Missing historical series must be tagged as `N/A` or `proxy`, never silently converted to zero.
5. Numeric threshold optimization follows topology validation, not the reverse.

## Backtest conclusion

v0.1 is retained as a frozen baseline and rejected for production use. v0.2 is a candidate calibration and remains blocked from actionable capital-allocation use until a full-series rolling backtest confirms lower false-positive behavior without unacceptable loss of lead time.

## Git / artifact rule

Benchmark fixtures, trigger logic, backtest outputs, calibration decisions, and lesson-learned changes are Git-tracked research artifacts and should be committed to the investment research branch before session closure.
