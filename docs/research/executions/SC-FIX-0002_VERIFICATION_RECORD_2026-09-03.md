# SC-FIX-0002 Verification Record — 2026-09-03

## Identity

- Verification ID: `SC-FIX-0002-VERIFY-20260903`
- Scope: scope-corrected + provenance-aware temporal revalidation
- Parent research commit: `f9fe7e8661fd704eee01ae45ad811454e09ae6d2`
- Revalidation artifact SHA256: `1f477b8f95064a0a9fbe42b7c60f5db6d01c67509808f80b8e67f196c48ae5f8`

## Frozen temporal attribution rule

A Crisis Confirmation is attributable to an Early Warning only when it occurs **after** the Early Warning and within the pre-declared time window. The earliest qualifying confirmation is used and one warning receives at most one attribution. No retrospective relabeling is permitted.

Fixed windows: **1 / 7 / 30 / 90 / 365 days**. Primary operating window: **90 days**.

## Revalidation result

The available daily-panel evidence was re-evaluated at warning-onset level across the four crisis benchmark cases:

| Case | Early Warning | First later Crisis Confirmation | Gap | 90-day attribution |
|---|---:|---:|---:|---|
| 2000 dot-com | 1999-04-09 | 2001-04-12 | 734d | No |
| 2008 GFC | 2006-06-09 | 2008-02-20 | 621d | No |
| 2020 COVID | 2019-12-27 | 2020-03-17 | 81d | Yes |
| 2022 rate shock | 2021-02-12 | 2021-02-02 | -10d | Invalid / PRE_EW |

Crisis-window hit counts: **1d 0/4, 7d 0/4, 30d 0/4, 90d 1/4, 365d 1/4**.

Therefore the 90-day warning-to-confirmation miss rate (FN rate) is **75% (3/4)** on the four crisis cases.

## 335-day claim disposition

The previously reported **335-day** figure is not a valid Early-Warning-to-Crisis-Confirmation lead time. It measures the distance between the 2022 Crisis Confirmation trigger and the 2022 benchmark anchor. The actual 2022 Crisis Confirmation (`2021-02-02`) precedes the Early Warning (`2021-02-12`) by 10 days.

**Disposition: REJECTED as an early-warning confirmation lead-time claim.**

## v0.2.4 verification status

This record does not promote a new v0.2.4 candidate performance number beyond the evidence already frozen in the repository. The temporal rule is deterministic, but full promotion still requires the complete scope-corrected fixture/provenance set and an independently frozen candidate artifact.

Accordingly, **SC-FIX-0002 remains BLOCKED for promotion** until the missing upstream fixture/provenance inputs are recovered or reconstructed and frozen.

## Deterministic verification

- Time-window deterministic tests: **4 passed**.
- Rules SHA256: `8404d3932be7ba602ab6eca1fdff6ce57192f315d3b76cfe63f8ff77705f642d`
- `time_window_metrics.py` SHA256: `308e55e314e94c2eeff3763b6f8c2db7247f114cd46b7cfe3bab9bf0b554740c`
- Tests SHA256: `42ade355c28d81d57110da4b8af214940963f0110f5277c7aad862319b9baa9b`
- `REPORT.md` SHA256: `90dfbb23821d256c2a8846380d2b8d0958f41eb9fb9046ee60d4dc96dd5a0881`
- `crisis_comparison.csv` SHA256: `f1c7f37dd129be77d40ec7807e2f623841b60a1ffc96f8a5119f98c3d765ba35`
- `time_window_results.csv` SHA256: `5b34024259616bdbc898bac3d764066c0c408acd680330c418ac0d5e733851c2`
- `time_window_summary.csv` SHA256: `ae8df39e61d512d50733d3638f35f30fb87d67a453d2cf315963960a9afb064d`
- Revalidation ZIP SHA256: `1f477b8f95064a0a9fbe42b7c60f5db6d01c67509808f80b8e67f196c48ae5f8`

## Final judgment

**SC-FIX-0002: BLOCKED.**

The temporal attribution mechanism is deterministic and the available revalidation is reproducible. However, the evidence is not sufficient to promote a complete scope-corrected v0.2.4 result. The 335-day figure is explicitly rejected as a warning-to-confirmation lead time, and the 90-day primary rule produces only 1/4 valid crisis confirmations in the available crisis set.

## Lesson Learned

Warning count, warning lead time, and warning-to-confirmation attribution are different measurements. A long apparent lead time must not be called a successful crisis confirmation unless the pre-declared temporal attribution window is satisfied.

## Rule modification check

No relaxation is justified. Keep the fixed 1/7/30/90/365-day windows and one-warning/one-confirmation attribution. Add/retain the reporting invariant: **crisis-stage trigger-to-anchor timing must never be labeled as warning-to-confirmation lead time.**

## Git storage decision

Commit this record as durable research evidence. Preserve the binary revalidation artifact separately and use its SHA256 as the integrity anchor rather than embedding an unverified binary in the repository.
