# Investment Research Loop

**Version:** v1.0  
**Effective:** 2026-09-02

## Standard execution loop

All investment research should follow this sequence unless a task explicitly requires a different workflow:

1. **Hypothesis** — define a falsifiable claim and expected mechanism.
2. **Data** — identify the minimum data required, source, period, frequency, and quality constraints.
3. **Threshold** — convert the hypothesis into quantitative trigger levels where applicable.
4. **Backtest** — test historical behavior and report FP, FN, lead-time, coverage, and sensitivity where applicable.
5. **Falsification** — actively search for counterexamples, failure regimes, and alternative explanations.
6. **Action** — translate surviving evidence into explicit investment action levels, position rules, or monitoring rules.

## Session-close protocol

After the research loop, every material session must explicitly record:

- **Lesson Learned** — what changed in the evidence or understanding.
- **Rule Change** — whether an existing model/rule/threshold needs modification: `YES` or `NO`.
- **Git Commit** — whether reproducible evidence, methodology, results, or governance changes should be committed: `YES` or `NO`.

## Decision discipline

- A successful backtest is **not** sufficient evidence for deployment; falsification must follow.
- Do not tune thresholds solely to improve historical fit without documenting the mechanism and out-of-sample risk.
- When falsification invalidates a hypothesis, revise the hypothesis/mechanism rather than forcing the threshold to fit.
- Investment actions must remain traceable to the evidence and the rule version that produced them.
- Material research artifacts should be committed to Git so that conclusions are reproducible and auditable.

## Session close template

```text
Lesson Learned: <result>
Rule Change: YES / NO — <reason>
Git Commit: YES / NO — <artifact/reason>
```
