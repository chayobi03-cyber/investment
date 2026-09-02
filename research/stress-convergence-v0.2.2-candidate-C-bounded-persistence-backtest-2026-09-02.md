# Stress Convergence v0.2.2 Candidate C — Bounded Persistence Backtest — 2026-09-02

## 0. Objective

Replay the **same seven benchmark windows** used for the v0.2.2 A/B comparison, changing only the Rates/Inflation branch to Candidate C (bounded persistence).

Benchmarks:

- 2000 dot-com
- 2008 GFC
- 2020 COVID
- 2022 rate shock
- 2013 taper tantrum false-positive window
- 2016 China/energy stress false-positive window
- Q4 2018 tightening selloff false-positive window

Required metrics:

`FP / FN / lead time / trigger frequency`

This remains an **event-window replay**, not a full daily-panel population backtest.

## 1. Frozen base signals

Unchanged from v0.2.1/v0.2.2 A/B:

- `R`: 10Y Treasury yield >= +40bp above trailing 12-month low.
- `I`: US CPI y/y inflation >= +0.4 percentage point above its level three months earlier.
- `L`: unemployment rate >= +0.3pp above trailing 12-month low.
- `C`: HY OAS >= +75bp above trailing six-month low.
- `V`: VIX >= 25 for >=5 trading days.
- `E`: S&P 500 >=10% below trailing 60-trading-day high.

Existing regimes remain unchanged:

- Credit/Liquidity: `C + V + (L OR E)`
- Growth/Exogenous: `L + (E OR V) + (C OR R)`

## 2. Candidate C — bounded persistence (frozen before result)

Rates/Inflation branch:

`R + I sustained for 2 consecutive weekly observations`

with a bounded alarm state:

1. Entry occurs at the first weekly observation satisfying the 2-consecutive-week persistence condition.
2. The Rates/Inflation alert remains active for **at most 8 weeks** from the entry observation.
3. After expiry, the branch is inactive until a **fresh 2-consecutive-week qualification** occurs after a **4-week cool-down**.
4. No other signal threshold is changed.

The 8-week active-age and 4-week cool-down are frozen candidate parameters, not tuned to the benchmark outcomes.

Rationale: Candidate B removed the 2022 FN but behaved as a long-duration regime-state alarm. Candidate C tests whether bounding the active state improves alarm discipline without changing the underlying 2-week sensitivity mechanism.

## 3. Direct seven-window replay

| Benchmark | Candidate B: 2-week persistence | Candidate C: bounded persistence | Change |
|---|---:|---:|---|
| 2000 dot-com | PASS | PASS | No material change; non-rates regime paths remain available. |
| 2008 GFC | PASS | PASS | No material change; credit/labor confirmation remains sufficient. |
| 2020 COVID | PASS | PASS | No material change; Credit/Liquidity path catches the shock. |
| 2022 rate shock | PASS | **FN** | The first R+I persistence qualification occurs in spring 2021 and expires long before the 2022-01-03 anchor; no fresh bounded qualification is established pre-peak. |
| 2013 taper tantrum FP window | **FP** | **FP** | Bounding alarm age does not prevent the initial false trigger inside the selected window. |
| 2016 China/energy FP window | **FP** | **FP** | Same: the false trigger occurs within the active bound. |
| Q4 2018 tightening FP window | PASS / no FP | PASS / no FP | No qualifying bounded trigger in the selected Q4 window. |

## 4. Aggregate FP / FN metrics

### Crisis detection

| Metric | Candidate B | Candidate C |
|---|---:|---:|
| TP | 4 / 4 | 3 / 4 |
| FN | 0 / 4 (0%) | **1 / 4 (25%)** |
| Pre-peak trigger frequency | 1.00 / event | **0.75 / event** |

### Selected false-positive benchmark

| Metric | Candidate B | Candidate C |
|---|---:|---:|
| FP | 2 / 3 | **2 / 3** |
| FP frequency | 66.7% | **66.7%** |

