# Market Regime Engine V1

Date: 2026-09-08
Status: OPERATIONAL RESEARCH SPEC — DATA CONNECTION PENDING

## 1. Purpose

`RAW DATA → point-in-time control → normalization (0–100) → Trend/Breadth/Risk/Macro/Cross-Asset → Market Score → Stress Override → Regime (R1–R6)`을 재현 가능한 형태로 정의한다.

시장 상태와 종목 상태를 분리한다.

```text
MarketScore
    ↓
Market Regime / Market Risk
    ↓
SectorScore
    ↓
Stock Score (Long / Medium / Short)
    ↓
BuyStrength + Risk Constraint
    ↓
Action
```

## 2. Market State Vector

| Axis | Baseline weight | Core inputs |
|---|---:|---|
| Trend | 25% | 1/5/20/60/120D return, MA distance/slope/alignment, drawdown |
| Breadth | 20% | advance/decline, % above MA, new high/low, sector participation |
| Risk | 20% | VIX, VKOSPI, realized/downside vol, drawdown, credit stress |
| Macro | 20% | U.S. 2Y/10Y, curve, real-rate proxy, DXY, KR rates/FX, credit |
| Cross-Asset | 15% | S&P 500, SOX, USD/KRW, JPY/KRW, gold, WTI, BTC, Korea/global RS |

Weights are research baselines, not optimized parameters.

## 3. Normalization

Default transformation is point-in-time historical percentile using observations available at timestamp `t` only.

`score = percentile_rank(history_to_t)`

For variables where higher raw value means worse market conditions, reverse the direction.

`risk-oriented signal score = 100 - percentile_rank(history_to_t)`

Heavy-tailed indicators may use fixed ex-ante winsorization. No future information may enter the normalization window.

Within-factor aggregation defaults to equal weight after correlation clustering. Highly correlated indicators must not receive duplicated weight merely because they have different names.

## 4. Market Score

`MarketScore = 0.25*Trend + 0.20*Breadth + 0.20*Risk + 0.20*Macro + 0.15*CrossAsset`

Market Opportunity and Risk are separate outputs.

## 5. Regime

| Regime | Score range | Meaning |
|---|---:|---|
| R1 | 75–100 | Strong Risk-On |
| R2 | 60–74.9 | Normal Risk-On |
| R3 | 50–59.9 | Late uptrend / caution |
| R4 | 40–49.9 | Neutral / transition |
| R5 | 25–39.9 | Risk-Off |
| R6 | 0–24.9 | Panic / severe stress |

### Stress override

R6 may be triggered even if composite MarketScore is above 25 when at least two independent stress clusters are simultaneously severe, such as equity breadth/drawdown collapse, volatility spike, credit stress, or liquidity/funding deterioration.

Store both `raw_regime` and `confirmed_regime`.

### Persistence

Default confirmation rule is two consecutive observations for a regime transition. R6 stress override can bypass persistence. This is a research baseline and must be validated for false transitions and response lag.

## 6. Separation Rule

MarketScore/Regime is not part of the raw Stock Score.

Reason: including Market Regime inside Stock Score and again inside BuyStrength causes double counting and makes the contribution of market conditions opaque.

Market is applied in the separate Market/permission layer and risk constraint.

## 7. Data-Time Rules

Each observation must store:

- observation timestamp
- source timestamp / publication timestamp when applicable
- market session / timezone
- availability timestamp
- source identifier
- revision status
- raw value
- normalized value
- rule version

Decision timestamp `t` may use only data with `available_at <= t`.

## 8. Promotion Gate

No rule is promoted to live operation before point-in-time backtest, OOS validation, walk-forward, parameter sensitivity, execution-cost analysis, and falsification.
