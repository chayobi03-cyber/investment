# Session Closure — 2026-08-18 — M1-B Remediation

## Session objective

Advance M1-B Data Integrity without promoting historical strategy performance.

## Completed

- Baseline provenance matrix fixed for SPY, IEF, TLT, GLD and BIL.
- Machine-checkable provenance tests added.
- Strict `gate_pass()` behavior established so unresolved `ERROR` or `REVIEW` findings fail promotion closed.
- Real historical ingest workflow added for CI execution with primary and secondary source retrieval.
- Corporate-action event capture and cross-source reconciliation added to machine evidence generation.
- M1-B evidence artifact generation added to CI.
- Deterministic regression and M1-B evidence execution separated into distinct workflow jobs to improve diagnosis without weakening promotion gates.
- Lessons learned and next-session handoff updated.

## Observed CI result

Latest retrievable CI evidence during the session was workflow run `32093348326`.

The run failed before real-data ingestion because deterministic pytest failed:

- provenance contract string mismatch
- capital matrix harness failure
- stress matrix harness failure

As a result, no M1-B real-data evidence artifact from that run exists. The ingest/evidence path was separated from the deterministic job so the next run can independently exercise it.

## What was done well

- Maintained fail-closed promotion behavior.
- Kept synthetic fixtures separate from historical evidence.
- Converted provenance and adjustment assumptions into executable checks.
- Diagnosed CI failures from the exact current PR head instead of relying on older successful runs.
- Separated unrelated regression failures from the historical-data evidence path.

## What did not work well

- The real historical ingest could not be executed inside the assistant runtime because direct external financial API access is unavailable there.
- A contract naming mismatch reached CI.
- Existing 12-case and stress harness regressions were discovered only after the broader CI update.
- PIT verification cannot be inferred from a price-history API alone.

## Low-risk / high-ROI workflow improvements

1. Run focused provenance tests and the two deterministic harness scripts before adding further CI layers.
2. Keep historical-data acquisition/evidence as a separate job with its own artifact and gate result.
3. Capture exact commit SHA, run ID, job ID and artifact availability in the session evidence.
4. Evaluate financial-data sources by evidence quality, PIT capability, licensing risk and operational cost before adding more vendors.
5. Prefer one authoritative/event source plus one independent reconciliation source over a large vendor set.

## Final gate state

| Gate | Status |
|---|---|
| M0 Risk Contract | GREEN |
| M1-A Data Acquisition | GREEN for development fixture/sample |
| M1-B Data Integrity | YELLOW / BLOCKING |
| M2-A Risk Calculation | GREEN for deterministic fixtures |
| M2-B Stress Calculation | GREEN for deterministic fixtures |
| M3 Historical Backtest | BLOCKED |

## Closure principle

No historical backtest, allocation optimization, stock selection, OOS experiment, or Monte Carlo promotion is authorized while M1-B remains blocked.

## Next session

Start with financial-information acquisition strategy and exact-head CI verification, then execute the actual five-series historical ingest and machine evidence path. M1-B remains fail-closed until all promotion criteria are evidenced.
