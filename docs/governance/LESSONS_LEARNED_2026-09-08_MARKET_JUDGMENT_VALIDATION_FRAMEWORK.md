# Lessons Learned — 2026-09-08 Market Judgment & Validation Framework Research

## 1. Context

A research memo proposed formalizing how this project defines "market state" (beyond a single price/index move) and how any such market-state score should be validated before being allowed to influence capital deployment. The result is `docs/research/market/MARKET_REGIME_JUDGMENT_FRAMEWORK_v1.0.md`.

## 2. Key conclusions

1. **Market direction and market state are different questions.** "Did the index rise?" is not the same question as "what environment is it rising in?" — trend, breadth, volatility/risk, rates/liquidity, and cross-asset flow must be read jointly.
2. **Stock-level and market-level scoring must stay separate**, then be blended with horizon-dependent weights (long-term more stock-weighted, short-term more market-weighted), rather than combined into one undifferentiated score or a simple multiplication.
3. **A single historical backtest is not evidence of a working rule.** This project already holds that discipline (`INVESTMENT_RESEARCH_LOOP.md`); the memo adds concrete mechanics for out-of-sample testing, walk-forward validation, parameter-sensitivity sweeps, transaction-cost realism, cross-market replication, and data-snooping correction (Reality-Check/SPA-style, optionally Deflated Sharpe Ratio and PBO/CSCV for advanced rigor).
4. **A rule's validation depth should be tracked and reported alongside its score.** A "Market Score = 82" that has only cleared economic logic and one backtest is not the same claim as one that has cleared out-of-sample and walk-forward testing; the framework introduces a separate Rule/Validation Confidence Score (0-100) for this.
5. **"Prediction" and "state judgment" must be kept separate.** The framework is built to say "this looks like a Risk-On environment," not "the price will rise" — and to test how existing strategies have historically performed in each state, rather than forecasting price directly.
6. **Every proposed rule needs a predeclared falsification condition**, not just a success story to point to after the fact.
7. **The new Market Regime (R1-R6) layer must be reconciled with, not merged into, the existing Stress Convergence three-state system** (Early Warning / Tightening State / Crisis Confirmation). They measure related but distinct things; systematic disagreement between them is itself a falsification signal for one or both.

## 3. What was explicitly NOT done

- No indicator, threshold, weight, or regime boundary in the new framework was backtested or validated in this session. All figures in the document are stated as candidates pending the P0/P1 work items.
- No connection was made yet to the live Buy Intensity or Portfolio Allocation staging rules; the framework only specifies how that connection would work once validated.
- No live market data was pulled or interpreted as part of this research task.

## 4. Immediate next steps (see framework §12 for full list)

- P0: freeze the concrete indicator set and data sources for the five axes.
- P1: run the score-bucket vs. forward-return backtest on at least one long-history market.
- P1: cross-check Market Regime labels against existing Stress Convergence window results once historical Market Regime output exists.

## Rule update

1. No existing hard rule (Buy Intensity, Portfolio Allocation staging, Stress Convergence three-state system) is changed by this session.
2. A new candidate methodology document is added: `docs/research/market/MARKET_REGIME_JUDGMENT_FRAMEWORK_v1.0.md`, status WORKING HYPOTHESIS — NOT YET VALIDATED.
3. This candidate framework may not be used to size or trigger a real trade until it clears at minimum Levels 1-3 of its own validation stack (economic logic, statistical relationship, historical backtest), per `INVESTMENT_RESEARCH_LOOP.md`.

## Session close

```text
Lesson Learned: Market state requires a 5-axis joint read (trend/breadth/risk/rates-liquidity/cross-asset), stock and market scores must blend with horizon-dependent weights rather than multiply, and no such rule may size capital before clearing an explicit out-of-sample / walk-forward / parameter-sensitivity / data-snooping validation stack — a single backtest is not sufficient.
Rule Change: NO — a new candidate framework was added; no existing hard rule was modified.
Git Commit: YES — new methodology/governance documents.
```
