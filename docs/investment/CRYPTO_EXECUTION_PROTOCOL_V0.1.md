# Crypto Execution Protocol V0.1

Date: 2026-09-26
Status: RESEARCH-ONLY EXECUTION TEMPLATE / NOT LIVE AUTO-TRADING

## Objective

Convert BTC entry-timing state into a purchaseable instruction set:

- exact trigger;
- executable price band;
- staged sleeve allocation;
- invalidation condition;
- confirmation condition.

This is an execution template, not an automatic order system.

## Execution Principle

Do not place a blind limit order simply because BTC reaches a lower price.

Baseline:

PRICE ZONE REACHED
-> STABILIZATION CONFIRMATION
-> EXECUTE NEXT AVAILABLE SESSION

Deep dislocations require stricter confirmation.

## Purchase Routes

| Tranche | Reference | Baseline allocation |
|---|---|---:|
| BUY-1 | Z1: -5% from prior 60D high | 20% |
| BUY-2 | Z2: -8% from prior 60D high | 25% |
| BUY-3 | Z3: -12% from prior 60D high | 30% |
| BUY-4 | post-stabilization confirmation | 25% |

The percentages refer to the crypto sleeve.

### BUY-1

Price enters Z1.

Required confirmation:
- 3D return > 0;
- close >= MA20;
- structural trend valid.

Execute only after confirmation.

### BUY-2

Price enters Z2 before or after BUY-1.

Required:
- same stabilization confirmation;
- no active multi-shock block in the richer engine.

### BUY-3

Price reaches Z3.

Required:
- 3D return > 0;
- close >= MA20;
- close >= MA50;
- no severe systemic stress.

### BUY-4

Remaining allocation after price-route confirmation plus at least one independent risk-cluster confirmation and stabilization persistence.

## Breakout Route

If BTC does not pull back and instead closes above the prior 60D high while:
- 5D return > 0;
- structural trend valid;
- no hard risk block;

emit a separate BREAKOUT_CONFIRMATION event.

This route is tested separately from pullback entries.

## No-Chase Rule

When BTC is within 2% of the prior 60D high and no pullback confirmation exists:

ACTION = WAIT

Do not convert strong trend into automatic purchase.

## Invalidation

Cancel or defer an entry state when:
- structural trend breaks;
- data becomes stale or fails PIT;
- multi-shock deterioration is confirmed;
- a new episode begins without stabilization;
- confirmation expires before execution.

## Live Output

CRYPTO EXECUTION
STATE: WAIT / READY / BUY_CONFIRMATION / BLOCKED
CURRENT PRICE:
ZONE:
BUY-1:
BUY-2:
BUY-3:
BUY-4:
TRIGGER:
INVALIDATION:
SLEEVE ALLOCATION:
DATA TIME:

The BUY labels are state labels for the research/execution template. They do not authorize automatic exchange execution.

## Promotion Gate

Automatic trading is blocked until the full Crypto Risk Engine passes:

PIT -> P0-P6 -> OOS -> walk-forward -> sensitivity -> falsification -> execution-cost -> risk-policy approval.
