# Lesson Learned — B0 Freeze and M1 Stock Method Contracts (2026-10-16)

## Evidence observed

1. GitHub Issue #27 is still OPEN.
2. The monitored return field is calculated from the last two valid 5-minute chart bars while configuration names the material-move thresholds as 15-minute thresholds.
3. Overall freshness is based on the newest timestamp among instruments. A fresh, unrelated instrument may hide stale Korean indices or leaders.
4. Current monitor tests pin status thresholds, alert behavior, breadth behavior, handling of failed VIX quotes, state key order, and runtime-branch updates. They do not directly cover the critical return-horizon and per-instrument freshness failures in Issue #27.
5. There are separate completeness, point-in-time normalization, publication/availability and provenance gate tests. These do not by themselves prove the live monitor's quote horizons or freshness aggregation are safe.
6. The GitHub status query returned pending with zero check contexts, and the connected action lookup returned no commit-associated runs for the inspected commits. A local clone/test run could not proceed because github.com DNS resolution failed in the execution environment. Test execution is therefore UNVERIFIED, not PASS.

## What was done

- Froze the existing source comparator as EXPERIMENT_B0_ENGINE_2026-10-16 at commit 2394db0bbc21b6ab36f4840b78dc227e4a84445c.
- Recorded key implementation/config/test/workflow blob SHAs and explicitly labeled the baseline NOT M1-CLEARED.
- Defined M1 regression contracts for 5m/15m/daily horizons, per-instrument and required-group freshness, prior-session close validation, quote conflicts, session/timezone behavior, corporate actions, PIT/vintage integrity and fail-closed decision propagation.
- Registered standalone method contracts for cross-sectional momentum/relative strength, quality, value, low-risk sizing, time-series trend, breakout/volume, deployment policy, and a multifactor combination gated on standalone evidence.

## Rule assessment

No existing live rule, threshold, weight, buy state, or execution permission needs to change during this documentation task. Preserve:
- BUY_ALLOWED=false
- EXECUTION_ALLOWED=false
- PROMOTION=DISABLED
- M0–M3 fail-closed promotion gates
- LOCKED-holding and PIT requirements

A documentation-level clarification is required: use EXPERIMENT_B0_ENGINE for the frozen research comparator and BUY_TRIGGER_B0_NO_BUY for the existing permission state. This avoids identifier collision without changing runtime semantics.

## Git decision

Git persistence is warranted. These are durable research controls and acceptance contracts that should survive session boundaries, be reviewable, and anchor later implementation/CI work. The freeze manifest, method test contracts, this lesson and the updated handoff should be committed.

## Next action

Implement Issue #27 remediation in a narrowly scoped change, add the M1 regression cases to the existing collector CI path, run the prescribed tests in GitHub Actions, inspect artifacts and negative fixtures, and keep all empirical strategy backtests blocked until the data gate is demonstrably GREEN.
