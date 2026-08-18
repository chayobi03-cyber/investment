# Next Session Handoff — Capital Preservation Investment Research

## Repository

- Repository: `chayobi03-cyber/investment`
- Branch: `research/capital-preservation-v0.1`
- Base branch: `main`
- Open PR: #1

## Research objective

Build and validate a capital-preservation-oriented investment research system for:

- T1 = KRW 10,000,000
- T2 = KRW 50,000,000
- T3 = KRW 100,000,000

Priority is capital survival and risk-adjusted compounding, not raw CAGR maximization.

## Current gate state

- M0 Risk Contract: GREEN
- M1-A Data Acquisition: GREEN for development sample/fixtures
- M1-B Data Integrity: YELLOW / BLOCKING
- M2-A Risk Calculation: GREEN for deterministic fixtures
- M2-B Stress Calculation: GREEN for deterministic fixtures
- M3 Historical Backtest: BLOCKED

## Non-negotiable rules

1. Do not start or promote historical strategy-performance analysis while M1-B is blocked.
2. Do not silently repair, delete, winsorize, or impute suspicious market observations.
3. Preserve anomaly evidence and classify it as `ERROR` or `REVIEW` with an explicit reason.
4. Never report CI GREEN unless the exact current commit has a retrievable successful workflow run.
5. Synthetic fixtures are engineering validation only; they are not evidence of investment alpha.
6. A high CAGR cannot override a failed data-integrity or risk gate.
7. No leverage by default in the research baseline.

## Immediate next-session tasks

### Task 1 — M1-B Data Integrity remediation

Validate the actual historical data sources for the baseline instruments:

- broad equity proxy / SPY-equivalent
- intermediate bond proxy / IEF-equivalent
- long-duration bond proxy / TLT-equivalent
- gold proxy / GLD-equivalent
- cash proxy / BIL-equivalent

For each series, establish:

- source and dataset identifier
- observation timestamp
- retrieval timestamp
- adjustment status
- split/dividend/corporate-action treatment
- point-in-time availability
- missingness
- duplicate records
- OHLC consistency
- extreme-return review
- independent cross-source confirmation for anomalies

The previously observed SPY low near 69 and BIL discontinuity around 2017 remain explicit QA findings until independently resolved.

### Task 2 — M1 fixture expansion

Extend fixtures to cover:

- normal OHLC
- OHLC range violation
- non-positive price
- extreme but valid market shock
- intraperiod range anomaly
- corporate-action discontinuity
- duplicate timestamp
- missing observation
- timestamp ordering issue
- point-in-time availability violation

Every fixture must specify expected severity and gate behavior.

### Task 3 — 12-case harness audit

Validate exactly:

`4 portfolios × 3 capital tiers = 12 cases`

Portfolio set:

- P0: Equity 100%
- P1: Conservative
- P2: Balanced
- P3: Defensive

Capital tiers:

- T1: 10M KRW
- T2: 50M KRW
- T3: 100M KRW

The harness must emit deterministic case IDs and report percentage and KRW results separately.

### Task 4 — Stress Matrix audit

Validate baseline scenarios:

- Equity -10%
- Equity -20%
- Equity -30%
- Equity -50%
- volatility x2
- correlation shock toward 1
- rate shock
- FX shock where applicable

Require machine-checkable mapping from scenario -> asset shock -> portfolio loss -> KRW loss.

### Task 5 — Current-head CI proof

Run deterministic tests on the latest PR head and record:

- commit SHA
- workflow run ID
- job ID
- test count
- passed/failed count
- conclusion
- artifact availability

Do not infer latest status from older workflow runs.

## Promotion criterion for M1-B GREEN

M1-B can become GREEN only when all critical data series have either:

- independently verified correct source values and adjustment handling, or
- documented, reproducible transformation rules with source evidence.

After M1-B GREEN, M2 historical-data integration can proceed.

## After M1-B GREEN

Proceed in this order:

`validated historical data`
-> `portfolio return series`
-> `M2 historical risk calculation`
-> `stress validation`
-> `12-case historical experiment`
-> `OOS split`
-> `robustness / Monte Carlo`

Do not optimize allocation parameters before a clean baseline is established.

## Session close requirement

At the end of the next session:

1. Update lessons learned.
2. Update this handoff if priorities change.
3. Record exact gate states.
4. Record exact current HEAD SHA.
5. Run current-head CI verification.
6. Commit all session closure documentation and implementation changes.
