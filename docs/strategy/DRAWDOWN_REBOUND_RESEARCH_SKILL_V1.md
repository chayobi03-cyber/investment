# Drawdown Rebound Research Skill V1

- **Status:** PROPOSED / RESEARCH_ONLY
- **Version:** `drawdown-rebound-research-v1.0`
- **Scope:** Korean listed equities initially; extensible by market adapter
- **Decision posture:** Capital preservation; fail-closed
- **Permissions:** `BUY_ALLOWED=false`, `EXECUTION_ALLOWED=false`, `PROMOTION=DISABLED`
- **Related controls:** [Market Check Workflow V1](../market/MARKET_CHECK_WORKFLOW_V1.md), [Issue #27](https://github.com/chayobi03-cyber/investment/issues/27), [Issue #31](https://github.com/chayobi03-cyber/investment/issues/31)

## 1. Purpose

Research whether short-term rebound/normalization trades can produce a positive net expectancy during drawdowns in companies that independently qualify as long-term investment candidates. Long-term quality is a universe filter, never a buy signal or grant of trading permission.

This document defines a proposed skill contract. It is not proof of an executable skill, a validated strategy, or permission to trade. No thresholds, production engine settings, or existing approval rules are changed by this document.

## 2. Non-negotiable controls

1. Inherit all upstream permission and risk restrictions. Never override `BUY_ALLOWED=false`, `EXECUTION_ALLOWED=false`, `DATA_NOT_READY`, `BLOCKED`, or `RESEARCH_ONLY`.
2. Keep research signals, simulated fills, actual fills, and approved orders as separate record types.
3. Fail closed on missing, stale, conflicting, non-point-in-time, or horizon-mismatched critical data.
4. No averaging down to recover losses. Any scale-in must be specified before the first entry and stay within the original trade and portfolio risk budgets.
5. No threshold tuning or production promotion from a single attractive backtest, market episode, or small sample.
6. Cash is a valid outcome. If evidence is insufficient, output `NO_TRADE`.
7. A stop price is not a guaranteed fill. Model gaps, limit moves, halts, liquidity, spread, and slippage explicitly.

## 3. Separation of decisions

Evaluate the following independently and preserve the evidence for each:

- **Long-term eligibility:** company quality, current financial condition, valuation, governance, balance-sheet resilience, industry structure, and potential permanent impairment.
- **Drawdown classification:** market, sector, and instrument regime.
- **Trade signal:** one of the pre-registered short-term hypotheses below.
- **Trade feasibility:** entry/stop/target geometry, costs, liquidity, holding period, and portfolio risk.
- **Permission:** upstream authorization only; this skill cannot grant permission.
- **Outcome evaluation:** compare frozen prediction and plan with later realized or simulated results.

### Long-term eligibility labels

- `L1`: eligible for long-term candidate research.
- `L2`: conditional; requires specified evidence or tighter risk bounds.
- `L3`: suspected thesis/financial deterioration; exclude from ordinary rebound candidates pending review.
- `L4`: excluded or evidence insufficient.

Historical eligibility must use information available as of each simulated decision date. Current survivors or present-day financial statements must not be projected backward into earlier universes.

### Drawdown-state labels

- `D1`: orderly correction.
- `D2`: persistent downtrend.
- `D3`: capitulation / disorderly selloff.
- `D4`: stabilization attempt, not a confirmed bottom.
- `D5`: recovery evidence confirmed by multiple inputs.

Labels require versioned, testable definitions. They must not be assigned narratively after observing future outcomes.

## 4. Registered strategy hypotheses

Run A, B, and C as separate experiment IDs with identical data, cost, split, and reporting conventions. Do not select the winner retrospectively without recording the full comparison and multiple-testing risk.

### A — Oversold plus stabilization

Candidate evidence may include decelerating downside momentum, a failed or improving retest, price recovery with volume, RSI change, and relative-strength improvement. An oversold reading by itself is insufficient.

### B — Support-zone response

Define support from historical price/volume evidence available before the signal. Record the source window, price zone, invalidation, and distance to the next resistance. Support is a hypothesis, not a guaranteed floor.

### C — Recovery confirmation

Require a defined improvement in short-term high/low structure, recovery and hold of selected trend references, volume/flow confirmation where reliable, and relative strength versus market/sector. A later entry is acceptable when it improves evidence quality.

Each hypothesis needs a pre-registered trigger, invalidation, exit rules, maximum holding period, permitted instruments, parameter set, and reasons that disprove it. Unregistered variants remain exploratory and must not be mixed into confirmatory results.

## 5. Required multi-timeframe analysis

- **Monthly:** long-term structure, major turning zones, thesis impairment and permanent-loss risk.
- **Weekly:** intermediate trend, support/resistance, trend deterioration, and whether the trade is counter-trend.
- **Daily:** setup, volume/flow response, entry trigger, invalidation and exit management.

All three timeframes are mandatory for candidate evaluation. Missing or contradictory data yields `DATA_NOT_READY` or `BLOCKED`. Counter-trend trades require an explicitly documented risk adjustment or rejection; the skill must not invent universal D/W/M thresholds.

Signals must use only bars completed and available at the decision timestamp. A close-derived signal cannot be filled at that same close unless the backtest models a genuinely executable closing-auction order submitted before the applicable cutoff.

## 6. Market and instrument data contract

Preserve raw observations before deriving features. Each field should retain, when available:

`instrument`, `field`, `value`, `unit`, `currency`, `source_name`, `source_url`, `observed_at`, `published_at`, `retrieved_at`, `session`, `revision/vintage`, `quality_state`, `missing_reason`.

Required validations:

- verified prior regular-session close and matching return horizon;
- per-instrument and per-field freshness, never freshness inferred from the globally newest symbol;
- OHLC/volume/quote consistency and exchange session/timezone alignment;
- corporate actions, adjusted/unadjusted prices, dividends and splits handled consistently;
- point-in-time fundamentals, disclosures, earnings dates, and sector/universe membership;
- source conflict, stale data, missing baselines, impossible values, and provisional flows clearly flagged;
- Korean-market mechanics considered where relevant: tick sizes, daily price limits, volatility interruptions, trading halts, closing/opening auctions, liquidity, and settlement-related constraints.

Do not hardcode changing fees, taxes, or market rules as permanent constants. Version their source and effective date. When these inputs cannot be verified, show a bounded scenario or mark the result not ready.

## 7. Trade plan and sizing

Every candidate plan must specify:

- decision timestamp and reference price/source;
- trigger and valid entry range;
- invalidation and stop policy;
- first/second target and time stop;
- expected holding duration;
- estimated commissions, taxes, spread, slippage and market impact;
- gross and net reward/risk and expectancy assumptions;
- maximum quantity and capital-at-risk;
- portfolio overlap, sector/factor concentration, correlated downside and gap stress;
- conditions that cancel the setup.

Sizing must be risk-based, for example:

`quantity <= floor(risk_budget / (entry_to_stop_loss_per_share + estimated_round_trip_cost_per_share))`

Use the applicable tick size and feasible lot/quantity constraints after calculating the preliminary size. The formula is a sizing aid, not evidence that the stop will execute at its assumed price. If account cash, current positions, or risk budget is unknown, return variables/scenarios instead of fabricated quantities.

## 8. Backtest and falsification protocol

Before results are interpreted as evidence of an edge, require:

1. Frozen hypothesis, parameters, universe rules, timestamps, and data vintages.
2. Point-in-time universe and fundamentals; controls against survivorship, look-ahead, and revised-data leakage.
3. Realistic signal-to-order latency and fill assumptions; avoid same-bar fills that would not have been executable.
4. Market/sector regimes covering rising, falling, range-bound, high-volatility and shock periods.
5. Net results after effective-date-appropriate fees, taxes, spread, slippage, partial fills, limit moves and missed fills.
6. Chronological train/validation/OOS or nested walk-forward splits; never randomly shuffle time series.
7. Comparison against cash, same-stock buy-and-hold, same-period benchmark, and a pre-registered simple staggered-entry baseline.
8. Trade count, signal frequency, capacity/liquidity bounds, turnover, holding time, MAE/MFE, gaps, serial dependence and overlapping positions.
9. Maximum drawdown, tail/stress loss, consecutive loss runs, recovery time, concentration and capital tied up—not just win rate or CAGR.
10. Parameter sensitivity, adverse cost assumptions, block/bootstrap or other dependence-aware uncertainty analysis where appropriate, and an explicit accounting of all tested variants.

Report unsuccessful regimes, rejected trades, misses, losses and strategy variants. A positive point estimate alone does not prove a stable positive expectancy. If samples are too few or confidence intervals are too wide, output `INSUFFICIENT_EVIDENCE`.

Expected trade value must use consistent units:

`E[net P&L] = P(win) * avg_net_win - P(loss) * avg_net_loss`

If costs are not already included in avg_net_win/avg_net_loss, subtract expected costs exactly once. Never double subtract costs or report a point estimate as validated expectancy when the underlying sample is insufficient.

## 9. Output and state machine

Each run reports:

### A. Run status
- `as_of_kst`, market session, workflow/strategy versions and source coverage;
- market and drawdown labels with evidence;
- `DATA_QUALITY`, `BUY_ALLOWED`, `EXECUTION_ALLOWED`, `PROMOTION`, `DECISION_MODE`.

### B. Long-term eligibility
Ticker, `L1-L4`, evidence date, thesis risks, missing inputs, and short-term eligibility separately.

### C. Candidate plans
Ticker, strategy A/B/C, trigger, invalidation, stop, targets, holding period, net reward/risk, sizing status, evidence quality, and state.

### D. Explicit no-trade reasons
Data gap/conflict, continuing downside, weak reward/risk, cost/liquidity issue, event risk, fundamental impairment, portfolio concentration, or upstream permission.

### E. Portfolio stress
Trade loss at stop assumptions, gap stress, correlated positions, available verified cash/risk budget, and effect on total portfolio risk.

### F. Next action
One of: `OBSERVE`, `DATA_REPAIR`, `REASSESS_ON_TRIGGER`, `PAPER_TRADE`, `RISK_REDUCTION_REVIEW`, or `NO_TRADE`. `APPROVED_TRADE_REVIEW` may be shown only if an independent upstream approval exists; this skill cannot create it.

Suggested state precedence: critical data/permissions first, then feasibility, then signal. Critical evidence missing => `DATA_NOT_READY`; hard rule violation => `BLOCKED`; research-only evidence => `RESEARCH_ONLY`; insufficient sample => `INSUFFICIENT_EVIDENCE`; otherwise a signal can only become a paper-trade candidate, never execution authorization.

## 10. Immutable signal and HOTL outcome ledger

Write each initial hypothesis/plan as an immutable event. Append outcome/evaluation events without rewriting the original decision.

Record:
- stable run/trade/episode ID, as-of timestamp, strategy/version and market state;
- raw data references and source/vintage hashes when available;
- signal, contrary evidence, trigger, stop, targets, costs, expected value assumptions and permission state;
- simulated versus actual status, orders/fills, quantities, actual costs and realized result;
- MAE/MFE, exit reason, and forward 5/20/60-session outcomes;
- cash and benchmark counterfactuals;
- error cause: data quality, regime classification, signal timing, plan/exit, execution cost, fundamental change, or evaluation leakage;
- corrective action, falsification status, rule-change proposal and rollback reference.

Do not merge a paper trade into actual performance. Missing forward outcomes remain pending, not zero. Preserve the original forecast before observing the outcome.

## 11. Promotion gates

The proposal remains research-only until all applicable gates are evidenced:

- the upstream data-integrity and deterministic market-check blockers are remediated and regression-tested;
- the strategy has frozen specifications and reproducible artifacts;
- PIT, leakage, cost, fill, market-regime and OOS checks pass;
- results are robust to reasonable cost/parameter perturbations and do not depend on a single episode;
- independent risk review covers portfolio exposure, gap risk, limits and stopping criteria;
- an explicit, versioned human approval changes permissions outside this skill;
- rollback and monitoring are documented.

A research report, paper-trade result, successful CI run, or this file alone cannot change permissions or promote production settings.

## 12. Skill implementation boundary

Recommended component design:
1. **Orchestrator:** validates inputs and coordinates stages; does not calculate execution permission.
2. **Eligibility evaluator:** point-in-time fundamentals and structural-risk classification.
3. **Regime evaluator:** market/sector/instrument state with provenance.
4. **D/W/M technical evaluator:** completed-bar features only.
5. **A/B/C signal evaluators:** separate versioned hypotheses.
6. **Risk/feasibility evaluator:** trade plan, costs, sizing and portfolio stress.
7. **Backtest/evidence evaluator:** leakage checks, walk-forward, benchmarks and uncertainty.
8. **HOTL ledger writer/evaluator:** immutable initial event and appended outcome.
9. **Decision gate adapter:** read-only interface to existing permissions; no authority to loosen them.

Keep deterministic calculations in tested code, not natural-language prompt reasoning alone. The prompt/skill should orchestrate contracts and explain results; data validation, return horizons, sizing, backtest accounting and ledger writes need executable tests.

## 13. First implementation milestone

Start with offline/replay fixtures and paper-trade records; do not start with live order routing. Test, at minimum:

- stale Korean index + fresh USD/JPY never yields aggregate GREEN;
- a five-minute return is never labeled daily or fifteen-minute;
- close-derived signal cannot fill at an unavailable same-bar price;
- missing monthly or weekly input blocks a fully qualified candidate;
- a deteriorating fundamental/thesis state is not rescued by a large drawdown;
- costs are included exactly once;
- paper results cannot be reported as real fills;
- missing outcomes remain pending;
- research output cannot change `BUY_ALLOWED`, `EXECUTION_ALLOWED`, or `PROMOTION`.

## 14. Decision

**Recommendation: implement as an isolated research skill after establishing the executable contracts and resolving upstream data-integrity dependencies.** Save this specification as a proposal, not an active trading rule. The next deliverable should be a small deterministic evaluation interface plus fixtures/tests and a paper-trade ledger—not automated orders or threshold tuning.
