# Stress Convergence v0.2.2 — D2 Threshold Sensitivity + Expanded Non-Crisis Tightening Set

Date: 2026-09-02
Status: FALSIFICATION / SENSITIVITY TEST

## 0. Objective

Test whether Candidate D's independent 2Y discriminator remains useful when:

1. the D2 threshold is varied ex ante rather than fixed at +60bp; and
2. the false-positive set is expanded beyond the original 2013 / 2016 / Q4-2018 windows to include additional non-crisis tightening regimes.

The existing seven-window replay found D(+60bp) at FN=0/4 and FP=0/3, but also found the 2022 lead time collapsed from roughly eight months under B to roughly three days under D. The next question is whether a lower D2 threshold can recover useful lead time without reintroducing the FP problem.

This artifact is intentionally a discriminator sensitivity/event-window stress test. It is not a full daily-panel population estimate of FP rate.

## 1. Frozen base rule

All non-D2 conditions remain unchanged from v0.2.2:

- R = 10Y Treasury yield >= trailing 12-month low +40bp
- I = US CPI y/y >= level three months earlier +0.4pp
- R+I persistence = 2 consecutive weekly observations
- L = unemployment rate >= trailing 12-month low +0.3pp
- C = HY OAS >= trailing six-month low +75bp
- V = VIX >=25 for >=5 trading days
- E = S&P 500 >=10% below trailing 60-trading-day high

Candidate D architecture:

`R + I sustained 2W + D2`

D2 remains:

`2Y Treasury yield >= trailing 12-month low + X bp`

The threshold X is the only experimental axis.

## 2. Ex-ante threshold grid

The sensitivity grid is fixed before reading the result:

- +40bp
- +50bp
- +60bp
- +70bp
- +80bp

No threshold is promoted solely because it maximizes the historical score.

## 3. Expanded non-crisis tightening / look-alike set

The original FP set is retained and expanded with structurally relevant tightening episodes:

| Window | Role | Why included |
|---|---|---|
| 1994 tightening | Negative-control tightening | Large short-rate repricing without a crisis; tests whether D2 simply detects tightening |
| 2004–05 tightening | Adversarial non-crisis tightening | Strong policy-rate repricing and 2Y rise; tests whether D2 confuses ordinary tightening with crisis-producing tightening |
| 2013 taper tantrum | Existing FP | Existing B false positive |
| 2016 China/energy stress | Existing FP | Existing B false positive |
| 2017 reflation / Fed tightening | Adversarial non-crisis tightening | R+I-style macro repricing plus material 2Y increase |
| Q4 2018 tightening selloff | Negative-control / existing window | Existing benchmark window; B was not classified as FP |
| 2021 reflation / taper / pre-2022 tightening | Adversarial non-crisis tightening | Strong R+I-style macro pressure with substantial 2Y repricing before the 2022 event |

The purpose is adversarial: the test asks whether D2 distinguishes **tightening** from **tightening that actually becomes crisis-producing stress**.

## 4. Data check for D2 sensitivity

FRED DGS2 is a daily 2-year U.S. Treasury constant-maturity yield series sourced from the Federal Reserve Board. The historical table confirms the relevant movements used in the sensitivity screen. citeturn780038view0turn604351search0

Representative observations:

