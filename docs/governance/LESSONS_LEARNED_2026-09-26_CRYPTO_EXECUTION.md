# Lesson Learned — Crypto Purchaseability

Date: 2026-09-26

## Lesson Learned

A market-state label alone is insufficient for actual decision support.

The BTC timing system must convert state into a purchaseable template containing:

price trigger + confirmation + tranche + invalidation.

A blind limit order at a drawdown threshold can fill during an accelerating decline. The baseline therefore uses price zones as trigger points and stabilization as the execution gate.

The daily structural state and live price trigger remain separate:
- daily structure uses the latest confirmed daily candle;
- live price can enter a trigger zone before stabilization is confirmed;
- the system outputs WAIT / BUY_READY / BLOCKED rather than treating price alone as a complete signal.

## Rule Change

YES

1. Add Crypto Execution Protocol V0.1.
2. Add explicit BUY-1/2/3/4 purchase states with crypto-sleeve allocation.
3. Prohibit blind limit orders in the baseline.
4. Require stabilization confirmation before pullback tranche execution.
5. Keep breakout confirmation as a separate research path.
6. Daily in-progress candle remains excluded from structural state.
7. Execution output must contain exact trigger prices when available.

## Current State

The execution template is coded for research monitoring.
Automatic order execution remains disabled.
Full promotion remains blocked by P6 DATA_NOT_READY.
