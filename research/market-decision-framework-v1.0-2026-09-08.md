# Investment Market Decision Framework v1.0

Date: 2026-09-08
Status: RESEARCH BASELINE — NOT YET PROMOTED TO LIVE TRADING RULE

## 1. Objective

Build a reproducible market-state engine that converts market data into:

`raw data → normalized factors → Market Score → Market Regime → horizon-specific score → buy strength / risk score → portfolio action`

The engine is a **state-classification system first**, not a return-prediction model. A high score means the observed market environment is historically more consistent with a favorable regime; it does not mean future returns are guaranteed.

## 2. Design principles

1. Separate market state from stock selection.
2. Separate long / medium / short horizons.
3. Prefer multiple independent evidence axes over duplicated indicators.
4. Use point-in-time data only; no look-ahead and no revised data leakage.
5. Keep economic logic, scoring rules, thresholds, and portfolio actions separately versioned.
6. Every rule must have a predefined falsification condition.
7. No rule is promoted from research to operational use without out-of-sample validation.

## 3. Market Score architecture

### 3.1 Primary five axes

| Axis | Weight | Purpose |
|---|---:|---|
| Trend / Price | 25% | Detect direction and persistence |
| Breadth / Internal strength | 20% | Determine whether the move is broad or concentrated |
| Volatility / Risk | 20% | Measure stress, dispersion, and drawdown risk |
| Rates / Liquidity / Credit | 20% | Measure financial-condition support or restraint |
| Cross-Asset | 15% | Confirm or challenge the equity narrative using other assets |

The weights above are **baseline research parameters**, not empirically optimized final weights.

### 3.2 Sub-indicators

#### A. Trend / Price
- 1d, 5d, 20d, 60d, 120d returns
- distance from 20/60/120/200-day moving averages
- moving-average slope
- moving-average alignment
- drawdown from recent high
- trend persistence / breakout state

#### B. Breadth / Internal strength
- advance / decline ratio
- advancing share of universe
- volume or turnover breadth
- share above 20d / 50d / 200d MA
- new highs / new lows
- sector breadth
- large-cap versus small/mid-cap participation

Universe definition must be fixed before backtesting. Changes in the universe are versioned changes to the experiment.

#### C. Volatility / Risk
- VIX for global risk
- VKOSPI for Korea
- realized volatility
- downside volatility
- index drawdown
- volatility term structure where reliable
- credit stress proxy / spread change

#### D. Rates / Liquidity / Credit
- U.S. 2Y and 10Y yields
- 10Y minus 2Y slope
- real yield proxy
- inflation compensation proxy
- KR rates / policy-rate expectations where available
- DXY / broad dollar
- financial-conditions index
- investment-grade / high-yield spread or equivalent stress proxy

The Chicago Fed NFCI is a useful reference structure because it combines 105 financial indicators across risk, credit, leverage and related markets rather than relying on one rate. citeturn578421search0turn578421search1

#### E. Cross-Asset
- S&P 500 / Nasdaq / semiconductor benchmark
- U.S. futures when doing same-day operational checks
- JPY / KRW and USD / KRW
- gold
- crude oil
- sovereign yields
- major crypto risk proxy
- Korea equity versus global equity relative strength

Cross-asset signals are treated as **confirmation / contradiction evidence**, not as independent return forecasts for the equity index.

## 4. Normalization: raw values → 0–100

Do not map raw levels directly into scores with arbitrary linear rules.

### 4.1 Preferred normalization

For each indicator, calculate a point-in-time historical percentile or robust z-score using only information available at that date.

Recommended baseline:

`indicator_score = 0–100 percentile rank`

For indicators where high values are bad, reverse the direction:

`risk_score = 100 - percentile_rank`

For heavy-tailed variables, use winsorization before standardization only when the winsorization rule is fixed ex ante.

### 4.2 Factor score

For each factor:

`Factor Score = weighted median/mean of constituent indicator scores`

Initial v1.0 choice: equal weight inside each factor unless evidence shows a justified alternative.

This intentionally reduces hidden double counting. Highly correlated indicators must be clustered before weighting.

### 4.3 Market Score

`Market Score = 0.25 Trend + 0.20 Breadth + 0.20 Risk + 0.20 Macro + 0.15 CrossAsset`

Range: 0–100.

Interpretation is state-based, not probabilistic until validated.

## 5. Market Regime v1.0

Base classification:

