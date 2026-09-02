# Korea Layer KOSPI Entry Threshold Backtest v0.1

Date: 2026-09-02 KST  
Status: **EXECUTABLE RESEARCH TEST — NOT A CAPITAL-ALLOCATION RULE**

## 1. Research question

Validate whether the provisional KOSPI entry zones from Korea Market Transmission Layer v0.1 contain incremental risk-adjusted value when combined with Stress Convergence v0.2 state.

Provisional absolute zones:

- 6,600–6,750: first accumulation/watch
- 6,300–6,500: stronger accumulation
- 6,000–6,300: stress-scenario accumulation
- >6,800 with improving foreign flow: confirmation/add-on

The backtest must not assume that these absolute index levels are historically stationary.

## 2. Critical comparability rule

KOSPI is a level index with a changing long-run level regime. The 6,000–6,750 absolute bands are concentrated in the 2026 regime and therefore cannot be validated against 2000/2008/2020/2022 using raw index levels.

The executable test therefore performs two separate analyses:

1. **Absolute-zone touch test:** records whether the 2026 absolute zones have enough observations to support statistical inference. Expected outcome: insufficient historical sample.
2. **Scale-invariant validation:** converts each 2026 absolute band into an equivalent **drawdown from the contemporaneous 252-trading-day KOSPI high**, then evaluates all historical occurrences of the equivalent drawdown interval since 2000.

This prevents a false conclusion caused by non-stationary index-level scaling.

## 3. Entry event definition

An entry event begins on the first trading day KOSPI enters the mapped drawdown interval after being outside that interval on the prior trading day.

For each entry event measure:

- KOSPI close and 252-day drawdown;
- Stress Convergence state at entry;
- forward return at approximately 1m/3m/6m/12m;
- worst forward drawdown over the same horizons;
- time to recover the entry close.

Events are not compounded into a portfolio simulation in v0.1; this is an entry-quality test.

## 4. Stress Convergence v0.2 linkage

The executable backtest uses the existing v0.2 gate topology where public reproducible time series permit reconstruction:

### Inflationary convergence proxy

`Energy + Credit + (Inflation OR severe Energy) + (Rates)`

### Financial-shock leg

`Credit + VIX + NFCI`

Daily persistence follows the v0.2 rule of 5 trading days or 2-of-3 observations in 5 days; weekly/monthly persistence is applied for NFCI/T5Y5Y where applicable.

Fed-hike probability and AI-financing are intentionally not backfilled because the required historical series are not reconstructed in this run. Therefore this is a **v0.2 topology proxy**, not a claim of a full 0–24 score reproduction.

## 5. False-positive / false-negative / lead-time linkage

To connect entry levels with the prior threshold validation, KOSPI stress events are defined for evaluation as a subsequent >=15% drawdown from the 252-day high, with nearby observations merged into a single episode.

For Stress Convergence:

- **TP:** an L2 proxy trigger occurs before the drawdown event anchor.
- **FN:** a >=15% drawdown event occurs with no preceding L2 proxy trigger within the allowed lookback.
- **FP:** an L2 proxy trigger is not followed by a >=15% drawdown within 60 calendar days.
- **Lead time:** event anchor minus first qualifying L2 trigger.

These are evaluation labels only and do not use future KOSPI data inside the live signal calculation.

## 6. Acceptance criteria

The provisional KOSPI bands are not promoted unless:

1. absolute 6,000–6,750 bands have sufficient independent observations, or the drawdown normalization is explicitly adopted;
2. entry events show positive and economically meaningful forward returns after transaction-cost-free comparison against an unconditional benchmark;
3. deeper bands do not merely improve headline return by taking materially more unresolved drawdown risk;
4. conditional results improve when Stress Convergence is **L0/L1 versus L2+**, or the data falsify that conditioning hypothesis;
5. the Korea layer does not materially worsen the established Stress Convergence FP/FN/lead-time trade-off;
6. results remain directionally stable across threshold sensitivity bands rather than depending on a single hand-picked level.

## 7. Next extension

Add the Korea-specific downstream variables that were identified in Korea Layer v0.1 but are not required for the first executable pass:

- foreign KOSPI net flow;
- Samsung Electronics / SK hynix returns and foreign flow;
- semiconductor export growth;
- breadth / realized volatility.

Those variables should be tested as **incremental confirmation features**, not as substitutes for the global Stress Convergence gate.
