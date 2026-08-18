# Next Session Handoff — Capital Preservation Investment Research

## Repository

- Repository: `chayobi03-cyber/investment`
- Branch: `research/capital-preservation-v0.1`
- Base branch: `main`
- Open PR: #1 (Draft)

## Research objective

Build and validate a capital-preservation-oriented investment research system for:

- T1 = KRW 10,000,000
- T2 = KRW 50,000,000
- T3 = KRW 100,000,000

Priority is capital survival and risk-adjusted compounding, not raw CAGR maximization.

## Current gate state at handoff

- M0 Risk Contract: GREEN
- M1-A Data Acquisition: GREEN for development fixture/sample
- M1-B Data Integrity: YELLOW / BLOCKING
- M2-A Risk Calculation: GREEN for deterministic fixtures
- M2-B Stress Calculation: GREEN for deterministic fixtures
- M3 Historical Backtest: BLOCKED

## Non-negotiable rules

1. Do not start or promote historical strategy-performance analysis while M1-B is blocked.
2. Do not silently repair, delete, winsorize, or impute suspicious market observations.
3. Preserve anomaly evidence and classify it with an explicit reason.
4. Never report CI GREEN unless the exact current commit has a retrievable successful workflow run.
5. Synthetic fixtures are engineering validation only; they are not evidence of investment alpha.
6. A high CAGR cannot override a failed data-integrity or risk gate.
7. No leverage by default in the research baseline.
8. Historical data evidence and synthetic regression fixtures must remain separate.

# Next Session Prompt

## Mission

Resume at **M1-B Data Integrity remediation** and do not enter historical backtesting or optimization unless M1-B is independently proven GREEN.

## Phase 0 — exact-head orientation

1. Verify repository, branch, PR #1, and exact current HEAD SHA.
2. Verify current CI status for that exact SHA.
3. Inspect the latest failed job before changing code.
4. Preserve all useful failure evidence.

## Phase 1 — financial-information acquisition strategy

Before broadening ingestion, evaluate and choose a small, defensible financial-information source stack for the five baseline ETFs:

- SPY
- IEF
- TLT
- GLD
- BIL

For each candidate source, assess:

- authoritative status
- historical depth
- OHLC availability
- corporate-action coverage
- dividend/distribution coverage
- publication timestamp availability
- point-in-time capability
- API stability
- rate limits
- terms/licensing/redistribution constraints
- reproducibility/versioning
- cost
- operational maintenance burden

Prefer **low-risk / high-ROI** sources. Do not add vendors merely to increase vendor count.

Required output:

`source -> purpose -> evidence strength -> PIT capability -> licensing risk -> operational cost -> decision`

Separate the roles of:

- official issuer / regulator evidence
- primary historical market-data feed
- independent reconciliation feed
- PIT/event-date evidence

## Phase 2 — real historical ingest

Run the ingest on the CI runner or another execution environment with outbound access.

For each of the five series, capture:

- exact source URL / dataset identifier
- retrieval UTC timestamp
- requested range
- actual first/last observation
- row count
- raw file hash
- normalized file hash
- schema version
- adjustment status
- corporate actions
- distribution events
- source-response metadata

Never silently overwrite raw source data.

## Phase 3 — machine QA

Run and record:

- duplicate timestamps
- missing observations
- timestamp ordering
- OHLC consistency
- positive price checks
- extreme-return review
- split/dividend consistency
- adjustment-rule consistency
- source-to-source reconciliation

For each finding emit:

`series + date + rule + observed value + expected/reference + classification + action + evidence pointer`

## Phase 4 — known anomaly closure

### SPY

Resolve the previously flagged approximately-69 low by collecting:

- raw primary observation
- independent source observation
- official/reference evidence where available
- classification
- quarantine/replacement decision
- transformation provenance

The observation must remain auditable even if excluded from normalized research data.

### BIL

Verify the 2017 reverse-split treatment against an authoritative corporate-action record and demonstrate that the normalized return series follows the declared adjustment rule.

## Phase 5 — PIT evidence

Do not mark PIT GREEN merely because historical price dates are correct.

Establish whether the chosen data source can prove:

`observation -> source publication/availability time -> research decision time`

For sources that cannot establish this, explicitly mark PIT as unavailable and identify the safest alternative evidence path.

## Phase 6 — machine evidence

Generate and retain:

`artifacts/baseline_history/M1B_EVIDENCE.json`

plus raw/normalized data artifacts and hashes.

The evidence must contain at minimum:

- exact commit SHA
- generation timestamp
- source identifiers
- retrieval timestamps
- row counts
- hashes
- QA results
- corporate-action results
- cross-source reconciliation results
- PIT result
- critical failures
- final machine gate result

## Phase 7 — M1-B promotion decision

M1-B GREEN only if:

1. all five baseline series have acceptable primary provenance;
2. independent reconciliation is available and passes defined tolerance or documented exceptions;
3. corporate-action handling is verified;
4. duplicate/missing/OHLC/timestamp checks pass or have explicit reviewed exceptions;
5. no unresolved critical anomaly remains;
6. PIT is proven or formally bounded by an approved evidence limitation;
7. machine evidence artifact is complete and hash-linked;
8. exact current-head CI is GREEN.

Otherwise remain `YELLOW / BLOCKING`.

## Phase 8 — after M1-B GREEN only

Proceed in this order:

`validated historical data`
-> `portfolio return series`
-> `M2 historical risk calculation`
-> `stress validation`
-> `12-case historical experiment`
-> `OOS split`
-> `robustness / Monte Carlo`

Do not optimize allocation parameters before a clean baseline is established.

## Session close requirements

1. Update lessons learned only with observed facts.
2. Record what worked, what failed, what is worth automating, and what is useful workflow guidance.
3. Prefer changes that reduce risk and increase ROI; do not add low-value process.
4. Record exact current HEAD SHA.
5. Run and inspect exact-head CI.
6. Record final gate states.
7. Commit implementation and governance changes.
8. Preserve M1-B fail-closed status unless evidence genuinely proves GREEN.
