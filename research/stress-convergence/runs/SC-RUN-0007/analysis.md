# Stress Convergence v0.2.4 — Time-Window / TTC Validation

Date: 2026-09-03
Status: DERIVED FROM FROZEN v0.2.3 OFFICIAL RECOVERED FIXTURE
Run: `SC-RUN-0007`

## A. Data and provenance gate

The v0.2.3 daily panel was recovered from successful GitHub Actions run `33640923172`. The uploaded artifact digest is `sha256:94d74c114e3197b3f01c2cadb9378fc987a1a95e08977ce563404e8aed9c529d`; the frozen daily-panel SHA-256 is `d889cc428077c18dc0fe470b267a518a7de33e7a74b89adbfdf34b4c559e9919`.

The historical raw FRED/Yahoo/HY source snapshots are not preserved, so this is an official recovered baseline, not a fresh upstream-data reconstruction.

## B. Frozen TTC rule

`TTC = Crisis Confirmation onset - Early Warning onset`.

Only a confirmation occurring after Early Warning can establish the link. The primary confirmation rule is `0 <= TTC <= 90 days`. 91-365 days is long-term connection only. `TTC > 365` is unrelated. A negative TTC is `PRE_EW` and cannot confirm the preceding Early Warning.

## C. 11-case results

| Case | EW | First CC after EW | TTC | Classification | 90D | 365D | Anchor relation |
|---|---|---|---:|---|---|---|---|
| 1994 tightening | 1994-08-12 | 2001-04-12 | 2435 | >365 unrelated | No | No | CC coverage unavailable in original 1994 window |
| 2000 dot-com | 1999-04-09 | 2001-04-12 | 734 | >365 unrelated | No | No | CC is 384d after anchor |
| 2004-05 tightening | 2004-05-14 | 2008-02-20 | 1377 | >365 unrelated | No | No | non-crisis window |
| 2008 GFC | 2006-06-09 | 2008-02-20 | 621 | >365 unrelated | No | No | CC is 134d after anchor |
| 2013 taper | 2013-07-12 | 2020-03-17 | 2440 | >365 unrelated | No | No | non-crisis window |
| 2016 China/energy | 2015-12-11 | 2020-03-17 | 1558 | >365 unrelated | No | No | non-crisis window |
| 2017 reflation/Fed | 2016-11-04 | 2020-03-17 | 1229 | >365 unrelated | No | No | non-crisis window |
| Q4 2018 selloff | none | none | — | no confirmation | No | No | non-crisis window |
| 2020 COVID | 2019-12-27 | 2020-03-17 | 81 | 31-90 valid-medium | Yes | Yes | CC is 27d after anchor |
| 2021 reflation/taper | 2021-02-12 | none after EW | — | no confirmation | No | No | v0.2.3 CC at 2021-02-02 is before EW |
| 2022 rate shock | 2021-02-12 | none after EW | — | no confirmation | No | No | v0.2.3 CC at 2021-02-02 is before EW |

## D. Metrics

For the 4 crisis windows: 1/4 (25%) has a Crisis Confirmation within 90 days of Early Warning; the same 1/4 remains connected within 365 days. 1/4 (25%) therefore falls in the 31-90 day band, while 2/4 (50%) have no post-EW confirmation within the fixture horizon and 2 historical links exceed 365 days. For the 7 non-crisis windows, the v0.2.3 Crisis Confirmation stage had 1 false-alarm window (2021); the v0.2.4 linked-to-EW 90-day rule has 0 false-alarm windows.

The v0.2.3 Crisis Confirmation rate was 1/6 evaluable non-crisis windows = 16.7%. Under the frozen TTC linkage rule, primary 90-day FP is 0/6 = 0%.

The 90-day rule changes the crisis-link interpretation from the v0.2.3 raw trigger count to one linked confirmation (2020), while rejecting long-distance links to 2000/2008 and the pre-EW 2022 trigger.

## E. 335-day verification

The previously reported `335d early` value for the 2022 rate-shock case is **not TTC**. It is the distance from the Crisis Confirmation date `2021-02-02` to the benchmark anchor `2022-01-03`.

The Early Warning date is `2021-02-12`, which is 10 days after that Crisis Confirmation. Therefore the true TTC for the available 2022 Crisis Confirmation is `-10 days` relative to Early Warning, classified as `PRE_EW`, not a 335-day confirmation lead. Under v0.2.4 it is rejected as a valid confirmation.

## F. Falsification

Q1: Is 90 days too short? The benchmark contains one valid 90-day link at 81 days (2020). The sample is too small to prove optimality, but there is no observed crisis recovery between 91-365 days that would argue for a longer primary window.

Q2: Is 90 days too long? No observed crisis link in the 91-365 or >365 bands becomes valid at 365; the 2000 and 2008 post-EW confirmations occur at 734 and 621 days respectively and remain excluded. On this benchmark, extending to 365 adds no crisis hits.

Q3: Are 1/7/30/90 day windows structurally different? Yes. All four crisis windows have 0/4 confirmation at 1, 7, and 30 days; 90 days identifies exactly one case.

Q4: Is the 335-day case a valid crisis confirmation? No. The 335 days was anchor-to-CC timing, not EW-to-CC TTC; the CC date precedes EW by 10 days.

Q5: Is there enough evidence to declare 90 days universally optimal? No. The 4-crisis benchmark is too small for that claim. The evidence is sufficient only to adopt 90 days as the current **pre-fixed primary rule** and to reject >365-day event linkage and pre-EW confirmations.

## G. Rule verdict

**PASS with qualification.** v0.2.4 solves the immediate event-linking problem without post-hoc window selection: long-gap links are no longer called successful confirmations, and the 335-day label is corrected.

The 90-day window is adopted provisionally as the primary confirmation window, not as a statistically proven optimum.

Additional rule now frozen: Crisis Confirmation must occur **after** Early Warning. This directional constraint is necessary and is independent of the numeric 90-day threshold.

## H. Lesson Learned

The largest improvement came from separating two concepts that had been conflated: (1) how far a Crisis Confirmation is from the Early Warning, and (2) how far that confirmation is from a historical crisis anchor. A large anchor lead is not evidence that the warning predicted a crisis if confirmation did not follow the warning.

## I. Rule modification

Add `R-SC-TTC-001`: only `CC_date > EW_date` can establish TTC. Add `R-SC-TTC-002`: `0-90d` is primary confirmation, `91-365d` is tracking only, `>365d` is unrelated. Keep anchor-relative timing as a separate field from TTC.

## J. Git status

The contract, manifests, deterministic tests, TTC runner, and v0.2.4 results are stored on branch `research/stress-convergence-reproducibility-v1`. The frozen daily panel itself remains in the official CI artifact rather than Git because the original upstream raw sources are not fully preserved; permanent fixture archival remains an infrastructure TODO.
