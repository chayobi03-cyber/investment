# B0 Baseline Freeze — 2026-10-16

- Baseline ID: EXPERIMENT_B0_ENGINE_2026-10-16
- Status: FROZEN FOR COMPARISON / RESEARCH ONLY / NOT M1-CLEARED
- Frozen source commit: 2394db0bbc21b6ab36f4840b78dc227e4a84445c
- Main documentation HEAD at freeze: a628833aec93859e23168cb27f41ea43e2711dd2
- Freeze date: 2026-10-16 (KST)
- Repository: https://github.com/chayobi03-cyber/investment
- Related issue: https://github.com/chayobi03-cyber/investment/issues/27

## 1. What is frozen

The B0 comparator is the existing engine as of source commit 2394db0bbc21b6ab36f4840b78dc227e4a84445c. The subsequent main commit a628833aec93859e23168cb27f41ea43e2711dd2 added only HANDOFF_STOCK_METHOD_BENCHMARK.md; the GitHub compare endpoint reported one added documentation file and no source changes.

This is a reproducibility freeze, not a statement that the baseline is correct, profitable, or eligible for live use. The market-monitor component is explicitly quarantined from buy-timing authorization until Issue #27 is remediated and M1 regression tests pass.

### Naming collision guard

- EXPERIMENT_B0_ENGINE means the frozen existing engine used as a research comparator.
- BUY_TRIGGER_B0_NO_BUY means the existing permission state whose meaning is “No Buy.”
- These labels are not interchangeable. No experiment identifier may override the permission state.

## 2. Frozen file manifest

The following blob SHAs were inspected on the frozen source snapshot. Because the only later commit changed the handoff document, these implementation/test files are unchanged between the frozen source commit and the current documentation HEAD.

| Component | Path | Blob SHA |
|---|---|---|
| Market monitor implementation | scripts/market_monitor/poll.py | 4c0dbb048c5b9c05c211fcdbb51bc5f451496541 |
| Monitor configuration | config/market_monitor.json | 2853984c81a7c96c47dd982aca3fb51e6516bc24 |
| Monitor unit tests | tests/test_market_monitor.py | 4c989ce0c5adc3dfa2154e4fc96bb86c5b21e30c |
| Monitor workflow tests | tests/test_market_monitor_workflow.py | d72f3afed16eb966f90fe6c8e86f0e8fc59f0335 |
| Scheduled monitor workflow | .github/workflows/market-monitor.yml | ab697ec55cb22f811cfb0fa6ddfb30fc0f4f830b |
| Collector CI workflow | .github/workflows/collectors-ci.yml | f8b2d50e669093f9a8a06349547ab67f6f6617ca |
| Stock data completeness | src/investment_pipeline/completeness.py | 5187fa34106171045937a516e5444dfa712b8cd8 |
| Point-in-time factors | src/investment_pipeline/factors.py | 03d6eba2d9fa86ef72c55fbc8115595f46c168a9 |
| Decision gate | src/investment_pipeline/decision_gate.py | 24820297e9d55da2087379780edcbb5a4be7ca41 |
| Data-pipeline tests | tests/test_data_pipeline.py | bd989167a357acff50718cc70aff4e35d06a8bf5 |
| Decision-gate tests | tests/test_decision_gate.py | 431e729770050c6efd339f2ed4fcbadd7619555d |
| PIT provenance tests | tests/r01/test_pit_provenance.py | 7c0a8f1c07b675be597e6ee71925b6a0ec3ed98c |
| Provenance-gate tests | tests/r01/test_provenance_gates.py | 61f70e2886d1a5841837d11730d3aaac51587850 |

## 3. Frozen behavior and non-negotiable constraints

1. Preserve the existing M0 Risk Contract, M1 Data Integrity, M2 Portfolio Risk Engine, and M3 Asset Allocation Backtest gates.
2. BUY_ALLOWED=false.
3. EXECUTION_ALLOWED=false.
4. Promotion remains DISABLED. A green research result cannot enable live buying or execution.
5. DATA_NOT_READY and BLOCKED remain fail-closed.
6. Do not use the compact market monitor's RISK, TREND, BUY_TRIGGER, or DATA_QUALITY fields as authoritative buy timing before Issue #27 acceptance tests pass.
7. Do not change thresholds, weights, or existing Buy Trigger states in this baseline-freeze task.
8. LOCKED holdings remain in risk exposure and must not become automatic sell candidates.
9. Point-in-time availability, source provenance, corporate actions, fees, slippage, liquidity, and look-ahead prevention are mandatory for later experiments.
10. The B0 comparator is evaluated on identical valid data windows and cost assumptions as candidate methods.

## 4. M1 / Issue #27 findings at freeze

Issue #27 is OPEN. The inspected implementation still computes change_pct from the final two valid chart closes returned by a range=1d, interval=5m query. That is a last-bar return, not an explicitly validated 15-minute or prior-session close-to-close return. The 15-minute threshold configuration therefore does not guarantee a 15-minute calculation.

The inspected build_state logic calculates age using the maximum timestamp across all successful instruments. One fresh, unrelated symbol can therefore make the aggregate freshness appear recent while critical Korean indices/leaders are stale.

Existing tests cover status thresholds, state/delta/alert behavior, breadth, handling of failed VIX quotes, schema key order, and runtime-branch update behavior. The checked-in monitor tests do not yet demonstrate the critical regression cases: 5m vs 15m vs daily horizon parity, a fresh USD/JPY masking stale Korean indices, a verified prior-session close, or quote conflict that must fail closed.

Additional M1 tests exist for stock snapshot completeness, point-in-time normalization, publication/availability and provenance gating. They are useful but do not close the monitor-specific gaps above.

## 5. Verification status — do not infer a pass

- Source and relevant test/workflow files: inspected through GitHub.
- Git compare: verified that a628833 is one documentation-only commit above the frozen source commit.
- Combined status response for the frozen source commit: state=pending, total_count=0, no individual check contexts.
- Commit-associated workflow runs returned by the connected GitHub action: none for the frozen source commit or the documentation HEAD.
- Local test execution: NOT RUN. A local clone attempt failed because this execution environment could not resolve github.com.
- Therefore, test status is NOT VERIFIED; absence of reported checks is not a passing result.

CI commands prescribed by the existing collector workflow include:

    python -m pytest -q -W error::DeprecationWarning tests/test_market_monitor.py tests/test_market_monitor_workflow.py tests/test_binance_derivatives_archive.py tests/test_fred_permission_macro.py tests/test_permission_evidence_bundle.py

Also required before M1 promotion: tests/test_data_pipeline.py, tests/test_decision_gate.py, tests/r01/test_pit_provenance.py, and tests/r01/test_provenance_gates.py.

## 6. Unfreeze policy

This manifest is immutable as the B0 comparator. Fixes must be made in a separate commit and tested against the frozen commit. If an intentional change to baseline behavior is later approved, create a new baseline ID and manifest rather than silently rewriting this one. Any performance claim must name both the baseline ID and candidate run ID.

## 7. Gate decision

M1 status: BLOCKED / NOT GREEN because Issue #27's required remediation and regression evidence are not yet verified.

Backtest promotion: BLOCKED until M1 is GREEN and the source data/run manifest is complete.

Operational locks: BUY_ALLOWED=false, EXECUTION_ALLOWED=false, PROMOTION=DISABLED.
