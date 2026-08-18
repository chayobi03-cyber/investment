# Lessons Learned — 2026-08-18

## Session scope

This session continued the capital-preservation research framework with emphasis on M1-B Data Integrity. Work stayed fail-closed and did not promote historical strategy performance.

## 1. Capital preservation remains the primary optimization objective

Raw CAGR is not the primary gate. The evaluation order remains:

1. Probability of ruin / catastrophic loss
2. Maximum drawdown
3. Stress loss
4. Recovery time
5. Volatility
6. Sortino
7. Calmar
8. CAGR

A higher CAGR cannot override materially worse downside characteristics or failed evidence gates.

## 2. Capital tiers must be tested separately

The same percentage allocation can behave differently at KRW 10M, 50M, and 100M because implementation granularity, transaction costs, diversification and liquidity differ. Percentage metrics and absolute KRW loss must both be reported.

## 3. Data QA is a hard promotion gate

The session reinforced that suspicious market observations must be quarantined or independently verified before supporting any performance claim. No silent correction, deletion, winsorization or imputation is allowed.

## 4. Outlier detection and outlier deletion are different operations

A large historical move may be a real market shock. The correct workflow is detect -> classify -> preserve evidence -> verify, not detect -> delete.

The SPY anomaly was treated as an evidence problem, not automatically as a bad market event.

## 5. Adjustment rules must be machine-readable

The provenance matrix now records source identity, secondary confirmation source, corporate-action handling, PIT rule, and adjustment rules for SPY/IEF/TLT/GLD/BIL. The important improvement is that the rule is executable-testable rather than only prose.

## 6. Known historical anomalies can often be explained, but explanation is not the same as gate clearance

The BIL 2017 discontinuity was identified as a reverse-split issue. The SPY suspicious low was retained as a quarantined anomaly. These explanations reduce ambiguity but do not by themselves make the full historical dataset GREEN.

## 7. Actual-data evidence must remain separate from synthetic engineering fixtures

The 12-case and stress harnesses are useful regression fixtures, but they are not historical evidence. Real historical ingest must produce separate machine evidence with source, retrieval and reconciliation metadata.

## 8. CI evidence must attach to the exact current head

A previous successful run cannot certify later changes. The session explicitly checked the current PR head and found a retrievable CI failure. The failure became evidence for remediation rather than being ignored.

## 9. Workflow improvement: isolate data-evidence execution from deterministic regression

A useful structural improvement was to separate the M1-B real-data ingest/evidence job from the deterministic harness job. This prevents an unrelated calculation-regression failure from hiding whether historical-data evidence generation itself can execute.

This is a low-risk, high-ROI workflow improvement because it improves diagnosis without weakening the final promotion gate: all required gates still have to pass before promotion.

## 10. Automation opportunities should be small, auditable and high-value

The most valuable automations identified in this session are:

- automatic provenance-contract validation
- automatic historical ingest with retrieval timestamps
- automatic duplicate/missing/gap/OHLC checks
- automatic corporate-action event capture
- automatic cross-source reconciliation
- automatic machine evidence artifact generation
- automatic fail-closed M1-B decision
- automatic exact-head CI evidence capture

Do not add automation merely for convenience when it increases data-source ambiguity or operational complexity.

## 11. What did not work well

The real-data ingest path could not be validated inside the assistant runtime because external financial API access is unavailable there. The implementation therefore had to be pushed to GitHub Actions for execution.

The first latest-head CI also exposed three failures: one provenance-contract string mismatch and two existing deterministic harness execution failures. This means future changes should be followed immediately by focused regression checks before adding another layer of automation.

## 12. Next-session focus: financial-information acquisition

The next session should explicitly evaluate how the project will obtain financial information with the lowest operational risk and highest reproducibility value.

The evaluation should cover:

- official issuer / exchange sources
- regulator filings and corporate-action records
- stable public historical APIs
- licensed commercial datasets where justified
- source terms, rate limits and redistribution constraints
- retrieval timestamps and dataset/version identifiers
- raw-data retention and hashing
- primary/secondary reconciliation strategy
- PIT-capable sources for research-decision timestamps

The objective is not to add many data vendors. It is to select a small, defensible source stack that maximizes evidence quality and minimizes maintenance and licensing risk.

## Current gate state at session close

| Gate | Status |
|---|---|
| M0 Risk Contract | GREEN |
| M1-A Data Acquisition | GREEN for development fixture/sample |
| M1-B Data Integrity | YELLOW / BLOCKING |
| M2-A Risk Calculation | GREEN for deterministic fixtures |
| M2-B Stress Calculation | GREEN for deterministic fixtures |
| M3 Historical Backtest | BLOCKED |
