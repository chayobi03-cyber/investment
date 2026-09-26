# Multi-Asset Sub-Agent Architecture V0.1

Date: 2026-09-26
Status: RESEARCH STRUCTURE — NOT LIVE

## Scope

Unify three asset families under one capital-preservation control plane:

- EQUITY: KRX / US equities, index, sector, stock
- GOLD: spot / futures / listed gold instruments
- CRYPTO: BTC / ETH / SOL and later broader crypto universe

The system does not use one universal entry signal. Market state and permission are shared controls; entry signals remain asset-specific.

## Agent topology

```text
                         Multi-Asset Orchestrator
                                  |
       +--------------------------+--------------------------+
       |                          |                          |
 Data/PIT Agent             Regime Agent              Evidence Agent
       |                          |                          |
       +--------------------------+--------------------------+
                                  |
                 +----------------+----------------+
                 |                                 |
          Permission Agent                    Risk Agent
                 |                                 |
       +---------+----------+----------+             |
       |                    |          |             |
 Equity Signal Agent   Gold Signal  Crypto Signal   |
       |                    |          |             |
       +--------------------+----------+-------------+
                                  |
                         Decision / Gate Agent
                                  |
                    BUY_ALLOWED = false (current)
```

## Separation rules

1. Data/PIT is the only agent allowed to declare data readiness.
2. Regime consumes validated PIT observations and never mutates asset thresholds.
3. Signal agents consume asset-specific price/factor inputs only. They must not consume permission output.
4. Permission is an overlay. It can block a signal but cannot rewrite it.
5. Risk is independent from signal conviction. It can reduce exposure to zero.
6. Evidence records Claim -> Data -> Timestamp -> Source -> PIT availability -> Calculation -> Result.
7. Decision is a gatekeeper, not an autonomous optimizer or forecaster.
8. Missing required evidence = DATA_NOT_READY. No silent imputation.
9. `available_at > decision_timestamp` is always ineligible.
10. Current deployment invariant: `BUY_ALLOWED=false` for all asset families.
11. Threshold changes require a new rule version and fresh chronological/OOS/walk-forward validation.
12. No shared mutable state between sub-agents.

## Common data axes

### Trend
1/5/20/60/120/200D returns, MA distance/slope/alignment, drawdown.

### Breadth / Relative Strength
Advance-decline, participation, cross-asset relative strength, sector breadth.

### Risk
Realized/downside volatility, drawdown, volatility indexes, credit/liquidity stress.

### Macro / Liquidity
Rates, real yields, curve, DXY, KRW FX, liquidity conditions, inflation transmission.

### Cross-Asset
Equity indices, SOX, USD/KRW, JPY/KRW, gold, WTI, BTC and relevant asset-family comparators.

## Asset-specific signal layer

### Equity
Candidate inputs:
- market/sector regime
- stock trend and relative strength
- foreign/institutional flow
- earnings / fundamental state
- valuation state
- event calendar

Existing Stock Score / BuyStrength work remains the source of truth.

### Gold
Candidate inputs:
- gold spot / futures trend
- real yields
- DXY
- inflation / geopolitical stress
- gold-equity/commodity relative strength
- drawdown / stabilization / breakout state

Gold signal logic must distinguish structural hedge demand from panic spikes.

### Crypto
Candidate inputs:
- frozen v0.2 BTC price signal
- BTC/ETH/SOL breadth and relative strength
- derivatives stress
- macro / FX
- regulation / market structure
- geopolitical transmission

Existing crypto v0.2 threshold contract remains frozen.

## Decision contract

Decision output has:

- asset
- signal_state
- permission_status
- market_gate
- confirmed_regime
- risk_gate
- evidence_status
- blocker_codes
- buy_allowed
- execution_allowed

Current invariant:

`buy_allowed == false`
`execution_allowed == false`

This is independent of any exposure multiplier or research score.

## Research sequence

Data/PIT -> Regime -> Asset Signal -> Permission -> Risk -> Evidence -> Decision -> P0-P6/OOS/WF

No threshold tuning before the frozen-rule research cycle is complete.

## Next implementation stages

1. Connect existing Stock Score / BuyStrength to Equity Signal Agent.
2. Build Gold PIT series and historical event model.
3. Connect frozen Crypto v0.2 + permission PIT layer.
4. Create a common multi-asset P0-P6 evaluation contract.
5. Add portfolio-level correlation/concentration and stress aggregation.
6. Only after asset-level P6 promotion, permit an execution adapter.
