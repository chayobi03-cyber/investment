# Stress Convergence v0.2.2 — Candidate B vs C vs D Direct Seven-Window Replay

Date: 2026-09-02
Status: EVENT-WINDOW BACKTEST / DETERMINISTIC REPLAY

## 0. Objective

Apply Candidate D to the exact same seven benchmark windows already used for Candidates B and C, with no changes to the frozen base thresholds, event anchors, or benchmark membership.

Required comparison:

- FP
- FN
- Lead Time
- Trigger Frequency

Seven windows:

### Crisis
- 2000 dot-com
- 2008 GFC
- 2020 COVID
- 2022 rate shock

### False-positive
- 2013 taper tantrum
- 2016 China/energy stress
- Q4 2018 tightening selloff

This remains an event-window replay rather than a full daily-panel population estimate.

## 1. Frozen rules

All candidates retain the same base signals:

- `R`: 10Y Treasury yield >= +40bp above trailing 12-month low.
- `I`: US CPI y/y >= +0.4pp above its level three months earlier.
- `L`: unemployment rate >= +0.3pp above trailing 12-month low.
- `C`: HY OAS >= +75bp above trailing six-month low.
- `V`: VIX >= 25 for >=5 trading days.
- `E`: S&P 500 >=10% below trailing 60-trading-day high.

Existing regime paths remain unchanged:

- Credit/Liquidity: `C + V + (L OR E)`
- Growth/Exogenous: `L + (E OR V) + (C OR R)`

### Candidate B

`R + I sustained for 2 consecutive weekly observations`

### Candidate C

Candidate B plus bounded state:

- maximum active age: 8 weeks
- cool-down after expiry: 4 weeks

### Candidate D

Candidate B plus an independent 2Y discriminator:

`R + I sustained for 2 consecutive weekly observations AND D2`

where:

`D2 = 2Y Treasury yield >= trailing 12-month low + 60bp`

The D2 threshold is frozen at +60bp before evaluating benchmark outcomes.

## 2. Direct seven-window result

| Benchmark | B: 2W persistence | C: bounded persistence | D: persistence + D2 | D interpretation |
|---|---:|---:|---:|---|
| 2000 dot-com | PASS | PASS | PASS | Existing non-rate confirmation path preserves detection. |
| 2008 GFC | PASS | PASS | PASS | Credit/labor route preserves the established ~55d lead. |
| 2020 COVID | PASS | PASS | PASS | Credit/liquidity route dominates; D2 is not required. |
| 2022 rate shock | PASS | FN | PASS, but late | D2 confirms only after the late-2021 rate repricing; pre-peak lead collapses to about 3 days. |
| 2013 taper tantrum | FP | FP | **NO FP** | 2Y rise remains below the frozen +60bp-from-12m-low D2 threshold during the selected FP window. |
| 2016 China/energy | FP | FP | **NO FP** | 2Y remains below the frozen D2 threshold during the selected FP window. |
| Q4 2018 tightening selloff | PASS / no FP | PASS / no FP | PASS / no FP | No change in the selected window. |

## 3. Aggregate metrics

### Crisis detection

| Metric | B | C | D |
|---|---:|---:|---:|
| TP | 4 / 4 | 3 / 4 | **4 / 4** |
| FN | 0 / 4 | 1 / 4 (25%) | **0 / 4 (0%)** |
| Pre-peak trigger frequency | 1.00 / event | 0.75 / event | **1.00 / event** |

### Selected false-positive benchmark

| Metric | B | C | D |
|---|---:|---:|---:|
| FP | 2 / 3 | 2 / 3 | **0 / 3** |
| FP frequency | 66.7% | 66.7% | **0%** |

### Selected-window trigger count

Counting only the seven benchmark windows above:

| Rule | Crisis triggers | FP triggers | Total qualifying windows |
|---|---:|---:|---:|
| B | 4 | 2 | 6 / 7 |
| C | 3 | 2 | 5 / 7 |
| D | **4** | **0** | **4 / 7** |

This total-window count is descriptive only; it should not be interpreted as a population-level alert rate.

## 4. Lead-time comparison

Primary event anchors are unchanged:

- 2000-03-24
- 2007-10-09
- 2020-02-19
- 2022-01-03

### 2000 dot-com

B, C, and D retain the pre-existing Rates/Inflation + Credit/Equity route. The benchmark evidence only specifies a positive, multi-week/month-scale lead, so no artificial point estimate is introduced here.

### 2008 GFC

All three retain the credit/labor confirmation route. Lead remains approximately **55 days** to the 2007-10-09 S&P peak.

### 2020 COVID

All three retain the Credit/Liquidity route. The benchmark trigger remains approximately **8–9 days after** the 2020-02-19 S&P peak because the shock was abrupt.

### 2022 rate shock

Candidate B qualifies the R+I persistence condition far earlier, with the established benchmark estimate of approximately **8 months** nominal lead from the spring-2021 first qualification to the 2022-01-03 anchor.

Candidate C expires that early state after 8 weeks and therefore records **FN / no pre-peak lead**.