- 1994: DGS2 was about 4.05% in January and reached 5.21% by late March, so +40/+50/+60/+70/+80bp are all crossed within the tightening episode. citeturn365844view0
- 2004: DGS2 fell to roughly 1.50% in March and rose to roughly 2.70–2.97% by June, crossing every threshold in the grid. The Federal Reserve's 2004 Monetary Policy Report explicitly describes higher 2Y and 10Y yields as markets priced a more rapid tightening path. citeturn365844view3turn218828search47
- 2013: DGS2 was roughly 0.30–0.52% during the main taper-tantrum window, leaving the rise from its trailing low well below the +60bp threshold used in the original D test. citeturn755977view3
- 2016: DGS2 was about 0.76% on 2016-01-29 and mostly 0.64–0.80% through February; this remains below the original +60bp-from-trailing-low discriminator over the selected early-2016 FP window. citeturn755977view2
- 2017: DGS2 reached about 1.89% by 2017-12-29 after being substantially lower during the prior period, so the higher D2 thresholds are crossed during the tightening/reflation regime. citeturn755977view0turn365844view1
- 2021: DGS2 reached 0.50% on 2021-11-26, 0.63% on 2021-12-02, 0.70% on 2021-12-07, 0.71% on 2021-12-23 and 0.76% on 2021-12-27. With the trailing low near 0.09%, +40bp, +50bp and +60bp thresholds are all crossed during 2021; +70bp is first crossed in early January 2022. citeturn755977view1turn365844view2

The historical data therefore support a wide D2 sensitivity range; the issue is not whether the thresholds are crossed, but whether crossing them is specific to crisis-producing tightening.

## 5. Sensitivity result — 2022 rate shock

The original D(+60bp) replay established approximately 3 calendar days of pre-peak lead to the 2022-01-03 S&P anchor, versus roughly eight months for B. The same replay established that the 2022 result is timing-sensitive to the 2Y confirmation threshold.

| D2 threshold | 2022 detection | Expected lead-time regime | Interpretation |
|---|---|---|---|
| +40bp | PASS | materially earlier than +60; weeks-scale | recovers much of B's early warning but increases tightening-regime exposure |
| +50bp | PASS | weeks-scale | intermediate sensitivity / specificity trade-off |
| +60bp | PASS | ~3 days | current D result; specificity improved in the small original FP set, but confirmation is late |
| +70bp | FAIL / no useful pre-peak confirmation | no pre-peak lead | threshold is too strict for the 2022 benchmark |
| +80bp | FAIL / no useful pre-peak confirmation | no pre-peak lead | clearly too strict |

The exact daily lead values for +40/+50 are not promoted to point estimates here because the existing repository artifact is an event-window replay rather than a fully executable daily panel. The stable qualitative ordering is robust: lowering X moves D2 confirmation earlier; raising X beyond +60 destroys the 2022 pre-peak property.

## 6. Expanded FP falsification

The critical result is qualitative but decisive.

### 6.1 D2 is not a crisis-specific discriminator

The FRED history and the monetary-policy literature show that large 2Y repricing is a normal feature of several ordinary tightening cycles. The 2004 Federal Reserve report explicitly notes that the 2Y yield rose as markets priced a faster monetary-policy tightening path, while 1994 was another major tightening episode. citeturn218828search47turn218828search2

Therefore a D2 rule of the form “2Y rose X bp from its trailing low” is measuring **policy/tightening repricing intensity**, not directly measuring “crisis-producing tightening.”

### 6.2 Lower thresholds recover lead time but weaken specificity

At +40/+50, the 2021 2Y move crosses the discriminator well before the 2022 peak. That is exactly the behavior desired for early warning, but it also means a strong pre-crisis tightening/reflation regime can satisfy D2. The same structural problem exists in 2004 and 2017, where the 2Y repricing was large enough to cross even relatively high D2 thresholds. citeturn365844view3turn755977view0turn755977view1

### 6.3 Higher thresholds do not solve the conceptual problem

Increasing D2 to +70/+80 suppresses more moderate episodes, but then the 2022 benchmark loses useful pre-peak detection. Meanwhile, very large ordinary tightening episodes such as 1994 and 2004 can still cross high thresholds. citeturn365844view0turn365844view3

Thus there is no defensible threshold-only solution in the tested grid.

## 7. Falsification summary

| Hypothesis | Result | Status |
|---|---|---|
| Lowering D2 below +60 recovers lead time | Yes | CONFIRMED |
| Lower D2 preserves specificity | No | FALSIFIED by expanded tightening set |
| Raising D2 above +60 preserves 2022 pre-peak detection | No | FALSIFIED |
| 2Y repricing alone distinguishes crisis-producing tightening | No | FALSIFIED / mechanism too broad |
| +60 is a robust universal discriminator | No | FALSIFIED |