| Regime | Score | Interpretation |
|---|---:|---|
| R1 | 75–100 | Strong Risk-On |
| R2 | 60–74.9 | Normal Risk-On |
| R3 | 50–59.9 | Late uptrend / caution |
| R4 | 40–49.9 | Neutral / transition |
| R5 | 25–39.9 | Risk-Off |
| R6 | 0–24.9 | Panic / severe stress |

### 5.1 Stress override

A low score is not required to trigger R6. Apply an R6 override when at least **two independent stress clusters** are simultaneously severe, for example:

- equity drawdown / breadth collapse
- volatility spike
- credit stress
- funding / liquidity deterioration

This prevents the system from waiting for a slow composite-score deterioration during a fast shock.

### 5.2 Persistence / hysteresis

Avoid one-day regime flips.

Baseline rule:
- Entry into a new regime requires 2 consecutive observations, unless the R6 stress override is triggered.
- Return to a higher regime requires confirmation by 2 observations.
- Record both `raw_regime` and `confirmed_regime`.

This distinction is important for measuring false alarms and response lag.

## 6. Horizon-specific scores

Do not use one market weight across all investment horizons.

### Long horizon

`Long Investment Score = 0.70 Stock Score + 0.30 Market Score`

Use mainly structural trend, fundamentals, valuation and long-cycle risk. Daily noise should have low influence.

### Medium horizon

`Medium Investment Score = 0.60 Stock Score + 0.40 Market Score`

Use a balanced mix of company state and market regime.

### Short horizon

`Short Investment Score = 0.40 Stock Score + 0.60 Market Score`

Use breadth, volatility, flows and cross-asset confirmation more heavily.

These coefficients are v1.0 baselines and must be validated rather than assumed optimal.

## 7. Buy-strength engine

Separate the three concepts:

1. **Opportunity** — how attractive the stock is.
2. **Market permission** — whether the market environment supports new risk.
3. **Risk budget** — how much portfolio loss can be tolerated.

Do not use simple multiplication such as `Stock Score × Regime Modifier` as the only mechanism because it can create nonlinear distortions and make a good stock look worthless in a weak market.

Baseline:

`Buy Strength(horizon) = 0.70 StockScore(h) + 0.30 MarketPermission(h)` for long-term orientation, with the horizon coefficients above applied consistently.

For operational sizing, apply an additional risk-budget cap rather than embedding all risk into the score.

## 8. Risk score

Risk Score is **not** the inverse of Market Score.

It should independently measure:

- current volatility
- drawdown
- breadth deterioration
- credit stress
- liquidity stress
- cross-asset disagreement
- concentration risk
- event risk where applicable

Suggested interpretation:

`0–20 = low risk`
`20–40 = normal`
`40–60 = elevated`
`60–80 = high`
`80–100 = severe`

A high Market Score and high Risk Score can coexist. This is an intentional feature: a market may be trending strongly while becoming fragile.

## 9. State versus forecast separation

The engine must store two different outputs:

### State layer
`Market Score / Factor Scores / Regime / Risk Score`

### Outcome layer
`future 5d / 20d / 60d / 120d returns, volatility, drawdown`

Do not train the state labels directly on future returns before the baseline regime definition is fixed. Otherwise the label itself becomes contaminated by the target.

## 10. Validation protocol

A rule is eligible for promotion only after all applicable levels pass.

### Level 1 — economic logic
Does the indicator have a plausible transmission mechanism?

### Level 2 — conditional statistical relation
Compare state/score buckets with future returns, volatility and drawdown.

### Level 3 — historical simulation
Test the complete decision rule with fixed timestamps and realistic execution assumptions.

### Level 4 — out-of-sample
Freeze the specification before the OOS period.

### Level 5 — walk-forward
Repeat train / test splits through time.

### Level 6 — parameter sensitivity
Test neighborhoods around all important lookbacks and thresholds.

### Level 7 — transaction costs / slippage
Use conservative costs and stress them upward.

### Level 8 — cross-market validation
At minimum: KOSPI, S&P 500, Nasdaq, Nikkei, Euro Stoxx / MSCI World where data availability permits.

### Level 9 — multiple testing / data snooping
Record every tested specification. Use White's Reality Check or related bootstrap methods when evaluating a family of candidate rules. Sullivan, Timmermann and White explicitly show why technical-rule performance needs correction for data snooping. citeturn759787search1turn759787search4

