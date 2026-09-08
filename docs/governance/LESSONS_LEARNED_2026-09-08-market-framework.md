# Lessons Learned — Market Decision Framework

Date: 2026-09-08

## What changed

The market-judgment work was upgraded from a list of indicators into a reproducible state-classification architecture:

`Market Data → Factor Scores → Market Score → Regime → Horizon Score → Buy Strength / Risk → Portfolio Action`

## Lessons learned

1. **Market direction is not market state.** A rising index can coexist with deteriorating breadth, volatility and credit conditions.
2. **Market and stock scores must remain separate.** The market engine answers whether the environment permits risk; the stock engine answers whether the individual asset is attractive.
3. **Time horizons require different market influence.** Long-term decisions should be less sensitive to daily market noise than short-term decisions.
4. **Market Score and Risk Score are not inverses.** A strong trend can coexist with elevated fragility.
5. **Composite weights are research baselines, not truths.** The initial 25/20/20/20/15 market weights must be validated and can be rejected.
6. **Normalization must be point-in-time.** Percentiles or z-scores calculated with future observations would create hidden look-ahead bias.
7. **Breadth needs a fixed universe.** Changing the market universe after seeing results changes the experiment.
8. **Stress needs an override path.** Composite scores can react too slowly to sudden multi-factor shocks.
9. **One-day regime flips are undesirable for operational use.** Raw regime and confirmed regime should be stored separately.
10. **Backtest success is insufficient.** OOS, walk-forward, parameter sensitivity, transaction costs, cross-market validation and multiple-testing controls are mandatory promotion gates.
11. **The strongest next experiment is incremental-value testing.** Add Trend → Breadth → Risk → Macro → Cross-Asset sequentially and measure whether each block adds independent information.

## Rule changes

- Treat the 5-factor market weights as `BASELINE`, not `VALIDATED`.
- Require explicit point-in-time availability metadata for every data series.
- Separate `State` outputs from `Outcome` measurements.
- Store `raw_regime` and `confirmed_regime` independently.
- Add `falsification_status` to every market-rule record.
- Record every tested parameter/specification for later data-snooping correction.

## Next research gate

Before connecting Market Score directly to portfolio buy-strength actions, complete:

`Experiment A: score monotonicity`
`Experiment B: regime separation`
`Experiment C: incremental value of each factor`

Only a passing result allows the horizon-weight and position-sizing experiments to proceed.
