# Lessons Learned — Korea Layer Backtest

Date: 2026-09-02 KST

## Findings

1. The provisional KOSPI 6,000–6,750 entry zones are not stationary across the full KOSPI history. Historical validation must therefore use a scale-invariant representation such as drawdown from a rolling 252-trading-day high, while retaining the absolute zones only for the current index-level regime.
2. The first CI implementation depended on `FinanceDataReader`, but the package was not installable from the GitHub Actions Python 3.12 environment. The backtest runner was changed to direct public HTTP retrieval for reproducibility.
3. Stress Convergence v0.2 cannot be honestly represented as a complete 0–24 score unless Fed near-term hike probability and AI-financing histories are reconstructed. The Korea backtest therefore labels its current implementation as a **v0.2 topology proxy** and reports data coverage rather than imputing unavailable axes.
4. KOSPI entry-threshold validation and Stress Convergence validation are separate but linked tests: entry bands measure forward risk/return quality; L2 proxy measures whether the same entry state occurs with preceding systemic stress and its FP/FN/lead-time properties.

## Rule updates

- Do not compare raw KOSPI index-level thresholds across distant historical regimes.
- Never impute missing Stress Convergence axes merely to obtain a complete score.
- Report absolute-zone results and normalized drawdown-zone results separately.
- Treat the Korea Layer as downstream confirmation; do not allow it to overwrite the global Stress Convergence gate.

## Next gate

Promotion requires the executable backtest to complete with data-coverage evidence and then a separate extension for Korea-specific foreign flow, semiconductor/export, and breadth variables. No capital-allocation rule is promoted from the current run.
