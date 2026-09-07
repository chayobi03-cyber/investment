# JPY Overlay Seven-Window Replay — v0.1 Result

**Date:** 2026-09-08
**Status:** REPLAY RESULT — AND-GATED OVERLAY DESIGN REJECTED, NOT PROMOTED
**Origin:** P1 open-work item from `docs/governance/CLAUDE_HANDOVER_2026-09-08.md`
and the "Required backtest/replay" section of
`docs/research/market/2026-09-03-jpy-stress-confirmation-framework.md`.
**Script:** `research/scripts/run_jpy_overlay_replay.py`
**CI workflow:** `.github/workflows/jpy-overlay-replay.yml`
**Confirmed run (this branch):**
[`34170419375`](https://github.com/chayobi03-cyber/investment/actions/runs/34170419375)
(commit `ed49f25`), reproducing exactly the original run
[`34005452731`](https://github.com/chayobi03-cyber/investment/actions/runs/34005452731)
(2026-09-06) from open PR
[`#5`](https://github.com/chayobi03-cyber/investment/pull/5).

> Research replay only, not a live trading or crisis signal.

## 0. Provenance note — this work already existed, unmerged

This exact experiment was already implemented and had a successful CI run on
2026-09-06, on branch `research/jpy-overlay-replay-2026-09-06`, as open pull
request **#5** ("research: replay JPY FX overlay on identical B/C/D
benchmark"). That PR was never merged and the result was never written up as
a governance record, so the 2026-09-08 handover still listed "JPY overlay
replay" as open P1 work. This document recovers the script onto this branch
unmodified and re-confirms the result independently (job
`101889510989` reproduces run `34005452731`'s numbers exactly). **PR #5
itself was not touched, merged, or closed by this session** — it remains
open with the original commits; a human should decide whether to close it
now that the result is captured here, or keep it for its own diff history.

## 1. Naming collision warning — read before comparing to other 2026-09-08 replays

The candidate labels **B / C / D** in this document are the pre-existing
**v0.2.2 Stress Convergence candidate definitions** from
`research/stress-convergence-v0.2.2-B-vs-C-vs-D-backtest-2026-09-02.md`:

- **Candidate B** — the frozen `R & I` (rates + inflation) two-consecutive-week
  Early Warning definition also used in `run_v0.2.3_daily_panel.py`.
- **Candidate C** — the "bounded persistence" transform of B
  (`research/stress-convergence-v0.2.2-candidate-C-bounded-persistence-backtest-2026-09-02.md`):
  once B fires, hold a state True for 8 weeks, then require a 12-week gap
  before it can re-arm.
- **Candidate D** — B combined with an independent 2-year-rate-shock
  discriminator (`DGS2` up ≥60bp from its trailing 1-year low)
  (`research/stress-convergence-v0.2.2-candidate-D-independent-discriminator-2026-09-02.md`).

**These are unrelated to the "A/B/C/D" labels used in this same session's**
`research/fx-accumulation-v0.1-A-vs-B-vs-C-vs-D-replay-2026-09-08.md`,
which are four different FX-accumulation strategies (fixed periodic,
asset-price trigger, FX trigger, combined). Do not conflate the two — they
share letters by coincidence, not by design.

## 2. Hypothesis

From `docs/research/market/2026-09-03-jpy-stress-confirmation-framework.md`:
JPY/KRW crossing a fixed observation level (850/875/900/925/950 per 100 KRW),
confirmed by a joint FX condition (JPY/KRW rising while USD/JPY falls over
the same short window), should function as a **secondary confirmation
discriminator** that improves an existing early-warning candidate's false
positive / false negative / lead-time profile — not as a standalone signal.

The framework document's explicit falsification conditions:

1. JPY thresholds materially increase false positives without a
   compensating reduction in false negatives.
2. JPY adds no incremental information after existing stress dimensions are
   included.
3. JPY signals are systematically driven by BOJ-specific repricing but are
   repeatedly misclassified as global crisis stress.
4. Threshold performance disappears when the observation window changes
   from one fixed horizon to another.

## 3. Data

- **Source:** Yahoo Finance (`JPYKRW=X`, `JPY=X` i.e. USD/JPY, `^GSPC`,
  `^VIX`), FRED (`DGS10`, `DGS2`, `CPIAUCSL`, `UNRATE`), and the same HY OAS
  GitHub archive mirror (`TGRADEA/gradea-fred-archive`) used by
  `run_v0.2.3_daily_panel.py`. Fetched inside GitHub Actions CI for the same
  reason as the FX-accumulation replay: this interactive session's network
  policy blocks direct egress to Yahoo Finance and FRED.
- **Window:** `1993-01-01` to `2022-01-10`, daily, forward-filled.
- **Benchmark (7 of the 11 v0.2.3 windows):** 4 crisis windows —
  2000 dot-com, 2008 GFC, 2020 COVID, 2022 rate shock — and 3 false-positive
  control windows — 2013 taper, 2016 China/energy, 2018 Q4 selloff. Start,
  end, and crisis-anchor dates are copied verbatim from
  `research/scripts/run_v0.2.3_daily_panel.py`'s `WINDOWS` list.
- **JPY overlay condition:** `JPY100KRW ≥ threshold AND 5-observation
  JPY/KRW rise AND 5-observation USD/JPY decline`, tested at each of
  850/875/900/925/950.

**Important caveat on benchmark vintage:** these window/anchor dates are the
**v0.2.3-era raw crash-onset anchors** (e.g. 2000 dot-com anchored at
`2000-03-24`, GFC at `2007-10-09`). They are **not** the later, frozen
v0.2.4 TTC registry from `research/stress-convergence/runs/SC-RUN-0007/`
(Early-Warning-onset → Crisis-Confirmation-onset within 90 days, per
`R-SC-TTC-001`/`R-SC-TTC-002`). This replay is internally self-consistent
with `run_v0.2.3_daily_panel.py`'s own convention, but it is a different
benchmark vintage than the officially frozen v0.2.4 one. A future revision
should re-run this same overlay test against the frozen v0.2.4 EW/CC onset
dates before treating the result as fully aligned with current Stress
Convergence governance.

## 4. Results

### 4.1 Base candidates (no JPY overlay)

| Candidate | TP | FN | FN rate | FP | FP rate | Mean lead (days) | Median lead (days) | Trigger frequency (of 4 crisis windows) | Total trigger count |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| B | 4 | 0 | 0.00 | 2 | 0.667 | 304.0 | 337.5 | 1.00 | 81 |
| C (bounded persistence) | 4 | 0 | 0.00 | 2 | 0.667 | 304.0 | 337.5 | 1.00 | 95 |
| D (independent discriminator) | 3 | 1 | 0.25 | 1 | 0.333 | 282.3 | 350.0 | 0.75 | 34 |

### 4.2 With JPY overlay applied (identical at all 5 thresholds — see section 5.3)

| Candidate | Threshold | TP | FN | FN rate | FP | FP rate | Mean lead (days) | Trigger count |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| B | 850–950 (all 5) | 1 | 3 | 0.75 | 1 | 0.333 | 31.0 | 2 |
| C | 850–950 (all 5) | 2 | 2 | 0.50 | 1 | 0.333 | 39.0 | 3 |
| D | 850–950 (all 5) | 0 | 4 | 1.00 | 0 | 0.000 | n/a (no triggers) | 0 |

Both runs (original PR #5 run `34005452731` and this branch's confirmation
run `34170419375`) produced numerically identical tables.

## 5. Falsification

### 5.1 Against the framework's own stated conditions

- **Condition 1** (FP rises without FN falling): not exactly what happened —
  FP fell (B/C: 0.667 → 0.333; D: 0.333 → 0.000). Taken alone this looks
  like the overlay is "working."
- **Condition 2** (no incremental information): not quite this either — the
  overlay clearly changes the outcome, just not favorably overall.
- **Condition 3** (BOJ-specific repricing misread as global stress): not
  directly testable from this summary table alone; would need the
  window-level `window_results.csv` to check which specific dates drove the
  2 remaining false positives.
- **Condition 4** (threshold-sensitivity disappears across horizons): the
  closest match — see 5.3.

### 5.2 A failure mode the framework document did not enumerate

**The AND-gated overlay purchases its false-positive reduction by destroying
most of the true-positive and lead-time value of the base candidates.**

- Candidate D collapses from **TP=3/FN=1** (a working, if imperfect,
  detector) to **TP=0/FN=4** — total loss of all crisis detection, and its
  false positive also drops to zero only because the combined AND condition
  essentially never fires at all (trigger count 0 of the historical sample).
  A detector that never fires trivially has zero false positives; that is
  not evidence of a good detector.
- Candidates B and C keep some detection ability (TP=1 and TP=2 out of 4)
  but at the cost of losing 75% and 50% of prior detections respectively,
  and — most importantly — **mean lead time collapses from ~304 and ~282
  days to ~31 and ~39 days**. An early-warning system whose only surviving
  hits arrive roughly a month before the crisis anchor instead of roughly
  ten months before has lost most of the "early" in early warning.

This is not literally framework condition 1 (FP did not rise), but it is the
same underlying failure the framework's Level 1–4 cascade language already
guards against: the framework describes JPY as an **additive confirmation
layer** ("only here can JPY contribute to a system-level crisis
classification" — section on Level 4), not as a **mandatory AND-gate** that
can zero out an otherwise-working base detector. This replay is best read as
falsifying the specific **AND-gate implementation**, not the broader
hypothesis that JPY/USD-JPY carries useful confirmation information.

**Recommended v2 design:** test JPY as an **OR/confidence-boost** signal
(e.g., raise confidence or shorten a required persistence window when JPY
confirms, rather than requiring JPY confirmation for the signal to fire at
all) so the base candidate's sensitivity and lead time are preserved and JPY
only sharpens or accelerates confirmation, consistent with the framework's
own cascade language.

### 5.3 Caveats

- **Identical results across all 5 thresholds (850–950) were not further
  investigated.** This could mean the actual triggering weeks in this
  7-window sample had JPY/KRW far outside the 850–950 band whenever the
  momentum condition was satisfied (plausible during acute flight-to-yen
  episodes), or it could indicate the threshold comparison is not
  discriminating within this specific historical sample for another reason.
  This is flagged as an **open question**, not assumed to be either a
  confirmed real pattern or a bug — resolving it requires inspecting
  `research/results/jpy_overlay_replay/window_results.csv` (produced by the
  CI run but, like the FX-accumulation artifact, not retrievable into this
  session — see the same Azure Blob Storage egress-block explained in
  `research/fx-accumulation-v0.1-A-vs-B-vs-C-vs-D-replay-2026-09-08.md`
  section 6).
- **Benchmark vintage mismatch** with the frozen v0.2.4 TTC registry (section 3).
- Only 4 crisis + 3 false-positive windows (7 of the original 11); the other
  4 windows (1994, 2004-05, 2017, 2021) were not included in this replay.
- No independent verification yet of whether the 2 remaining false
  positives are BOJ-specific repricing episodes misclassified as global
  stress (framework condition 3) — would require per-window inspection.

## 6. Action

- **Do not promote the AND-gated JPY overlay (850–950, 5-observation
  momentum) to a rule.** This reinforces, rather than changes, the existing
  2026-09-08 lesson-learned stance that "USD/JPY 155 하회 신호는 후보 경보이며
  하드 매매 규칙이 아니다."
- Do not use this replay to conclude JPY/USD-JPY carries no useful
  information — the failure is attributable to the specific AND-gate
  combination rule, not necessarily to the underlying JPY signal.
- Before any further JPY overlay validation, re-run against the frozen
  v0.2.4 EW/CC onset registry (not the v0.2.3 raw anchors) and test an
  OR/confidence-boost combination design instead of an AND-gate.

## 7. Lesson Learned

A secondary confirmation signal that is combined with a base detector via a
**mandatory AND-gate** can look successful on a false-positive-only view
while quietly destroying most of the base detector's true-positive coverage
and lead time. Any future "combine signal X with existing detector Y"
proposal in this project should report the *combined* TP/FN/lead-time
profile against the *base* detector's own profile side by side (as this
document does), not just the combined signal's own summary in isolation —
otherwise an FP improvement can mask a much larger sensitivity loss.

Separately: valuable, CI-validated research work can sit unmerged and
undocumented in an open pull request indefinitely if a session that
produces it does not also write the governance record. The Auto Commit
Policy's "report the commit SHA and affected paths" step should be treated
as incomplete until the corresponding governance/lessons-learned document
exists, not just the code.

## 8. Rule Change

**YES, narrow** — record in
`docs/governance/LESSONS_LEARNED_2026-09-08_MARKET_SESSION.md`'s existing
JPY section (or as an amendment to
`docs/research/market/2026-09-03-jpy-stress-confirmation-framework.md`) that:

1. The AND-gated JPY overlay design (this document) was replayed and
   rejected due to the TP/lead-time collapse in section 5.2.
2. Future JPY overlay validation should use an OR/confidence-boost
   combination rule and the frozen v0.2.4 EW/CC registry.

No change to the JPY observation levels themselves (850/875/900/925/950),
the 90-day TTC primary window, or the Portfolio Allocation Rule is justified
by this replay.

## 9. Git Commit

**YES** — CI-executed, reproducible replay result with a documented
methodology, both result tables, and a falsification section, per the Auto
Commit Policy v0.1. Committed alongside the recovered
`research/scripts/run_jpy_overlay_replay.py` and
`.github/workflows/jpy-overlay-replay.yml`.
