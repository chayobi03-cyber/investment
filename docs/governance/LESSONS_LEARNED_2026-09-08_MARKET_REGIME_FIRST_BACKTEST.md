# Lessons Learned — 2026-09-08 Market Regime First Exploratory Backtest

## 1. Context

Following the concrete indicator/regime spec added to `MARKET_REGIME_JUDGMENT_FRAMEWORK_v1.0.md` (§4.1, §6.2), the user asked for the backtest to actually run against Korea, US, gold, crypto, and bond-market data. This session's own network egress blocks FRED/Yahoo Finance directly, so a script (`research/scripts/run_market_regime_v0.1_backtest.py`) and a new GitHub Actions workflow were added, matching the existing `run_v0.2.3_daily_panel.py` pattern.

## 2. What was run

Five CI iterations were needed to get a usable result, each driven by a real defect or data-coverage problem found and fixed in sequence:

1. First run: succeeded technically but only covered 2023-08-01 to 2026-09-08 (~3 years) — far short of the 10-20 year target.
2. Added per-series coverage diagnostics to find the cause.
3. Diagnostics showed the HY OAS credit-spread series (BAMLH0A0HYM2) was the culprit: both FRED's own `fredgraph.csv` direct download and the GitHub archive mirror `run_v0.2.3_daily_panel.py` had used previously now only return data from ~2023-08/09 onward — almost certainly an ICE BofA licensing restriction on FRED's public CSV endpoint (or a downstream effect of it on the mirror), not a bug in this project's fetch code.
4. Rather than requiring HY OAS for every date, `weighted_axis()` was changed to renormalize each axis's weights row-by-row over whichever components are actually available on a given date, so the ~30-year KOSPI/S&P 500/VIX/UST-yield history is not truncated by one late-starting series.
5. Final run covered **1996-12-11 to 2026-09-08 (9,342 trading days, ~30 years)**.

Before each push, the script was validated locally against synthetic (non-network) data, catching two real bugs before they reached CI: a Python conditional-expression operator-precedence bug that made the score-bucket table's top bucket ignore its lower bound, and a regime-label write-order bug where a lower-precedence rule (R3) could silently override a simultaneously-true, higher-precedence rule (R2).

## 3. Result

The score-bucket vs. forward-return relationship (framework §9) is **not monotonic** on this ~30-year sample, on both KOSPI and the S&P 500, at the 60-day and 120-day horizons specifically: the lowest Market Score bucket and the R6 (Panic) regime showed forward returns comparable to or stronger than the higher-score buckets/regimes, rather than weaker. Full detail and figures are recorded in the framework document, new §9.1.

This is exactly the condition the framework's own §11.1 falsification rule is designed to catch, and it is now marked TRIGGERED in that section.

## 4. Interpretation — not a simple "framework failed"

1. The pattern is consistent with well-known post-drawdown mean reversion / crisis-recovery behavior (2000-2002, 2008-2009, 2020 COVID, 2022), but this has **not yet been decomposed by episode** — a thin low-score/R6 bucket dominated by a handful of large V-shaped recoveries would produce exactly this pattern without meaning the axes are meaningless.
2. The R1/R6 boolean cut points in §6.2 are evidently miscalibrated for rarity: R1 fired on only 6 of 9,342 KOSPI days and 1 of 9,342 S&P 500 days in 30 years. Statistics built on that few observations are not reliable evidence either way.
3. This is a single full-sample run (§10 Level 3), not out-of-sample or walk-forward (Levels 4-5) — which the framework's own validation stack already says is insufficient on its own. This result is the concrete demonstration of why those later levels are required, not a reason to conclude anything final yet.
4. No weight was re-fit to this result. Per `INVESTMENT_RESEARCH_LOOP.md`'s explicit rule against tuning thresholds to fit historical results, the next steps are diagnostic (episode decomposition, OOS/walk-forward, R1/R6 recalibration), not a weight change.

## 5. Rule update

1. No existing hard rule changed.
2. `MARKET_REGIME_JUDGMENT_FRAMEWORK_v1.0.md`: new §9.1 recording the first real backtest result; §11.1 marked triggered with a cross-reference; three new P0 items added (episode decomposition, OOS/walk-forward before any weight revision, R1/R6 cut-point recalibration); two prior P1 items marked done with results linked.
3. The candidate Risk Gate mapping in §7 (R1 = full deployment, R6 = no deployment) remains explicitly unvalidated and is now further from promotion, not closer, pending the P0 work above.

## Session close

```text
Lesson Learned: A ~30-year exploratory backtest of the candidate Market Score/Regime spec shows a non-monotonic, partly-inverted score-bucket-vs-forward-return relationship at 60-120 day horizons on both KOSPI and the S&P 500 -- triggering the framework's own falsification rule 11.1. This is informative, not fatal: the pattern looks like crisis-recovery mean reversion concentrated in a thin, rarely-firing R1/R6 tail, and the correct response per the project's research discipline is episode decomposition and out-of-sample/walk-forward testing, not re-fitting weights to this same sample.
Rule Change: NO — no existing hard rule modified; framework document records the result and adds diagnostic next steps.
Git Commit: YES — first real quantitative evidence for this framework, material governance/research content.
```
