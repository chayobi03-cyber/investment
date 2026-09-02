# Stress Convergence v0.2.2 Candidate Backtest — 2026-09-02

## 0. Objective

Directly compare the two v0.2.2 rule candidates against the **same benchmark used for v0.2.1**:

- 2000 dot-com
- 2008 GFC
- 2020 COVID
- 2022 rate shock
- false-positive windows: 2013 taper tantrum, 2016 China/energy stress, Q4 2018 tightening selloff

Required metrics: `FP / FN / lead time / trigger frequency`.

This is an **event-window benchmark replay**, not a claim of full daily-panel population statistics. The repository's v0.2.1 result explicitly labels its own run as event-window numerical backtest / not full-series replication.

## 1. Frozen base signal definitions

Same definitions as v0.2.1:

- `R`: 10Y Treasury yield >= +40bp above trailing 12-month low.
- `I`: US CPI y/y inflation >= +0.4 percentage point above its level three months earlier.
- `L`: unemployment rate >= +0.3pp above trailing 12-month low.
- `C`: HY OAS >= +75bp above trailing six-month low.
- `V`: VIX >= 25 for >=5 trading days.
- `E`: S&P 500 >=10% below trailing 60-trading-day high.

Existing regime paths remain unchanged:

- Credit/Liquidity: `C + V + (L OR E)`
- Growth/Exogenous: `L + (E OR V) + (C OR R)`

## 2. v0.2.2 candidates

### Candidate A — Equity confirmation expansion

Rates/Inflation regime:

`R + I + (L OR C OR E)`

This is the first proposed v0.2.2 candidate from the v0.2.1 falsification section. Valuation confirmation is not introduced because no frozen valuation threshold was previously specified.

### Candidate B — Rates/Inflation persistence

Rates/Inflation regime:

`R + I sustained for 2 consecutive weekly observations`

The v0.2.1 proposal specified an integer persistence rule but did not freeze N. For this comparison, **N=2 weeks is frozen as the minimum candidate**, avoiding an unfunded choice of a longer persistence window. This parameter must not be tuned after seeing the results.

All other v0.2.1 regime gates remain unchanged for both candidates.

## 3. Direct benchmark result

| Benchmark | Candidate A: R+I+(L/C/E) | Candidate B: 2-week R+I persistence | Interpretation |
|---|---:|---:|---|
| 2000 dot-com | PASS | PASS | Existing regime paths preserve detection; A adds no material advantage in this event-window test. |
| 2008 GFC | PASS | PASS | Credit/labor confirmation remains sufficient. |
| 2020 COVID | PASS | PASS | Credit/Liquidity regime catches the shock; rates persistence is not required. |
| 2022 rate shock | **FN** | **PASS** | B removes the specific 2022 pre-peak miss; A still waits for equity drawdown confirmation. |
| 2013 taper tantrum FP window | PASS / no FP | **FP** | R was elevated while inflation acceleration also qualified, so persistence fires without a crisis peak. |
| 2016 China/energy FP window | PASS / no FP | **FP** | A rate/inflation sequence is present despite the absence of a target crisis event. |
| Q4 2018 tightening FP window | PASS / no FP | PASS / no FP | Persistence does not qualify throughout the selected Q4 window. |

## 4. Aggregate metrics

### Crisis detection

| Metric | Candidate A | Candidate B |
|---|---:|---:|
| TP | 3 / 4 | **4 / 4** |
| FN | **1 / 4 (25%)** | **0 / 4 (0%)** |
| Crisis trigger frequency | 0.75 / event | **1.00 / event** |

### Selected false-positive benchmark

| Metric | Candidate A | Candidate B |
|---|---:|---:|
| FP | **0 / 3** | **2 / 3** |
| FP frequency | **0%** | **66.7%** |

## 5. Lead-time assessment

The event anchors are unchanged from v0.2.1:

- 2000-03-24
- 2007-10-09
- 2020-02-19
- 2022-01-03

For the first three episodes, both candidates retain the already-validated non-rates regime paths, so the event-window timing remains broadly consistent with the v0.2.1 benchmark (2008 approximately 55 days pre-peak; COVID trigger approximately 8–9 days after the peak, because the shock was extremely abrupt).

The differentiating case is 2022:

- Candidate A remains **post-peak**, because `E` requires a >=10% equity drawdown and therefore cannot act as a true pre-peak confirmation for the 2022-01-03 anchor.
- Candidate B can qualify substantially earlier because R and I were simultaneously active for multiple weeks before the 2022 peak. Using the frozen observation-date rule rather than an intraday release-lag adjustment, the first 2-week persistence qualification is in **spring 2021**, implying roughly **8 months of lead time** to the 2022-01-03 peak.

That long lead is not automatically a benefit: it indicates that Candidate B can remain active for an extended period before the event and therefore behaves more like a **regime-state alarm** than a tight crisis timer.

## 6. Falsification

### Candidate A

Survives the FP test but does **not** solve the structural problem identified by 2022. Equity drawdown is a confirmation variable that is intrinsically downstream of the first phase of a duration shock.

**Conclusion:** insufficient as the sole v0.2.2 change.

### Candidate B

Eliminates the 2022 FN in the benchmark, but fails the selected FP set with 2/3 false positives. The mechanism is visible in the historical inflation data: inflation acceleration can coexist with elevated long rates during non-crisis tightening episodes. FRED's historical CPI series confirms the monthly observations used to evaluate this condition, while DGS10 provides the daily rate series.

**Conclusion:** improves sensitivity at the expense of specificity and alarm duration.

## 7. Decision

**Do not promote either candidate directly to a final v0.2.2 production rule.**

The falsification result is more useful than either raw score:

1. `E` is too lagging to repair the 2022 pre-peak duration FN.
2. A bare `R + I` persistence gate is too permissive and generates material false positives.
3. The next rule should preserve the regime-aware architecture while making the Rates/Inflation branch **stateful but bounded**.

### Recommended next candidate family: bounded persistence + confirmation

Test a third formulation rather than selecting A/B unchanged:

`R + I sustained for N weeks` **AND** a bounded confirmation condition such as:

- a minimum rate impulse / slope, or
- a maximum persistence age before the alert decays, or
- a non-equity confirmation that is independent of the downstream drawdown.

The exact added threshold must be frozen before the next backtest.

## 8. Lesson Learned

The 2022 experiment shows that the missing capability is not simply “one more signal.” The model needs to distinguish:

- **shock onset** — rates/inflation acceleration,
- **shock persistence** — whether the condition remains active,
- **stress confirmation** — credit/equity/volatility deterioration.

This supports a three-stage Rates/Inflation path rather than substituting one binary gate for another.

## 9. Evidence / source note

The v0.2.1 repository benchmark defines the frozen signals, anchors, and prior 3/4 detection result. FRED documents DGS10 as a daily 10Y Treasury series and CPIAUCSL as a monthly CPI series; the historical CPI observations cover the 2013, 2016, 2018, 2021 and 2022 periods used in the persistence falsification. 

Repository precedent: `research/stress-convergence-regime-aware-v0.2.1-backtest-2026-09-02.md`.

## 10. Status

- Candidate A: **REJECT as final rule**
- Candidate B: **REJECT as final rule**
- v0.2.2 status: **NOT FINAL**
- Next step: **bounded-persistence candidate + same benchmark**
