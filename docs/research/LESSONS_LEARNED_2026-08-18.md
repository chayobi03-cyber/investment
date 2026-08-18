# Lessons Learned — 2026-08-18

## Session scope

This session initialized and advanced the capital-preservation investment research framework for three capital tiers:

- T1: KRW 10,000,000
- T2: KRW 50,000,000
- T3: KRW 100,000,000

The session intentionally prioritized data integrity and deterministic risk calculation before any historical strategy-performance claims.

## 1. Capital preservation must be the primary optimization objective

Raw CAGR is not the primary gate. The evaluation order is:

1. Probability of ruin / catastrophic loss
2. Maximum drawdown
3. Stress loss
4. Recovery time
5. Volatility
6. Sortino
7. Calmar
8. CAGR

A strategy with higher CAGR must not automatically outrank a lower-CAGR strategy with substantially better downside characteristics.

## 2. Capital tiers must be tested separately

The same percentage allocation can produce different implementation behavior at KRW 10M, 50M, and 100M because minimum trade sizes, transaction costs, diversification granularity, and implementation constraints differ. Percentage metrics and absolute KRW loss must therefore both be reported.

## 3. Data QA is a hard promotion gate

Initial market-data sampling exposed suspicious observations. A SPY monthly record contained a low near 69 while surrounding open/close values were near 686. A BIL price-level discontinuity around 2017 also required corporate-action verification.

Lesson: suspicious values must be quarantined or independently verified before they can support any performance claim. They must not be silently corrected or deleted.

## 4. Outlier detection and outlier deletion are different operations

A large historical move can be a genuine market shock. Therefore the data pipeline should:

- detect
- classify
- preserve evidence
- request verification

rather than automatically remove observations.

The SPY issue was refined from a simple OHLC error assumption into an `INTRAPERIOD_RANGE_ANOMALY` review condition. This prevents the QA system from confusing unusual market behavior with invalid OHLC structure.

## 5. Deterministic calculation tests caught a genuine specification error

The first stress-loss test expected KRW -1.925M for a T1 P1-style scenario, but the implemented weighted shock mathematically produced KRW -1.8M. The expected value was corrected.

Lesson: even simple financial arithmetic requires executable tests; prose calculations are not sufficient evidence.

## 6. Synthetic fixtures must never be presented as investment performance

The 12-case harness and stress matrix are deterministic engineering fixtures. They validate code paths and risk calculations but do not establish a historical investment edge.

This distinction must remain explicit in documentation, CI output, and future reports.

## 7. Promotion gates must remain hard constraints

Current promotion policy:

`M0 -> M1 -> M2 -> M3`

A blocked upstream gate cannot be bypassed because a downstream simulation looks attractive. In particular:

- M1 data-integrity failure blocks historical backtesting.
- M2 risk-engine failure blocks strategy comparison.
- CAGR cannot override evidence-quality or risk-gate failure.

## 8. CI is necessary but not sufficient

The deterministic CI run completed with 6 tests passing after correction. However, later harness changes were not independently certified by a newly retrievable Actions result in this session.

Lesson: never report "latest CI GREEN" unless the exact current commit has an attributable successful workflow run. A previously successful run is not evidence for later code.

## 9. Research should fail closed

The appropriate status when provenance, corporate-action treatment, or current-run verification is incomplete is `YELLOW / BLOCKING`, not an inferred PASS.

This keeps the research chain auditable and prevents optimistic interpretation from entering the baseline.

## 10. Next-session priority is data, not alpha

The next session must first resolve M1-B. No new strategy optimization, stock selection, or historical return ranking should be promoted until the critical-data QA contract is satisfied.

## Current gate state at session close

| Gate | Status |
|---|---|
| M0 Risk Contract | GREEN |
| M1-A Data Acquisition | GREEN for development fixture/sample |
| M1-B Data Integrity | YELLOW / BLOCKING |
| M2-A Risk Calculation | GREEN for deterministic fixtures |
| M2-B Stress Calculation | GREEN for deterministic fixtures |
| M3 Historical Backtest | BLOCKED |
