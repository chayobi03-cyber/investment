# Investment — Capital Preservation Research

This repository hosts a research program for a capital-preservation-oriented public-equity investment system.

## Initial research tiers

- T1: KRW 10,000,000
- T2: KRW 50,000,000
- T3: KRW 100,000,000

## Research principle

Optimize for long-term capital survival and risk-adjusted compounding before maximizing raw returns.

## Current gates

- M0: Risk Contract — GREEN
- M1: Data Integrity — YELLOW / BLOCKING
- M2-A: Risk calculation engine — GREEN for deterministic fixture validation
- M2-B: Stress engine / capital matrix — GREEN for deterministic fixture validation
- M3: Historical asset-allocation backtest — BLOCKED until M1 data integrity is GREEN

The current 12-case and stress harnesses use synthetic deterministic fixtures for engine validation only. They are not investment performance results.

No strategy is promoted to the next milestone while an upstream gate is not GREEN.
