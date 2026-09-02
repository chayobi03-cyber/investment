# Stress Convergence v0.2.3 — Three-Stage Daily-Panel Validation

Date: 2026-09-02
Status: DAILY-PANEL MEASUREMENT / RESEARCH ONLY
Workflow run: 33640923172
Validated implementation commit: 36ce6c8c15ef5211d64c5f8b563749e893ce7ad3

## 1. Purpose

Run the expanded 11-window benchmark against actual daily data and measure three states separately:

1. Early Warning — R + I sustained for two consecutive weekly observations.
2. Tightening State — Early Warning + 2Y repricing >= +40bp from trailing 12-month low.
3. Crisis Confirmation — existing Credit/Liquidity OR Growth/Exogenous path; D2 is contextual, not a hard gate.

## 2. Measured results

| Stage | Missed crises (미탐) | Crisis windows | False alarms (오탐) | Non-crisis windows evaluated | FP rate | Average early detection | Median early detection | Windows with any trigger | Alert-start events |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Early Warning | 0 | 4 | 6 | 7 | 85.7% | 304d | 337.5d | 10/11 | 19 |
| Tightening State | 1 | 4 | 5 | 7 | 71.4% | 301.7d | 350d | 8/11 | 19 |
| Crisis Confirmation | 3 | 4 | 1 | 6* | 16.7% | 335d† | 335d† | 2/11 | 2 |

`*` 1994 is excluded from Crisis Confirmation because available HY OAS history does not cover that year.

`†` n=1. The 2022 trigger occurred 335 days before the 2022 anchor, which is too early to interpret literally as a crisis confirmation.

## 3. Window-level results

| Window | Early Warning | Tightening State | Crisis Confirmation |
|---|---|---|---|
| 1994 tightening | FP — 1994-08-12 | FP — 1994-08-12 | N/A |
| 2000 dot-com | 1999-04-09 (350d early) | 1999-04-09 (350d early) | no pre-anchor trigger |
| 2004–05 tightening | FP — 2004-05-14 | FP — 2004-05-14 | no trigger |
| 2008 GFC | 2006-06-09 (487d early) | 2006-06-09 (487d early) | no pre-anchor trigger |
| 2013 taper | FP — 2013-07-12 | no trigger | no trigger |
| 2016 China/energy | FP — 2015-12-11 | FP — 2015-12-11 | no trigger |
| 2017 reflation/Fed | FP — 2016-11-04 | FP — 2016-11-14 | no trigger |
| Q4 2018 selloff | no trigger | no trigger | no trigger |
| 2020 COVID | 2019-12-27 (54d early) | no trigger | no pre-anchor trigger |
| 2021 reflation/taper | FP — 2021-02-12 | FP — 2021-10-27 | FP — 2021-02-02 |
| 2022 rate shock | 2021-02-12 (325d early) | 2021-10-27 (68d early) | 2021-02-02 (335d early) |

## 4. What the numbers mean

### Early Warning

- It catches all 4 crisis windows.
- It fires in 6 of 7 non-crisis windows.
- It is therefore a good **"something is building"** signal, but it is too noisy for direct action.

### Tightening State

- It cuts false-alarm windows from 6/7 to 5/7.
- It removes the 2013 false alarm.
- It misses the 2020 crisis because the rate-pressure condition does not rise enough.
- For 2022, it arrives 68 days before the anchor rather than 325 days before it.

It is useful as a **"rate pressure is becoming meaningful"** state, not as a universal crisis detector.

### Crisis Confirmation

- It has the lowest observed false-alarm rate among the three states (1/6 evaluable non-crisis windows).
- It still misses 3/4 crisis windows before their selected anchors.
- The 2022 trigger is 335 days early and is therefore better interpreted as a broad stress signal than literal crisis confirmation.

## 5. Decision

**Do not promote any of the three states as a single final action rule yet.**

Keep the three concepts separate:

`Early Warning` = macro stress is building

`Tightening State` = rate/policy pressure is significant

`Crisis Confirmation` = actual market/credit damage is appearing

The previous D2 idea should remain a state descriptor rather than a hard crisis gate.

The next experiment should impose a frozen rule for how long after Early Warning a Crisis Confirmation is considered valid, then rerun the same 11 windows.

## 6. Methodology limitations

1. This is a historical daily-panel replay, not a real-time publication-vintage backtest; release lags are not modeled.
2. HY OAS data are incomplete for 1994.
3. The 11 windows are an adversarial benchmark, not a population-wide estimate of false-alarm probability.
4. `Alert-start events` counts starts of a state inside the selected windows; it is not the same as a daily alert rate.

## 7. Lesson Learned

The three signals are doing different jobs rather than competing for one winner:

**Early Warning sees the problem early. Tightening State describes the pressure. Crisis Confirmation should verify that real damage is appearing.**

Trying to force one threshold to perform all three jobs creates the same sensitivity/specificity trade-off seen in B/C/D.

## 8. Git status

Research result: preserved in Git.

Git save: YES
