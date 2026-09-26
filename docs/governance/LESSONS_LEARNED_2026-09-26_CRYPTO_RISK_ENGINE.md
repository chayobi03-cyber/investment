# Lesson Learned — Crypto Risk Engine

Date: 2026-09-26

## Lesson Learned

Crypto should not be modeled as a separate prediction game.

The existing capital-preservation architecture is reusable, but crypto requires explicit separation of:

- Market Score
- Asset / Price Opportunity
- Permission / Risk Constraint
- Buy State

A strong market trend can coexist with poor entry timing, and a cheap price can coexist with an active macro/derivatives shock. Therefore "cheap" and "permitted to escalate" are separate dimensions.

Derivatives variables such as funding and open interest are more safely treated first as leverage-risk / overheating controls. Their value as directional alpha must be demonstrated by incremental out-of-sample evidence.

BTC should be the first validation asset. Secondary assets and broader altcoin logic should not be promoted before the core state machine survives PIT, OOS, walk-forward, sensitivity, and falsification tests.

## Rule Change

YES

1. Investment Research Loop upgraded from v1.0 to v1.1.
2. Crypto Risk Engine V0.1 added as a research-only module.
3. Market Score / Opportunity Score / Permission / Action State separation is now a reusable governance rule.
4. Multi-shock deterioration is a hard escalation block in the crypto baseline.
5. Crypto exposure is modeled relative to a dedicated crypto sleeve during research, not directly as a total-portfolio target.
6. No leverage, margin, or automatic order execution is part of the baseline engine.

## Validation Status

- Deterministic engine: CODED
- Unit tests: PASS
- PIT historical dataset for full crypto model: NOT YET COMPLETE
- P0-P6 crypto backtest: NOT YET COMPLETE
- OOS / walk-forward / sensitivity: NOT YET COMPLETE
- Live deployment: DISABLED

Therefore the valid operational state remains:

DATA_NOT_READY / RESEARCH_ONLY

## Git Commit

This lesson is persisted because it changes reusable methodology and governance.