For selected backtests, use Deflated Sharpe Ratio to account for selection bias, multiple testing and non-normal returns. citeturn759787search8

Use Probability of Backtest Overfitting / CSCV when the experiment has a large strategy-selection space. citeturn578421search4

### Level 10 — paper / shadow operation
Run the rule without allocating capital and compare live signal behavior against the frozen research specification.

## 11. Primary experiments

### Experiment A — score monotonicity
Bucket Market Score into 5 or 10 bins and compare future 5/20/60/120-day returns, realized volatility and MDD.

Success criterion is not merely positive average return. The relationship should be directionally stable, economically meaningful, and not disappear under modest specification changes.

### Experiment B — regime separation
Measure return, volatility, MDD, hit rate and recovery time for R1–R6.

### Experiment C — incremental value
Compare:
1. price-only
2. price + breadth
3. + risk
4. + macro
5. + cross-asset

to test whether each additional axis contributes independent information.

### Experiment D — horizon value
Compare long/medium/short weighting schemes against a common-weight baseline.

### Experiment E — action value
Simulate stock-level buy-strength rules under each regime and compare against buy-and-hold, periodic accumulation, cash baseline and simple trend baseline.

### Experiment F — robustness
Vary:
- MA windows
- lookback windows
- regime thresholds
- persistence length
- factor weights
- indicator inclusion / exclusion

The goal is a stable performance plateau, not a single best parameter.

## 12. Rejection / falsification rules

The framework must be downgraded, revised or rejected when any of the following occurs:

1. Score and future outcomes show no stable conditional separation.
2. Regime ordering is unstable across reasonable thresholds.
3. OOS performance collapses relative to development performance.
4. Small parameter changes cause large performance changes.
5. Transaction costs remove the economic value.
6. Cross-market behavior is inconsistent with the claimed mechanism.
7. Performance depends on one narrow historical episode.
8. The selected specification is no longer superior after multiple-testing adjustment.
9. Live/shadow signals materially diverge from backtest assumptions.

## 13. Data requirements

Every input series must have:

- source
- ticker / series identifier
- frequency
- publication timestamp or availability convention
- revision policy
- transformation
- direction (`higher_is_better` / `higher_is_worse`)
- normalization method
- missing-data handling
- backtest start date
- confidence / quality flag

The minimum reproducible dataset is a daily panel indexed by **observation date** plus **availability date**.

## 14. Research data-source priorities

1. official / primary market data
2. exchange and central-bank data
3. established institutional datasets
4. high-quality research databases
5. secondary commentary only for narrative context

Do not substitute a narrative source for a numerical primary series when a primary series is available.

## 15. Known evidence base

Time-series momentum research reports persistent predictability from a security's own past returns across 58 diversified futures and forwards over more than 25 years, with robustness across subsamples and lookbacks. citeturn759787search0

Longer historical work also reports trend-following evidence across markets and macro environments, supporting trend as a candidate signal family while not proving this exact composite framework. citeturn759787search3turn759787search10

Financial-conditions indices provide a useful precedent for combining heterogeneous financial variables into a single state indicator rather than interpreting one rate or spread in isolation. citeturn578421search0turn578421search7

Out-of-sample evaluation has long been used to distinguish genuine leading information from in-sample fit; for example, Estrella and Mishkin evaluated financial variables as recession predictors at 1–8 quarter horizons and found the yield-curve slope particularly useful beyond two quarters in their sample. citeturn578421search11

## 16. v1.0 implementation sequence

1. Freeze universe and data dictionary.
2. Build daily point-in-time market panel.
3. Implement factor normalization.
4. Implement factor scores and Market Score.
5. Implement R1–R6 plus stress override and persistence.
6. Generate daily score history.
7. Run Experiments A–C before connecting to stock actions.
8. Only after A–C pass, test horizon weights and buy-strength rules.
9. Run OOS / walk-forward / robustness / multiple-testing checks.
10. Start shadow operation before any capital deployment.

## 17. Governance status

This document establishes the **research baseline** only.

Promotion path:

`RESEARCH → VALIDATED → SHADOW → OPERATIONAL`

No promotion is allowed solely because the backtest CAGR or Sharpe is attractive.

## 18. Key lesson

The important deliverable is not a 0–100 number. It is a **falsifiable state machine** whose state definition, data timing, score construction, regime transitions, portfolio actions, and validation protocol are all explicit and reproducible.
