# Stress Convergence v0.2.3 — Three-Stage Daily-Panel Validation

Date: 2026-09-02
Status: DAILY-PANEL MEASUREMENT / RESEARCH ONLY
Workflow run: 33640923172
Validated head commit: 616cdd6c78f3ffe754833a51fc504a8a08332734

## 1. Purpose

Run the expanded 11-window benchmark against actual daily data and measure the three states separately:

1. Early Warning — R + I sustained for two consecutive weekly observations.
2. Tightening State — Early Warning + 2Y repricing >= +40bp from trailing 12-month low.
3. Crisis Confirmation — existing Credit/Liquidity OR Growth/Exogenous path; D2 is contextual, not a hard gate.

Measured outputs:

- False alarms in non-crisis windows (FP / 오탐)
- Missed crisis windows (FN / 미탐)
- Pre-anchor lead time (조기 탐지 시간)
- Trigger frequency (경보 발생 빈도)

## 2. Eleven benchmark windows

### Crisis windows

- 2000 dot-com — anchor 2000-03-24
- 2008 GFC — anchor 2007-10-09
- 2020 COVID — anchor 2020-02-19
- 2022 rate shock — anchor 2022-01-03

### Non-crisis / look-alike windows

- 1994 tightening
- 2004–05 tightening
- 2013 taper tantrum
- 2016 China/energy stress
- 2017 reflation / Fed tightening
- Q4 2018 tightening selloff
- 2021 reflation / taper

## 3. Daily data used

- FRED: DGS10, DGS2, CPIAUCSL, UNRATE
- Archived HY OAS: BAMLH0A0HYM2 mirror
- Yahoo Finance: S&P 500 and VIX

Lower-frequency macro observations were carried forward to daily dates. This is an event-window historical-data replay, not a real-time publication-vintage backtest.

## 4. Measured results

| Stage | Crisis missed (FN / 미탐) | Crisis windows | Non-crisis false alarms (FP / 오탐) | FP windows evaluated | FP rate | Pre-anchor lead | Windows with any trigger | Total onset episodes |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Early Warning | 0 | 4 | 6 | 7 | 85.7% | mean 304d; median 337.5d | 10/11 | 19 |
| Tightening State | 1 | 4 | 5 | 7 | 71.4% | mean 301.7d; median 350d | 8/11 | 19 |
| Crisis Confirmation | 3 | 4 | 1 | 6* | 16.7% | 335d (n=1) | 2/11 | 2 |

`*` 1994 is excluded from Crisis Confirmation because the available HY OAS history does not cover that year.

## 5. Window-level first-trigger result

| Window | Early Warning | Tightening State | Crisis Confirmation |
|---|---|---|---|
| 1994 tightening | FP — 1994-08-12 | FP — 1994-08-12 | N/A (HY coverage) |
| 2000 dot-com | 1999-04-09, lead 350d | 1999-04-09, lead 350d | no pre-anchor trigger |
| 2004–05 tightening | FP — 2004-05-14 | FP — 2004-05-14 | no trigger |
| 2008 GFC | 2006-06-09, lead 487d | 2006-06-09, lead 487d | no pre-anchor trigger |
| 2013 taper | FP — 2013-07-12 | no trigger | no trigger |
| 2016 China/energy | FP — 2015-12-11 | FP — 2015-12-11 | no trigger |
| 2017 reflation/Fed | FP — 2016-11-04 | FP — 2016-11-14 | no trigger |
| Q4 2018 selloff | no trigger | no trigger | no trigger |
| 2020 COVID | 2019-12-27, lead 54d | no trigger | no pre-anchor trigger |
| 2021 reflation/taper | FP — 2021-02-12 | FP — 2021-10-27 | FP — 2021-02-02 |
| 2022 rate shock | 2021-02-12, lead 325d | 2021-10-27, lead 68d | 2021-02-02, lead 335d |

## 6. Interpretation

### Early Warning

The first stage is very sensitive. It catches all four crisis windows, including the slow-burn 2022 episode 325 days before the anchor. However, it also fires in 6 of 7 non-crisis tightening/look-alike windows.

**Conclusion: good for detecting that macro stress is building, but too noisy to be a direct action trigger.**

### Tightening State

Adding the 2Y repricing condition reduces the false-alarm windows from 6/7 to 5/7 and suppresses the 2013 signal, but it also loses the 2020 crisis and shortens the 2022 lead from 325d to 68d.

**Conclusion: useful as a tightening-intensity label, but not sufficient as a universal crisis gate.**

### Crisis Confirmation

The independent crisis paths are much less noisy in the selected non-crisis set: only 1/6 evaluable FP windows. But they miss 3/4 crisis windows before the selected anchors.

More importantly, the 2022 result triggers on 2021-02-02, about 335 days before the 2022-01-03 anchor. That is too early to describe semantically as a "crisis confirmation". It is behaving like a broad stress-state signal.

**Conclusion: the raw trigger is precise in the selected FP set, but its timing semantics do not match the label "crisis confirmation".**

## 7. Falsification result

The three-state split is directionally useful, but the current definitions are not yet a complete sequential warning system.

The data show:

- Early Warning = early but noisy.
- Tightening State = somewhat less noisy, still misses some crisis types.
- Crisis Confirmation = low false alarms, but often too late or, in the 2022 case, too early relative to the actual crisis anchor.

Therefore the three stages should not yet be treated as a simple `A -> B -> C` mandatory chain.

## 8. Rule decision

**KEEP the three concepts, but revise the semantics.**

Proposed interpretation:

- Early Warning = "macro stress is building"
- Tightening State = "policy/rate pressure is becoming significant"
- Crisis Confirmation = "market damage/credit/liquidity confirmation is present"

D2 should remain a state descriptor rather than a mandatory crisis gate.

A future version should explicitly require crisis confirmation to occur after the warning state becomes active, or define a bounded confirmation window. That rule must be frozen before the next backtest.

## 9. Methodology limitations

1. This is a historical daily-panel replay, not a real-time vintage backtest; release lags are not modeled.
2. HY OAS coverage is incomplete for 1994, so Crisis Confirmation is not evaluated for that FP window.
3. The 11-window set is deliberately adversarial and small; the FP rates are window-level benchmark rates, not population false-positive rates.
4. The current result reports onset frequency and first trigger per window; production alert-rate behavior needs a full continuous-period panel.

## 10. Lesson Learned

The important result is not that one stage "wins". The result is that the three signals perform different jobs:

**Early Warning sees the problem early. Tightening State describes the pressure. Crisis Confirmation tells us whether actual damage is appearing.**

Trying to make one threshold perform all three jobs creates the B/C/D trade-off already observed.

## 11. Git decision

This result is material research evidence and should be preserved.

Git save: YES