## 5. Lead-time comparison

Event anchors remain:

- 2000-03-24
- 2007-10-09
- 2020-02-19
- 2022-01-03

### 2000

Candidate C retains the pre-existing Rates/Inflation + Credit/Equity path. Event-window lead remains positive and multi-week/month scale. No C-specific timing penalty is established.

### 2008

Candidate C retains the Credit/Labor confirmation route. Lead remains approximately **55 days** to the 2007-10-09 peak, consistent with the prior benchmark.

### 2020

Candidate C retains the Credit/Liquidity route. The benchmark trigger remains approximately **8–9 days after** the 2020-02-19 S&P peak because the shock was abrupt; this is a known limitation of the event anchor rather than a C-specific degradation.

### 2022

Candidate B's first R+I persistence qualification was in **spring 2021**, yielding roughly **8 months** of nominal lead to the 2022-01-03 anchor.

Candidate C deliberately bounds this state to 8 weeks. That initial state therefore expires before the 2022 event anchor, and the replay records **no valid pre-peak C trigger**.

Consequently, C changes the 2022 lead time from approximately **+8 months** under B to **no pre-peak lead / FN**.

## 6. Falsification

Candidate C fails the central trade-off test in this seven-window benchmark.

- It **does reduce state duration**, which was the main conceptual defect of Candidate B.
- It **does not reduce event-level FP frequency** in the selected 2013/2016 windows because those false triggers occur inside the bounded activation period.
- It **reintroduces the 2022 FN** because the bounded state cannot carry a spring-2021 Rates/Inflation condition into the January-2022 event.

Therefore, bounding the lifetime of the alarm is **not sufficient** to solve the specificity problem and is actively harmful to long-lead duration-shock detection under the current parameterization.

## 7. Decision

**Candidate C: REJECT as the final v0.2.2 rule.**

Candidate comparison now stands at:

| Rule | Crisis FN | Selected FP | 2022 pre-peak lead | Structural issue |
|---|---:|---:|---:|---|
| Candidate A | 1 / 4 | 0 / 3 | none | Equity confirmation is too lagging. |
| Candidate B | 0 / 4 | 2 / 3 | ~8 months | Overly persistent / regime-state behavior. |
| Candidate C | 1 / 4 | 2 / 3 | none | Bounding state removes long lead but does not remove initial FPs. |

The falsification narrows the design space:

> **The next candidate should not merely tune persistence duration. It needs an additional discriminator that separates genuine duration-shock onset from non-crisis tightening episodes.**

Suitable next families are a frozen rate-impulse/slope filter, a non-equity stress confirmation, or a formally defined multi-stage onset→persistence→confirmation state machine.

## 8. Lesson Learned

A temporal bound is a **state-management control**, not a **specificity control**.

Candidate C demonstrates that:

1. Bounding alarm lifetime can stop an early trigger from remaining active indefinitely.
2. It cannot prevent the initial false positive if the underlying R+I condition itself is non-specific.
3. A hard lifetime bound can destroy useful lead time for slow-burn duration shocks such as the 2022 episode.

So the missing component is not simply persistence duration; it is **causal discrimination between tightening regimes and crisis-producing tightening regimes**.

## 9. Source / benchmark provenance

The frozen signal definitions, event anchors, and prior A/B outcomes are inherited from:

`research/stress-convergence-regime-aware-v0.2.1-backtest-2026-09-02.md`

and

`research/stress-convergence-v0.2.2-candidate-backtest-2026-09-02.md`

FRED documents DGS10 as a daily 10Y Treasury series and CPIAUCSL as a monthly CPI series. The benchmark remains an event-window replay rather than a population-level daily-panel estimate.

## 10. Status

- Candidate A: REJECT
- Candidate B: REJECT
- Candidate C: **REJECT**
- v0.2.2: **NOT FINAL**
- Next candidate requirement: **add an independent discriminator, not another persistence-duration-only tweak**
