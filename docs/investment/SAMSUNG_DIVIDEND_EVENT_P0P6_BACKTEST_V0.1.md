# Samsung Electronics Dividend Event → P0~P6 Backtest v0.1

Date: 2026-09-22
Status: RESEARCH CONTRACT — FROZEN / NOT LIVE

## Objective

Test whether entering Samsung Electronics during the 2026-09-22 → 2026-09-29 pre-ex-dividend window adds risk-adjusted value after combining the dividend event with the existing Observation → P0~P6 market pipeline.

This is an event overlay, not a replacement for P0~P6.

`Opportunity = event economics + stock/price`
`Permission = P0~P6 market/risk gates`
`Action = f(Opportunity, Permission)`

## Current event

- Decision window: 2026-09-22 through 2026-09-29
- Record date: 2026-09-30
- Ex-dividend date: 2026-09-29
- Latest article estimate: KRW 4,604/share
- Estimated gross yield at price P: 4,604 / P
- Estimated net cash dividend under 15.4% withholding: KRW 3,895/share
- 4,604 is NOT an officially fixed dividend and must never be treated as ground truth.

The event input must retain source, publication/availability timestamp, and revision status. A later-confirmed dividend must not be used to simulate an earlier decision.

## Entry variants

For every eligible decision date in 2026-09-22..2026-09-28, evaluate:

- E0: no event overlay; existing P0~P6 gate only.
- E1: event-aware watch/scout; dividend yield is information only.
- E2: event-aware scout when expected net dividend exceeds modeled expected adverse gap and P2+ permission is present.
- E3: event-aware active entry only when P3+ is present and no oil/rates/FX/credit multi-shock block is active.

2026-09-29 is retained as an ex-date observation/control date, not a normal pre-ex entry date.

## No-lookahead event economics

At decision timestamp t:

`expected_net_dividend_t = expected_gross_dividend_t * (1 - tax_rate)`

`event_edge_t = expected_net_dividend_t / entry_price_t - expected_gap_t - costs_t`

The model must use only information available at t.

If expected dividend is missing, stale, or not publicly available at t, the event overlay is DATA_NOT_READY rather than imputed.

## Required P0~P6 integration

Each event row must preserve:

- P0 price signal
- P1 price location
- P2 extension/chase
- P3 leadership / RS / breadth
- P4 macro / cross-asset
- P5 attribution evidence
- P6 fundamentals

The event overlay may tighten permission but may not override a failed hard risk gate.

P6 remains DATA_NOT_READY until archival PIT fundamentals are available.

## Controls

At minimum compare:

1. P0~P6 without dividend event overlay.
2. Same dates with dividend overlay.
3. Entry before event announcement versus after event announcement.
4. Entry 1/2/3/5 sessions before ex-date.
5. Ex-date control.
6. Non-dividend matched controls with similar price shock / market regime where available.

## Outcomes

Report 1D / 5D / 20D / 60D and the existing long horizons where data permits:

- total return including realized dividend
- price return excluding dividend
- dividend contribution
- positive rate
- mean / median return
- worst return
- MAE / post-entry drawdown
- probability of losing more than net dividend
- probability of recovering the net dividend gap within 1/5/20 sessions
- trigger frequency
- incremental lift versus P0 baseline
- false positives / misses only after a pre-registered classification target is defined

## Falsification

The event overlay is rejected for promotion if, on OOS/walk-forward data:

- dividend-adjusted total return does not improve versus the no-overlay control;
- losses greater than the net dividend are not reduced;
- performance depends materially on the final confirmed dividend rather than the information available at entry;
- results disappear after costs/slippage;
- event-specific gates only improve in-sample results.

## Fail-closed

No live BuyStrength or MarketScore modification occurs from this study.

Status transitions remain:

`RESEARCH → VALIDATED → SHADOW → OPERATIONAL`

Only after strict PIT, event-vintage integrity, OOS/walk-forward robustness, costs, and falsification are GREEN.
