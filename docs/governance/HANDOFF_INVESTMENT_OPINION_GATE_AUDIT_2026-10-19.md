# Handoff — Investment Opinion Availability & Decision-Gate Audit

Updated: 2026-10-19 (KST)

## Current conclusion

- Audit status: MIXED_FAILURE.
- Repository: https://github.com/chayobi03-cyber/investment
- Base audited: main commit c30f3f0b7e2ed84f4b668b4778d57e51fc1b5312.
- Audit issue: #35 — Separate investment opinion output from buy permission and execution gates.
- Existing blockers: #27 (market monitor return horizons/freshness), #31 (deterministic market-check/HOTL persistence), draft PR #30 (proposed #27 remediation).
- Branch for audit artifacts: audit/investment-opinion-gates-2026-10-19.
- Live controls remain BUY_ALLOWED=false, EXECUTION_ALLOWED=false, PROMOTION=DISABLED.
- No runtime code, threshold, weighting, or live permission changed in the audit.

## Verified facts

1. DecisionGateAgent only emits DATA_NOT_READY, BLOCKED or RESEARCH_ONLY; BUY_ALLOWED and EXECUTION_ALLOWED are hard-coded false.
2. schemas/multi_asset_decision_v0.1.schema.json has no investment opinion, thesis, confidence, valuation, downside or reassessment fields.
3. The MultiAssetOrchestrator fans a PIT failure out to downstream agents, and DecisionAgent includes permission/evidence/source gate failures in the final status.
4. RiskAgent currently checks that MDD, MAE and stress_loss are non-null; it does not enforce numeric risk limits in that class, and concentration_ok defaults true.
5. MARKET_REGIME_ENGINE_V1.md describes two consecutive observations for a regime transition; RegimeAgent currently copies raw_regime directly to confirmed_regime.
6. Issue #27 remains open and the main branch's poll.py still uses adjacent 5-minute bars for change_pct while aggregate freshness uses the newest timestamp across all symbols.
7. PR #30 is draft/open/unmerged. Its tests, backtest and test-history check runs report success on the PR branch, but this does not fix main.
8. Issue #31 remains open and calls for deterministic market-check execution and inspectable HOTL persistence.
9. All historical gate pass rates, opportunity frequencies/durations and 2000/2008/2020/2022/2025-2026 replay performance remain NOT_COMPUTABLE from this audit.

## Non-negotiable controls

- Keep BUY_ALLOWED=false, EXECUTION_ALLOWED=false and PROMOTION=DISABLED.
- Keep EXPERIMENT_B0_ENGINE separate from BUY_TRIGGER_B0_NO_BUY.
- Do not loosen data-quality, PIT, source-provenance, conflict, hallucination, risk or HOTL controls to increase opinion coverage.
- Do not claim an asset is cheap merely because price fell.
- Treat unknown portfolio/ETF look-through exposure as UNKNOWN, never zero.
- Do not run strategy-performance promotion until M1 Data Integrity is GREEN.

## Next actions

### P0 — Verify and merge the Issue #27 remediation candidate
- [ ] Review PR #30 relative to current main; resolve merge-base drift.
- [ ] Confirm 5m, validated 15m and prior-session return horizons are distinct.
- [ ] Confirm freshness is per instrument and required group with session-aware rules.
- [ ] Run 2026-10-12 discrepancy, fresh-FX/stale-Korean series, missing prior close, session-boundary, and quote-conflict fixtures.
- [ ] Verify the tests run on the eventual merge commit; keep #27 open until its acceptance criteria pass.

### P1 — Implement versioned Opinion Contract v0.2
- [ ] Keep v0.1 immutable; add opinion_status, opinion_class, thesis, evidence/counter-evidence, confidence, valuation state, downside scenario, validity and reassessment fields.
- [ ] Ensure permission=false and execution=false can coexist with OPINION_READY / OPINION_PROVISIONAL.
- [ ] Ensure missing thesis-critical evidence returns OPINION DATA_NOT_READY; never manufacture a directional opinion.
- [ ] Add tests for quote-only failure, long-term-fundamental evidence failure, a macro permission block, concentration block, future available_at and source conflicts.
- [ ] Do not change the global buy/execution locks or thresholds.

### P2 — Implement quantitative risk-limit contract
- [ ] Define a separately versioned source of truth for max MDD/MAE/stress-loss/concentration limits.
- [ ] Require threshold version, measured value, comparison result and blocker code.
- [ ] Remove implicit concentration_ok=true when the required portfolio input is missing.
- [ ] Add pass/fail/boundary/missing-threshold tests. Do not select thresholds based on OOS results.

### P3 — Fix regime-confirmation parity
- [ ] Reconcile code with MARKET_REGIME_ENGINE_V1.md.
- [ ] Implement two-observation persistence or set confirmed_regime unknown when history is insufficient.
- [ ] Test stress override independently and measure false transitions/response delay.

### P4 — Build point-in-time replay and A–D comparison
- [ ] Freeze the main baseline and data/config hashes.
- [ ] Run same point-in-time observations, costs and fill conventions for baseline and Experiments A–D.
- [ ] Cover 2000, 2008, 2020, 2022 and available verified 2025–2026 periods; report gaps without proxy substitution.
- [ ] Compute opinion coverage, gate pass rates, joint-gate windows, lead time, MDD, CVaR/ES, stress loss, turnover, cash drag, costs and benchmark comparisons.
- [ ] Keep results NOT_COMPUTABLE until the data contracts pass. No arbitrary opinion-coverage or buy-rate target.

## Case status carry-forward

- TSMC: observed 2026-10-16 close $412.61; two-share notional $825.22, about KRW 1.096M at the 2026-10-19 FX close of KRW 1,328.72/USD, before fees and spread. Q3 earnings evidence is positive, but valuation and full semiconductor factor concentration were not computed. Treat opinion as provisional / WAIT; permissions false.
- SK hynix: reported historical buy KRW 1,271,000 and sale KRW 1,302,000 gives KRW 31,000 gross or ~2.44% before costs. This is one outcome, not evidence of strategy efficacy. Recent source price observations disagree; reconcile before order-time decision.
- 2026-10-12 market monitor: KOSPI -0.377% reported vs reported session close -3.65%; source Issue #27 shows wrong return horizon and false-green freshness. Block buys until fix verified.

## Git and lesson learned

- Audit issue #35 is open.
- Persist report and this handoff on branch audit/investment-opinion-gates-2026-10-19.
- Submit the documentation in a review PR; do not merge direct to main.
- End-session lesson: a safe decision system needs two separate products: an evidence-backed opinion and an independently evaluated permission/execution result. Preserve valid analysis while refusing unsafe transactions; do not trade off data integrity for answer completeness.
- Resume using this handoff; first check the live state of Issues #27/#31/#35 and PR #30 rather than assuming any blocker is resolved.
