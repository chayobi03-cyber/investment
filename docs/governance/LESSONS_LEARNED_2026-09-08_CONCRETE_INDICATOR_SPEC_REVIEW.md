# Lessons Learned — 2026-09-08 Concrete Indicator/Regime Spec Review

## 1. Context

A third follow-up memo (after the original framework proposal and the DSR/PBO review) supplied a fully worked-out, executable version of the five-axis indicator construction: named components per axis, sub-weights, specific 0-100 transform cut points, and a boolean R1-R6 decision formula. This was reviewed and folded into `MARKET_REGIME_JUDGMENT_FRAMEWORK_v1.0.md` as new §4.1 and §6.2.

## 2. What was checked

- Citation quality of the memo's ~15 supporting links: almost all are SEO/blog-tier sites (profitma.com, mastermind-x.com, finwiz.io, deanfi.com, thetrading.tools, tapeboard.com, buildalpha.com, etc.), below this project's evidence bar (`INVESTMENT_RESEARCH_LOOP.md` §2). One (convextrade.com) is a live data snapshot (HY OAS level), not a methodology source.
- Cross-check against the axis-level academic/institutional anchors already established in the prior independent-research session (§1.2: NFCI, Estrella-Mishkin, Zaremba et al., Moskowitz/Ooi/Pedersen).
- Internal consistency: the memo's Macro/Rates axis used "10Y-2Y" only, which conflicts with the already-established correction that the NY Fed's own official model uses 10Y-3M.

## 3. Findings and actions

1. **The structure is genuinely useful** — it is the first version of this framework concrete enough to implement in backtest code (named indicators, explicit sub-weights, a literal boolean regime formula) rather than illustrative prose. Adopted as a new "v0.1 candidate specification" layer (§4.1, §6.2), not as validated rules.
2. **Every numeric cut point is kept as an explicitly-labeled untested candidate**, consistent with how this project already treated the DSR/PBO thresholds: none of VIX<=18, HY OAS<=250bp, the 60/50/40/20 Market_Score bands, or any other level in §4.1/§6.2 is authorized for a live decision before recalibration on this project's own trailing-percentile data and §10.6 sensitivity testing. A new falsification condition (§11.8) makes this explicit.
3. **10Y-2Y vs. 10Y-3M**: the memo's Axis D table used 10Y-2Y only; corrected in §4.1 to note both should be carried, with 10Y-3M given precedence per the NY Fed's own official model (already established in §1.2).
4. **The breadth axis sub-weight split** (25% to %-above-200D-MA, the largest single component) is directionally consistent with the independently-verified breadth literature (Zaremba et al.) treating broad participation as the dominant signal — noted as a plausibility check, not confirmation, since the specific split itself is untested.
5. Added a new P1 item: implement and backtest this concrete spec directly (both with the memo's hardcoded cut points and with this framework's own trailing-percentile transform substituted in), since it is the first piece of this framework specific enough to actually run.

## 4. Rule update

1. No existing hard rule changed.
2. `MARKET_REGIME_JUDGMENT_FRAMEWORK_v1.0.md`: new §4.1 (concrete candidate indicator construction) and §6.2 (concrete candidate boolean regime formula) added; new falsification condition §11.8; new P1 item for implementation/backtesting.
3. Framework validation status unchanged: still WORKING HYPOTHESIS. This session added executable specificity, not validation.

## Session close

```text
Lesson Learned: A concrete, code-ready indicator/regime specification is a useful addition even when its supporting citations are low-tier, as long as every numeric threshold is explicitly labeled a candidate and the spec is reconciled against previously-verified corrections (10Y-3M) rather than silently overriding them.
Rule Change: NO — no existing hard rule modified; framework extended with an explicitly-candidate implementation layer.
Git Commit: YES — governance/evidence-discipline record and framework amendment.
```
