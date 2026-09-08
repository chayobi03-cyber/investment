# Stock Score V1 — Specification

Date: 2026-09-08
Status: RESEARCH BASELINE — DATA CONNECTION PENDING

## 1. Objective

종목별로 시장 상태와 독립된 `Long / Medium / Short` 점수를 계산하고, 이후 Sector / Market / Catalyst / Risk를 별도 계층에서 결합한다.

Baseline horizon weights:

`Long 50% / Medium 30% / Short 20%`

These weights are frozen operating assumptions until OOS validation. Do not optimize them using the first OOS sample.

## 2. Stock Factors

The minimum factor set is:

1. Trend / Momentum
2. Earnings / Fundamental
3. Valuation
4. Relative Strength
5. Supply / Demand
6. Institutional / Foreign Flow
7. Sector Strength
8. Catalyst
9. Risk / Drawdown

### Anti-double-count rule

Trend and Momentum are one factor for weighting purposes. Relative Strength is defined versus a fixed benchmark and is not re-added through the same-price trend signal. Sector Strength is based on sector-level relative performance and is not copied into stock relative strength. Institutional/Foreign Flow is flow data, while Supply/Demand is price-volume/order-flow behavior; correlation must be measured before aggregation. Market Regime is excluded from the raw Stock Score and applied separately in BuyStrength/permission/risk constraint.

## 3. Horizon Factor Weights

### Long Score

| Factor | Weight |
|---|---:|
| Earnings / Fundamental | 30% |
| Valuation | 20% |
| Trend / Momentum | 15% |
| Relative Strength | 10% |
| Sector Strength | 10% |
| Supply / Demand | 5% |
| Institutional / Foreign Flow | 3% |
| Catalyst | 4% |
| Risk / Drawdown | 3% |

### Medium Score

| Factor | Weight |
|---|---:|
| Trend / Momentum | 20% |
| Relative Strength | 20% |
| Earnings / Fundamental | 15% |
| Sector Strength | 15% |
| Institutional / Foreign Flow | 15% |
| Supply / Demand | 5% |
| Valuation | 3% |
| Catalyst | 4% |
| Risk / Drawdown | 3% |

### Short Score

| Factor | Weight |
|---|---:|
| Trend / Momentum | 25% |
| Supply / Demand | 20% |
| Relative Strength | 15% |
| Sector Strength | 10% |
| Institutional / Foreign Flow | 10% |
| Catalyst | 10% |
| Risk / Drawdown | 5% |
| Earnings / Fundamental | 3% |
| Valuation | 2% |

These are starting specifications only. They must not be tuned to historical outcomes before the baseline validation set is frozen.

## 4. Factor Definitions

### Trend / Momentum

Use fixed lookbacks aligned with horizon: long-term 120/200D structure, medium-term 20/60D and 1–6M momentum, short-term 5/10/20D. Include distance to moving averages, slope, persistence, breakout/reversal state. Avoid counting the same return window multiple times.

### Earnings / Fundamental

Revenue growth, operating-income growth, EPS growth, margin trend, ROIC/ROE where economically appropriate, FCF generation, leverage/debt service, and estimate revision when a point-in-time estimate source is available. Report missing fields rather than substituting later-period information.

### Valuation

Use ratio measures appropriate to business type: PER/PBR/EV-EBITDA/FCF yield or sector-specific alternatives. Prefer percentile versus own history and peer/sector distribution over absolute thresholds. Financials require separate valuation handling.

### Relative Strength

Stock return relative to fixed benchmark and sector benchmark over horizon-aligned windows. Benchmark definitions are frozen in the dataset manifest.

### Supply / Demand

Volume/turnover behavior, accumulation/distribution proxies, abnormal turnover, gap/price-volume confirmation, and drawdown recovery behavior. Do not infer institutional demand from price alone.

### Institutional / Foreign Flow

KRX investor-type net buy/sell and rolling accumulation by stock when available. Keep raw flow, flow trend, and flow persistence separate. Do not double count foreign ownership as daily flow.

### Sector Strength

Sector index relative return, breadth, trend and participation versus KOSPI/KOSDAQ benchmark. SectorScore is calculated before StockScore.

### Catalyst

Point-in-time events such as earnings/guide changes, material contracts, product/regulatory events, capital actions and other company disclosures. Catalyst is event-state information, not a narrative sentiment score.

### Risk / Drawdown

Volatility, downside volatility, recent and historical drawdown, gap risk, liquidity/turnover risk, concentration/event risk. Risk is stored independently from opportunity score.

## 5. Long / Medium / Short Score Calculation

For each horizon `h`:

`StockScore_h = Σ weight_i,h × FactorScore_i,h`

All factor scores are 0–100 and are point-in-time.

If required inputs are unavailable, the engine does not manufacture a proxy silently. The score is marked `INSUFFICIENT_DATA` or uses a pre-approved missing-data policy recorded in the rule registry.

## 6. Composite Stock Score

`CompositeStockScore = 0.50*Long + 0.30*Medium + 0.20*Short`

This is a frozen operating baseline, not an optimized result.

## 7. BuyStrength

User-proposed baseline:

`BuyStrength = 0.40*Stock + 0.25*Sector + 0.25*Market + 0.10*Catalyst`

Use `Stock = CompositeStockScore` for the baseline implementation. Sector and Market are independently computed outside StockScore.

Risk is not hidden inside the 0.40/0.25/0.25/0.10 weights. Apply a separate Risk Alarm / sizing constraint after BuyStrength.

Therefore output must show both:

`BuyStrength` and `Risk Alarm`

A high BuyStrength can still result in `관망` or `매수 금지` when the risk constraint fails.

## 8. Action Mapping — baseline

| Condition | Action |
|---|---|
| High BuyStrength + low/moderate risk + confirmation | 강한 매수 |
| High BuyStrength + acceptable entry / risk | 분할매수 |
| Good score but entry extension / short-term risk elevated | 눌림목 매수 |
| Existing holding / no sufficient new edge | 보유 |
| Insufficient evidence / mixed signals | 관망 |
| Risk alarm / data integrity failure / severe regime constraint | 매수 금지 |

Exact numeric thresholds are deliberately not fixed in this specification. They require a frozen dataset and validation study rather than arbitrary cutoffs.

## 9. Universe V1

Initial universe:

- 삼성전자
- SK하이닉스
- 삼성SDI
- KB금융
- 현대차
- 삼성화재
- SK이노베이션
- 두산에너빌리티
- NAVER
- 삼성바이오로직스

Expand to KOSPI/KOSDAQ large caps only after the data pipeline and survivorship/universe rules are stable.

## 10. Required Output Fields

`rank, ticker, name, as_of, Long, Medium, Short, Composite, Sector, Market, Catalyst, Risk, BuyStrength, RiskAlarm, Action, data_completeness, evidence_refs`

No rank is published as a real investment ranking when any critical input is missing or the score is based on substituted/estimated data.