Candidate D requires D2 in addition to B. The FRED 2Y series shows the trailing 12-month low near 0.09% during early 2021, making the frozen D2 threshold roughly 0.69%. DGS2 first exceeds this level on 2021-12-07 (0.70%), with further observations above/bordering that threshold later in December. The 10Y series is also back above the relevant +40bp threshold late in December. Under the weekly two-observation persistence convention, the first clean joint D qualification falls at the end of December, yielding approximately **3 calendar days of pre-peak lead** to 2022-01-03. citeturn441381view0turn441381view1turn386037view0turn386037view2

Therefore D preserves the 2022 detection but gives up most of B's lead time.

## 5. Why D removes the 2013 FP

The selected 2013 taper window occurs while the 2Y yield rises, but the absolute level is still far below the D2 threshold implied by the preceding 12-month low.

FRED shows 2Y yields around 0.2–0.4% through the relevant 2012–2013 period, including roughly 0.40% on 2013-07-05 and about 0.42% in late August. With an earlier 12-month low around 0.22%, the +60bp D2 threshold is approximately 0.82%, so D2 does not confirm the B-style R+I state. citeturn612430view1turn780620view0

Result: **B FP -> D no FP**.

## 6. Why D removes the 2016 FP

For the selected early-2016 China/energy stress period, DGS2 remains below the +60bp discriminator relative to its trailing 12-month low. Representative observations are approximately 0.76% on 2016-01-29 and 0.66–0.74% in early/mid-February. The rate has not yet reached the level required by the frozen D2 rule, so the B-style R+I persistence alarm is blocked. citeturn122638view1turn612430view2

Result: **B FP -> D no FP**.

## 7. Falsification

### Candidate B

Strength:

- FN = 0/4
- 2022 lead ≈ 8 months

Failure:

- FP = 2/3
- behaves like a long-duration regime-state alarm

### Candidate C

Strength:

- reduces state duration

Failure:

- FP remains 2/3
- 2022 FN returns

Conclusion: duration bounding is not a specificity control.

### Candidate D

Strength:

- FN = 0/4
- FP improves from 2/3 to 0/3
- 2022 is still detected before the anchor

Failure / warning:

- 2022 lead falls from ≈8 months under B to only ≈3 days under D
- the independent discriminator therefore solves the benchmark FP problem at a large lead-time cost

The key falsification result is that **D is not simply a better B; it moves the model from an early regime detector toward a late confirmation detector for the 2022-style shock.**

## 8. Decision

### Benchmark decision

**Candidate D passes the seven-window discrimination test.**

It is the first candidate in this sequence that simultaneously achieves:

- FN = 0/4
- FP = 0/3
- positive pre-peak detection for 2022

However, D should **not yet be declared the final production rule** because its 2022 lead time is only about three days, which is materially worse than Candidate B.

### Current ranking

| Rank | Rule | FN | FP | 2022 pre-peak lead | Decision |
|---|---|---:|---:|---:|---|
| 1 | **D** | **0/4** | **0/3** | ~3 days | **BEST CURRENT CANDIDATE; more validation required** |
| 2 | B | 0/4 | 2/3 | ~8 months | REJECT as final — too permissive |
| 3 | C | 1/4 | 2/3 | none | REJECT |

The practical design problem is now sharply defined:

> D2 is an effective specificity discriminator, but +60bp is too stringent/timing-sensitive if the objective is to preserve a materially useful early warning for slow-burn duration shocks.

Therefore the next experiment should test **D2 as a distinct axis**, not revert to persistence-duration tuning. The threshold must be frozen before the next benchmark, and any new threshold must be justified ex ante rather than selected from the result.

## 9. Lesson Learned

The progression B -> C -> D isolates three different failure modes:

1. **B:** persistence restores sensitivity but confuses tightening regimes with crisis-producing tightening.
2. **C:** bounding persistence controls alarm duration but does not improve initial signal specificity.
3. **D:** an independent short-rate discriminator can materially improve specificity, but the discriminator may arrive too late if its threshold is too demanding.

The architecture should therefore retain three distinct concepts:

- **Onset:** R + I
- **Persistence:** 2 weekly observations
- **Independent confirmation:** 2Y repricing axis

The next optimization target is not persistence duration. It is the **timing/sensitivity of the independent discriminator**.

## 10. Data provenance and reproducibility note

FRED documents DGS2 and DGS10 as daily Treasury constant-maturity series from the Board of Governors of the Federal Reserve System. The DGS2 table contains the historical observations used for the D2 checks above. citeturn134070search1turn134070search0

The repository's B/C benchmark documents define the same seven windows, signal thresholds, and event anchors used here. The prior C report explicitly records B vs C outcomes and rejects C. fileciteturn5file0L2-L3

This document is an event-window deterministic replay. It is not a claim of full-series daily FP rate, and it does not justify production deployment without a broader out-of-sample panel.

## 11. Final status

- Candidate B: **REJECT**
- Candidate C: **REJECT**
- Candidate D: **PASS BENCHMARK / NOT FINAL PRODUCTION RULE**
- v0.2.2: **NOT FINAL**
- Next test: **independent-discriminator sensitivity test with ex-ante frozen threshold + expanded non-crisis tightening set**
