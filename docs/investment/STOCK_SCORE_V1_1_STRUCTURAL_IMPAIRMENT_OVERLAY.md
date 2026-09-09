# Stock Score V1.1 — Structural Impairment Overlay

Date: 2026-09-10
Status: APPROVED OPERATING RULE

## 1. Purpose

Stock Score V1 measures opportunity across Long / Medium / Short horizons. However, a falling share price must not automatically be interpreted as a better entry point when the company's competitive position or earnings engine may be deteriorating.

This rule adds a separate `Structural Impairment` assessment above the existing V1 score without changing the frozen V1 horizon weights.

Core rule:

> **가격 하락 = 저평가 신호로 자동 해석하지 않는다. 먼저 구조적 훼손 여부를 확인한다.**

## 2. Separation from Existing Scores

The existing Long / Medium / Short scores remain unchanged.

`CompositeStockScore = V1 formula`

`StructuralImpairment = separate 0–100 risk score`

`AdjustedInvestmentScore` is not part of the frozen V1 baseline and must not be used as a validated model output until an OOS (out-of-sample) validation is completed.

Until validation, Structural Impairment is primarily a **ranking penalty / action gate**, not a new optimized weight.

## 3. Structural Impairment Dimensions

Evaluate the following dimensions using point-in-time evidence:

| Dimension | Question |
|---|---|
| Competitive Moat | 경쟁우위가 약해지고 있는가? |
| Product / Usage | 핵심 제품·서비스 이용이 구조적으로 밀리고 있는가? |
| Monetization | 사용량이 늘어도 매출/이익으로 전환되는 힘이 약해지는가? |
| Capex / Cash Flow | 경쟁 대응 비용이 커지면서 현금창출력이 구조적으로 약해지는가? |
| Ecosystem Displacement | 플랫폼·고객·개발자 생태계가 경쟁자 쪽으로 이동하는가? |
| Concentration / Dependency | 특정 제품, 고객, 지역, 공급망 또는 규제에 대한 구조적 의존성이 커지는가? |

## 4. Evidence Standard

Do not score structural impairment from price action alone.

Priority evidence:

1. Company filings, earnings releases, guidance and investor presentations
2. Primary operating metrics and disclosed usage/revenue data
3. High-quality independent research and industry data
4. Korean sources for local interpretation and cross-checking
5. Market price only as supporting evidence, not as proof of structural deterioration

The investment research workflow remains:

`US/global primary & high-quality analysis → Korean sources → conflicting-narrative cross-check → discard low-quality/recycled claims`

## 5. AI / Technology Competition Rule

For AI-exposed companies, do not use a simplistic model-vs-model ranking such as “ChatGPT better than Gemini”. Evaluate the economic mechanism:

`AI capability → adoption/usage → product displacement or retention → monetization → margin/cash flow → competitive position`

For a company such as Google/Alphabet, the relevant questions include:

- Is AI reducing or strengthening Search economics?
- Is AI usage translating into Search / YouTube / Cloud monetization?
- Is competitor adoption causing measurable traffic, query, customer or developer displacement?
- Is AI capex increasing faster than the resulting economic return?
- Is the ecosystem advantage strengthening or eroding?

A negative market reaction is not sufficient evidence of impairment, and a low valuation is not sufficient evidence of recovery.

## 6. Action Gate

Structural Impairment should be reported separately with the normal Stock Score.

| Structural state | Default treatment |
|---|---|
| Low / no evidence | No structural penalty; normal scoring applies |
| Emerging concern | Reduce conviction; require stronger entry evidence |
| Material deterioration | Downgrade action even when Stock Score is high |
| Severe / confirmed impairment | `매수 금지` until thesis is re-established |
| Evidence insufficient | `관망` rather than inventing a favorable score |

The exact numeric penalties remain unfrozen until validation.

## 7. Required Output Extension

Add these fields to live review output when the overlay is active:

`StructuralImpairmentScore, StructuralImpairmentState, StructuralEvidence, StructuralPenaltyApplied, StructuralReviewDate`

A ranking must distinguish:

`Opportunity Score` = how attractive the stock appears

from

`Structural Risk` = whether the underlying investment thesis may be deteriorating.

## 8. Lesson from 2026-09-10 GOOGL Review

GOOGL's price decline should not have been treated as a stronger buy signal solely because the entry price became cheaper. The correct sequence is:

`price weakness → investigate AI/search competitive mechanism → verify operating evidence → classify structural impairment → then decide whether valuation creates an opportunity`

This rule is now reusable across AI, semiconductor, platform, consumer and other disruption-sensitive sectors.

## 9. Validation Requirement

Before converting Structural Impairment into a fixed numerical weight or formula:

- freeze the evidence definitions;
- construct historical point-in-time observations;
- define explicit falsifiers;
- test whether the overlay improves downside protection without destroying opportunity capture;
- validate out-of-sample.

No weight optimization should be performed on the first OOS sample.