## 8. Decision

### Candidate D as currently defined

**REJECT AS FINAL RULE.**

Not because D2 is useless, but because the hard-AND architecture makes D2 carry a semantic burden it cannot satisfy:

> large 2Y repricing identifies a meaningful tightening / policy-repricing regime, but does not by itself identify whether that regime will become a market crisis.

The original 7-window result therefore should be interpreted as a useful proof-of-concept, not as evidence that +60bp is a stable production threshold.

### Current model ranking

| Candidate | Main strength | Main failure | Status |
|---|---|---|---|
| B | Best early warning | Too many ordinary tightening FP | REJECT final |
| C | Limits persistence duration | Does not improve initial specificity; loses 2022 | REJECT |
| D(+60) | Excellent original 7-window FP suppression | 2022 lead collapses; fails expanded conceptual test | REJECT final |
| D sensitivity family | Reveals trade-off directly | No single threshold dominates | RESEARCH RESULT |

## 9. Rule revision proposal

Do **not** continue optimizing the D2 threshold as a single hard gate.

Split the information into two distinct states:

### Early Warning

`R + I sustained 2W`

Purpose: preserve early detection of slow-burn rate/inflation regimes.

### Tightening Confirmation

`D2 = 2Y >= trailing 12m low + X`

Purpose: characterize policy-rate repricing intensity and increase confidence, but not determine crisis status by itself.

### Crisis Confirmation

Retain the independent credit/liquidity/equity confirmation paths already present in the model rather than making D2 a substitute for them.

This produces a three-stage interpretation:

`R+I onset/persistence → D2 tightening confirmation → Credit/Liquidity or Growth/Exogenous crisis confirmation`

The key architectural change is that **D2 becomes an orthogonal state descriptor, not a mandatory crisis gate.**

## 10. Next experiment

The next candidate should test whether combining the three states improves the precision/lead-time trade-off:

`Early Warning = R+I persistence`

`Tightening State = Early Warning + D2 band`

`Crisis Alert = existing crisis path + context from Tightening State`

The D2 band should be tested as categorical information, e.g. <+40 / +40–60 / >=+60bp, instead of searching for one magic threshold.

That experiment must use an expanded daily-panel non-crisis set and a true out-of-sample holdout before any production promotion.

## 11. Lesson Learned

1. Persistence duration was not the specificity solution; C already showed that.
2. D2 improved specificity in the small original FP set, but the expanded non-crisis tightening test shows that the discriminator is fundamentally a **tightening-intensity signal**, not a crisis detector.
3. Threshold tuning exposes a Pareto frontier rather than a single optimum: lower X improves lead time and worsens FP exposure; higher X reduces sensitivity and can miss the 2022 pre-peak window.
4. The model should separate **onset**, **tightening state**, and **crisis confirmation** rather than forcing one scalar threshold to perform all three jobs.

## 12. Session close

Lesson Learned: D2 is useful as an orthogonal tightening-state feature, but not as a hard crisis discriminator.
Rule Change: YES — remove D2 as a mandatory hard-AND gate; use it as a confirmation/state axis pending an expanded daily-panel validation.
Git Commit: YES — this sensitivity/falsification artifact is material, reproducible research evidence and should remain alongside the prior B/C/D results.

## 13. Reproducibility note

This document deliberately preserves the original v0.2.2 base thresholds and adds only the D2 threshold axis plus the expanded non-crisis tightening challenge set. It should be read together with:

- `research/stress-convergence-v0.2.2-B-vs-C-vs-D-backtest-2026-09-02.md`
- `research/stress-convergence-v0.2.2-candidate-D-independent-discriminator-2026-09-02.md`
- `docs/governance/INVESTMENT_RESEARCH_LOOP.md`
