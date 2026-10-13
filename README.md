# Investment — Capital Preservation Research

This repository hosts a research program for a capital-preservation-oriented public-equity investment system.

## Initial research tiers

- T1: KRW 10,000,000
- T2: KRW 50,000,000
- T3: KRW 100,000,000

## Research principle

Optimize for long-term capital survival and risk-adjusted compounding before maximizing raw returns.

## Current gates

- M0: Risk Contract
- M1: Data Integrity
- M2: Portfolio Risk Engine
- M3: Asset Allocation Backtest

No strategy is promoted to the next milestone while an upstream gate is not GREEN.

## Market-check operating contract

All user-requested market checks use the canonical [Market Check Workflow V1](docs/market/MARKET_CHECK_WORKFLOW_V1.md). It fixes the collection order, return horizons, source timestamp handling, data-quality gates, response schema, HOTL evaluation record, and decision permissions.

The workflow document is an active research contract, not proof that executable automation is complete. The current market monitor has an open integrity blocker in [Issue #27](https://github.com/chayobi03-cyber/investment/issues/27). Until its remediation and regression tests pass, monitor return and compact risk/quality fields must not authorize entry decisions. `BUY_ALLOWED=false` and `EXECUTION_ALLOWED=false` remain in force.
