# Handoff — Investment Drawdown Rebound Research

Updated: 2026-10-16

## Current status

- Strategy specification exists: docs/strategy/DRAWDOWN_REBOUND_RESEARCH_SKILL_V1.md
- Specification commit: 71a7d68946a437dcc6ff2641563245d591ba670a
- Implementation and strategy performance validation are pending.
- Mode: RESEARCH_ONLY
- Permissions remain: BUY_ALLOWED=false; EXECUTION_ALLOWED=false; PROMOTION=DISABLED.

## Goal

Research whether short-term rebound trades in stocks independently assessed as long-term investment candidates can produce positive net expectancy after realistic costs. Prioritize capital preservation, drawdown, tail risk, and reproducibility.

## References and blockers

- Market workflow: docs/market/MARKET_CHECK_WORKFLOW_V1.md
- Issue 27: https://github.com/chayobi03-cyber/investment/issues/27
- Issue 31: https://github.com/chayobi03-cyber/investment/issues/31

Issue 27 concerns invalid return horizons and cross-instrument freshness. Issue 31 requires deterministic market-check execution and verifiable HOTL persistence. Inspect their live status and actual code/tests before proceeding.

## Non-negotiable rules

1. Long-term eligibility is a candidate filter, not a buy signal.
2. Keep strategy A (oversold plus stabilization), B (support-zone response), and C (recovery confirmation) as separate experiments.
3. Daily, Weekly, and Monthly validation is mandatory.
4. Fail closed on missing, stale, conflicting, or non-point-in-time data.
5. Model realistic signal-to-order timing, fills, fees, taxes, slippage, price limits, halts, liquidity, and gap risk.
6. Use chronological OOS and walk-forward tests, benchmarks, uncertainty analysis, and multiple-testing controls.
7. Preserve initial hypotheses immutably; keep paper trades separate from actual fills.
8. Research results must not alter production thresholds or permissions.

## Next actions

### P0 — Upstream data integrity

- [ ] Fix and test separate 5-minute, validated 15-minute, and prior-session close-to-close returns.
- [ ] Validate freshness per instrument, field, and session; a fresh USD/JPY quote must not mask stale Korean market data.
- [ ] Test missing prior close, stale/conflicting quotes, provisional flows, and session boundaries.
- [ ] Verify Issue 31 deterministic workflow and inspectable HOTL persistence requirements.
- [ ] Keep all trading permissions disabled.

### P1 — Research interface

- [ ] Define versioned input/output schemas and provenance fields.
- [ ] Separate eligibility, regime, D/W/M analysis, A/B/C signals, trade feasibility/risk, backtest evaluation, and HOTL recording.
- [ ] Put deterministic calculations and validation in tested code, not prompt text alone.

### P2 — Regression tests

- [ ] Missing/stale D/W/M data blocks candidate qualification.
- [ ] A 5-minute return is never labeled daily or 15-minute.
- [ ] A close-derived signal cannot fill at an unavailable same-bar price.
- [ ] Fundamental deterioration cannot be overridden by drawdown size alone.
- [ ] Costs are counted exactly once.
- [ ] Paper trades are never reported as actual fills; missing outcomes remain pending.
- [ ] Research cannot change BUY_ALLOWED, EXECUTION_ALLOWED, or PROMOTION.

### P3 — Paper research

- [ ] Freeze A/B/C hypotheses and parameters before holdout evaluation.
- [ ] Use point-in-time universe and fundamentals.
- [ ] Compare with cash, same-stock buy-and-hold, a benchmark, and a preregistered staggered-entry baseline.
- [ ] Report net expectancy, MDD, tail/stress loss, consecutive losses, MAE/MFE, turnover, holding period, and uncertainty.
- [ ] Include losing periods and all tested variants; do not select only the best historical result.
- [ ] Require adequate samples and robustness to costs and parameter perturbations before claiming an edge.

### P4 — Promotion review

- [ ] Review reproducibility, OOS robustness, portfolio overlap, gap stress, risk limits, stop criteria, and rollback.
- [ ] Require explicit, versioned human approval outside this skill.
- [ ] Keep production promotion disabled until all upstream and strategy-specific gates pass.

## Required run report

Report KST as-of time, session, versions, sources, data quality, market regime, L1-L4 eligibility, A/B/C setup, entry/stop/targets/time stop, costs, net reward/risk, sizing status, no-trade reasons, portfolio stress, and next action.

Allowed next actions: OBSERVE, DATA_REPAIR, REASSESS_ON_TRIGGER, PAPER_TRADE, RISK_REDUCTION_REVIEW, NO_TRADE.

## State definitions

- DATA_NOT_READY: critical input missing, stale, conflicting, or not point-in-time verifiable.
- BLOCKED: a hard risk, integrity, or permission contract is violated.
- RESEARCH_ONLY: analysis is possible but trading is not authorized.
- INSUFFICIENT_EVIDENCE: sample size or uncertainty is inadequate.
- NO_TRADE: signal, expectancy, feasibility, or risk case is inadequate.

Never silently convert these states into trade permission.

## Lesson learned

Long-term quality justifies observation, not automatic entry. A strategy must demonstrate point-in-time correctness, realistic fills and costs, out-of-sample robustness, positive net expectancy supported by sufficient evidence, and acceptable portfolio tail risk. Documentation alone does not resolve upstream blockers.

## Resume instruction

Start at P0. Inspect current Issue 27/31 status and actual repository code/tests before implementation. Do not assume a blocker is resolved from documentation alone. Commit only reproducible, tested changes. At the end of each session, update this handoff with verified status, evidence/commit IDs, remaining blockers, lessons learned, and any justified rule-change proposal.
