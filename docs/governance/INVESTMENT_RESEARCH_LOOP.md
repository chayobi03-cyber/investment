# Investment Research Loop

**Version:** v1.1  
**Effective:** 2026-09-26

## Standard execution loop

All investment research should follow this sequence unless a task explicitly requires a different workflow:

1. **Hypothesis** — define a falsifiable claim and expected mechanism.
2. **Data Contract** — identify the minimum data, source, population/universe, period, frequency, PIT/availability requirement, freshness, and quality constraints.
3. **Threshold / State Contract** — pre-register thresholds, persistence, episode/re-arm rules, and action states before OOS testing.
4. **Data QA / PIT Gate** — fail closed on missing, stale, revised-after-decision, conflicting, or provenance-incomplete inputs.
5. **Backtest** — test historical behavior across predefined horizons and report FP, FN, lead-time, frequency, tail loss, MDD, and survival.
6. **Falsification** — actively search for counterexamples, failure regimes, false positives, and alternative explanations.
7. **Ablation / Incremental Value** — remove one factor cluster at a time and require evidence that added complexity provides incremental OOS value.
8. **Action** — translate surviving evidence into explicit states, position rules, or monitoring rules.
9. **Promotion Gate** — require OOS, walk-forward, sensitivity, execution-cost, provenance, and unresolved-risk checks before operational use.

## Decision architecture

The default architecture is:

```text
Market State
    ↓
Permission / Risk Constraint
    ↓
Asset or Price Opportunity
    ↓
BuyStrength / Action State
```

Market state must not be silently embedded twice into asset opportunity scoring.

For systems that expose both market and asset dimensions, keep:

- **MarketScore** — environment health/opportunity;
- **OpportunityScore** — asset/price evidence;
- **Permission** — whether risk conditions allow escalation;
- **ActionState** — the explicit state machine result.

A strong opportunity signal cannot override a failed permission gate.

## Episode discipline

Daily observations inside one continuous market episode must not be treated as independent trades.

Every event-driven research model must pre-register:

- episode start condition;
- episode end / re-arm condition;
- cooldown if applicable;
- staged-entry handling;
- outcome attribution.

## Session-close protocol

After the research loop, every material session must explicitly record:

- **Lesson Learned** — what changed in the evidence or understanding.
- **Rule Change** — whether an existing model/rule/threshold needs modification: `YES` or `NO`.
- **Git Commit** — whether reproducible evidence, methodology, results, or governance changes should be committed: `YES` or `NO`.

## Decision discipline

- A successful backtest is not sufficient evidence for deployment; falsification must follow.
- Do not tune thresholds solely to improve historical fit without documenting the mechanism and out-of-sample risk.
- When falsification invalidates a hypothesis, revise the hypothesis/mechanism rather than forcing the threshold to fit.
- Prefer staged model construction and ablation to uncontrolled factor accumulation.
- Investment actions must remain traceable to the evidence and the rule version that produced them.
- Material research artifacts should be committed to Git so that conclusions are reproducible and auditable.

## Crypto extension

Crypto research inherits all gates above.

Additional mandatory controls:

- BTC is the first validation asset; secondary assets require explicit promotion.
- Market Score, Opportunity Score, and Buy State remain separate.
- Derivatives data are treated as risk/positioning inputs, not automatic bullish factors.
- Funding/OI leverage overheating can restrict escalation.
- Multi-shock deterioration is a hard block until stabilization is demonstrated.
- B0-B4 state transitions require pre-registered persistence and episode rules.
- No leverage, margin, or automatic order execution is part of the baseline research engine.
- Crypto sleeve exposure must be modeled separately from total-portfolio exposure during strategy validation.

## Current research gate

For any strategy that lacks complete PIT history and forward outcomes:

```text
DATA_NOT_READY
```

is the valid system state.

## Session close template

```text
Lesson Learned: <result>
Rule Change: YES / NO — <reason>
Git Commit: YES / NO — <artifact/reason>
```
