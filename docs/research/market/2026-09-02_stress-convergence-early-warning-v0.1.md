# Stress Convergence Early-Warning Framework v0.1

Date: 2026-09-02 KST
Status: PROVISIONAL — not yet backtested

## 1. Core hypothesis

The existing AI → Private Credit risk hypothesis is expanded into a parallel stress-convergence structure:

Geopolitics → Energy → Inflation → Fed → Rates → Credit

running in parallel with:

AI investment/financing → leverage/refinancing dependence → Private Credit → Credit transmission

The investment question is whether independent stress axes converge strongly enough to justify defensive action before broad credit deterioration becomes visible.

## 2. Early-warning dimensions

| Axis | Primary indicator | Provisional warning condition |
|---|---|---|
| Energy | Brent crude | >$90; severe >$100 |
| Inflation | US 5Y5Y forward inflation | >2.5%; severe >3.0% |
| Fed | Implied near-term hike probability / repricing | >50% hike probability or sharp hawkish repricing |
| Rates | US 10Y Treasury | >4.75%; severe >5.0% |
| Credit | US HY OAS | >400bp; severe >500bp |
| Financial conditions | Chicago Fed NFCI | >0; severe >0.5 |
| Market stress | VIX | >25; severe >35 |
| AI financing | AI CapEx/FCF pressure + refinancing/credit-event evidence | 2+ independent financing stress signals |

Thresholds are provisional and must be calibrated against historical false positives/negatives.

## 3. Scoring

Each dimension receives 0–3 points:

- 0 = normal
- 1 = warning
- 2 = material stress
- 3 = severe stress

SC_raw = sum of eight dimensions, range 0–24.

Action levels:

- L0 Normal: 0–3
- L1 Watch: 4–7
- L2 Defensive: 8–11
- L3 High Stress: 12–17
- L4 Crisis Convergence: 18–24

## 4. Convergence rule

A high score alone is insufficient. Action escalation requires causal independence.

Do not count mechanically linked observations as independent confirmations. Example: Fed repricing and Treasury yield movement may represent one rates-policy transmission rather than two independent stress axes.

L2 or above should require at least three economically distinct axes showing persistent stress, with at least one Credit/Private Credit confirmation.

## 5. Trigger logic

A trigger should combine:

1. Level: threshold breached.
2. Delta: deterioration over a defined lookback window.
3. Persistence: breach persists for multiple observations.
4. Confirmation: another independent axis confirms the same transmission.

This prevents one-day geopolitical headlines or market noise from creating a false crisis signal.

## 6. Falsifiers

The framework is falsified or materially weakened if:

- Energy remains elevated but inflation expectations do not rise.
- Inflation rises temporarily but Fed/rates normalize without credit deterioration.
- Rates remain high while HY spreads and private-credit stress remain contained.
- AI financing stress appears but does not transmit into broader credit conditions.
- Historical backtests generate unacceptable false-positive or false-negative rates.

## 7. Current provisional snapshot

As of 2026-09-02, the working assessment is L1 Watch rather than confirmed credit stress. The current concern is Energy → Inflation/Fed → Rates convergence; broad HY credit and financial-condition confirmation is not yet established.

The key next test is whether the energy/rates shock propagates into inflation expectations and then into credit spreads/private-credit stress.

## 8. Next validation step

Backtest the thresholds against:

- 2000–2002 dot-com stress
- 2007–2009 GFC
- 2020 COVID shock
- 2022 inflation/rates shock
- selected non-crisis false-positive periods

Measure false positives, false negatives, lead time, and contribution of each axis. Calibrate thresholds only after this test.
