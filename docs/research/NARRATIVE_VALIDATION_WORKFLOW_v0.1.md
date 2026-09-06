# Narrative-to-Evidence Validation Workflow v0.1

**Project:** Investment — Capital Preservation Research  
**Status:** AMENDED FROZEN CONTRACT v0.1  
**Effective date:** 2026-09-04  
**Amendment date:** 2026-09-07  
**Purpose:** Convert market/news narratives into falsifiable hypotheses and validate them against independent sources, cross-asset evidence, fixed time windows, and flow-attribution controls before they can influence investment or stress-detection decisions.

---

## 1. Purpose and Scope

This workflow is an **external narrative validation layer** for the investment research system.

It does **not** treat news volume, analyst consensus, or a persuasive article as evidence of a crisis. News creates a hypothesis to test. Market data and independent evidence determine whether the hypothesis survives.

### Core principle

> **Narrative is an input to investigation, not evidence of confirmation.**

### Primary use cases

- Validate a market article or analyst thesis.
- Find independent analyses making a similar claim.
- Search explicitly for counterarguments and falsifying evidence.
- Determine whether apparently similar articles are genuinely independent.
- Align narrative claims with observable market data.
- Separate discretionary investor flow from mechanical / non-discretionary flow before interpreting capital-flow signals.
- Feed validated evidence into the existing stress-convergence framework.

### Out of scope

- Direct trade execution.
- Portfolio position sizing.
- Replacing authoritative market/economic data with news articles.
- Declaring a financial crisis solely from narrative strength.
- Treating investor-category flow statistics as pure investor sentiment without attribution checks.

---

## 2. Workflow Contract

Every execution MUST follow this sequence:

```text
INPUT ARTICLE / CLAIM
        ↓
1. CLAIM EXTRACTION
        ↓
2. HYPOTHESIS FORMULATION
        ↓
3. INDEPENDENT SOURCE SEARCH
        ↓
4. SOURCE INDEPENDENCE CHECK
        ↓
5. COUNTER-EVIDENCE SEARCH
        ↓
6. MARKET-EVIDENCE VALIDATION
        ↓
7. MECHANICAL-FLOW ATTRIBUTION CHECK
        ↓
8. CROSS-ASSET CONVERGENCE CHECK
        ↓
9. TIME-WINDOW ALIGNMENT
        ↓
10. NARRATIVE / EVIDENCE SCORING
        ↓
11. EXISTING STRESS-DETECTOR COMPARISON
        ↓
12. FINAL CLASSIFICATION
        ↓
13. LESSON LEARNED / RULE CANDIDATE
```

### Mandatory separation

The workflow MUST output three independent judgments:

1. **Narrative Strength** — how strongly the narrative is being expressed by credible, independent sources.
2. **Evidence Strength** — how strongly observable data support the causal claim.
3. **Crisis Confirmation** — whether actual broad financial stress is confirmed.

These values MUST NOT be collapsed into a single “risk” label.

---

## 3. Claim Extraction Contract

From the input article, extract **3–7 testable claims**.

Each claim MUST contain:

- `claim_id`
- `claim_text`
- `claim_type`
- `causal_chain`
- `expected_market_implications`
- `falsifier`
- `time_horizon`

### Claim types

- `macro`
- `monetary_policy`
- `rates`
- `fx`
- `credit`
- `liquidity`
- `equity_valuation`
- `commodity_energy`
- `capital_flow`
- `geopolitical_transmission`

### Example

```yaml
claim_id: C01
claim_text: "Higher Japanese government bond yields may reduce Japanese demand for overseas bonds."
claim_type: capital_flow
causal_chain:
  - JGB yield rises
  - relative domestic return improves
  - overseas bond attractiveness falls
  - Japanese foreign-bond demand declines
expected_market_implications:
  - JGB yields ↑
  - USD/JPY ↓ or yen strengthens
  - foreign bond demand ↓
  - US long-end term premium may ↑
falsifier: "Japanese foreign-bond demand remains strong despite materially higher JGB yields."
time_horizon: 1M-6M
```

---

## 4. Search Contract

For every material claim, execute four search classes.

### A. Direct confirmation search

Search for independent sources supporting the claim.

Example:

```text
Japan JGB yields repatriation US Treasury demand
Japan bond yields foreign bond selling yen
```

### B. Mechanism search

Search for the causal mechanism itself rather than the article wording.

Example:

```text
JGB yield differential Japanese investors foreign bonds
yen carry trade funding cost risk assets
Treasury term premium foreign demand fiscal supply
```

### C. Counter-evidence search — REQUIRED

Every material claim MUST have an explicit falsification search.

Example:

```text
JGB yield rise limited impact US Treasury demand
Japan repatriation argument counter evidence
yen carry unwind why not systemic crisis
```

### D. Historical analogue search

Search for prior episodes with similar causal structure.

Example:

```text
historical JGB yield rise Japanese repatriation global bonds
previous yen carry unwind market impact
2008 2020 2022 Treasury yield stress comparison
```

---

## 5. Source Hierarchy

Source quality is ranked as follows:

| Tier | Source | Default weight |
|---|---|---:|
| S1 | Central banks, government agencies, statistical agencies, Treasury | 5 |
| S2 | Reuters, Bloomberg, FT, WSJ and equivalent high-quality financial reporting | 4 |
| S3 | Bank / institutional research with identifiable methodology | 4 |
| S4 | Specialist financial/economic publications | 3 |
| S5 | General financial media | 2 |
| S6 | Individual commentary, blogs, social posts | 1 |

Source tier is **not** a truth score. It is evidence-quality metadata.

Official data sources should be preferred for numerical market/economic observations. News sources are primarily used for interpretation, expert commentary, and narrative discovery.

---

## 6. Source Independence Contract

Article count MUST NOT be treated as independent evidence count.

Two or more articles are considered **non-independent** when they substantially reproduce the same wire report, analyst note, press release, or original source without adding material independent evidence.

### Required fields

```yaml
source_id:
source_type:
source_tier:
publication_date:
primary_or_secondary:
independence_group:
original_source_if_known:
claim_supported:
claim_opposed:
new_evidence_added:
```

### Rule

> Ten articles repeating one Reuters report count approximately as **one underlying evidence event**, not ten independent confirmations.

---

## 7. Counter-Evidence Contract

Counter-evidence is mandatory and must be evaluated symmetrically.

For each claim, record:

- strongest supporting evidence
- strongest opposing evidence
- unresolved ambiguity
- what observation would falsify the claim

### Counter-evidence categories

1. **Mechanism failure** — causal link may not operate as proposed.
2. **Magnitude failure** — effect exists but is too small to matter.
3. **Timing failure** — effect occurs outside the claimed time window.
4. **Historical failure** — similar conditions previously did not produce the claimed result.
5. **Market-price failure** — actual prices do not confirm the narrative.
6. **Alternative explanation** — another mechanism better explains the observed move.

---

## 8. Market Evidence Contract

A narrative becomes evidence-bearing only when its expected implications can be compared with observable data.

### Default cross-asset groups

```text
RATES:
  US 2Y
  US 10Y
  US 30Y
  JGB 10Y / relevant Japanese tenors

FX:
  USD/JPY
  DXY

EQUITY:
  S&P 500
  Nasdaq
  relevant sector/index

CREDIT:
  HY OAS
  IG spreads
  relevant CDS when available

VOLATILITY / LIQUIDITY:
  VIX
  Treasury liquidity measures when available
  funding-market indicators when relevant

COMMODITY / MACRO:
  crude oil
  inflation expectations
  labor indicators
```

The analyst MUST NOT require every asset group for every narrative. Only causally relevant groups should be tested.

---

## 8.1 Mechanical / Non-Discretionary Flow Adjustment Contract

Investor-category flow statistics MUST NOT be interpreted as pure investor sentiment until material mechanical or non-discretionary flows have been identified and annotated.

### Typical mechanical-flow sources

- corporate share buybacks
- ETF creations/redemptions and passive rebalancing
- index reconstitution
- benchmark tracking flows
- scheduled corporate actions
- central-bank or sovereign operations when they enter the relevant market statistics
- forced or rule-based mandate flows

### Required fields

```yaml
mechanical_flow_adjustment:
  present: true
  flow_type:
  entity:
  scheduled_or_discretionary:
  expected_notional:
  execution_window:
  actual_notional:
  market_statistics_bucket:
  attribution_confidence:
  residual_unexplained_flow:
```

### Mandatory rules

1. Before using an investor-category flow as evidence of risk appetite, determine whether a material portion is mechanically generated.
2. Corporate buybacks MUST be separated from discretionary “other corporate investor” demand when the data permit.
3. A category such as `other_corporations` / `other_entities` MUST NOT be treated as a homogeneous sentiment signal.
4. If exact attribution is unavailable, mark the flow as **partially attributed / unresolved**, rather than assigning it entirely to discretionary demand.
5. Mechanical-flow adjustment changes the interpretation of the flow signal; it does not by itself create or confirm crisis status.
6. When a mechanical flow is large enough to plausibly mask underlying selling pressure, the execution MUST explicitly test the market with and without that flow.

### Canonical interpretation pattern

```text
reported investor-category flow
        ↓
identify mechanical / non-discretionary component
        ↓
attribute known component
        ↓
calculate residual discretionary flow
        ↓
interpret residual as the stronger sentiment signal
```

### Example

If:

```text
foreigners      -X
institutions    -Y
individuals     -Z
other entities  +A
```

and a known corporate buyback accounts for most of `+A`, the workflow MUST NOT conclude that `other entities` represent broad discretionary demand. The relevant question becomes whether the **residual flow after mechanical adjustment** remains materially negative or positive.

### Evidence-strength implication

Unadjusted material mechanical flow does not automatically subtract a fixed number of Evidence Strength points. Instead, it MUST be reported as an attribution limitation and the resulting conclusion MUST avoid treating the raw investor-category number as a clean sentiment measure.

---

## 9. Cross-Asset Convergence Contract

A narrative is considered **cross-asset supported** only when at least two causally distinct market observations are directionally consistent with the proposed mechanism.

### Example

Narrative:

```text
BOJ tightening
→ yen strengthens
→ carry economics deteriorate
→ global risk assets become vulnerable
```

Minimum useful evidence:

```text
USD/JPY ↓
+
JGB yield ↑
+
credible evidence of leveraged/carry positioning deterioration
```

A single asset move MUST NOT be described as cross-asset confirmation.

---

## 10. Time-Window Contract

All narrative validation MUST preserve the project's multi-horizon structure.

| Horizon | Purpose |
|---|---|
| 1D | Immediate market reaction / event detection |
| 1W | Short-term persistence |
| 1M | Medium-term regime development |
| 90D | Structural change |
| 1Y | Regime / secular change |

### Timing rule

A claim about a causal transmission is not confirmed merely because two events occurred at different dates.

The workflow MUST record:

```yaml
signal_start:
confirmation_start:
confirmation_end:
allowed_window:
time_alignment_status:
```

### Existing project rule compatibility

This workflow MUST NOT bypass the project's fixed early-warning → confirmation time-window rule. Narrative evidence can propose or strengthen a hypothesis, but only the existing validation framework can classify an actual stress confirmation.

---

## 11. Narrative Strength Score

Narrative Strength measures **quality and independence of the narrative**, not whether it is true.

Suggested 0–100 score:

```text
+20  high-quality primary / institutional source
+15  ≥3 genuinely independent credible sources
+15  mechanism independently discussed
+10  historical analogue identified
+10  specialist/institutional research support
+10  recent repeated discussion across independent channels
+10  clear, testable causal chain
-20  major credible counter-narrative
-20  evidence mostly derivative/repeated reporting
```

Score is capped to 0–100.

Interpretation:

| Score | Interpretation |
|---:|---|
| 0–29 | weak narrative |
| 30–49 | observable narrative |
| 50–69 | strong narrative |
| 70–84 | dominant/credible narrative |
| 85–100 | exceptionally strong narrative |

A high Narrative Strength score MUST NOT imply crisis confirmation.

---

## 12. Evidence Strength Score

Evidence Strength measures whether observed data support the mechanism.

Suggested 0–100 score:

```text
+20  primary/authoritative numerical evidence
+20  direct market-price confirmation
+20  ≥2 relevant cross-asset confirmations
+15  persistence inside the stated time window
+10  historical analogue supports mechanism
+10  independent institutional analysis
-20  strong contradictory market evidence
-20  alternative explanation is stronger
-15  timing does not align
```

Score is capped to 0–100.

Interpretation:

| Score | Interpretation |
|---:|---|
| 0–29 | unsupported |
| 30–49 | weak evidence |
| 50–69 | moderate evidence |
| 70–84 | strong evidence |
| 85–100 | very strong evidence |

### Mechanical-flow qualification

Where a material capital-flow indicator is used, Evidence Strength MUST include a note on whether the observed flow is:

- fully attributed;
- mechanically adjusted;
- partially attributed; or
- unresolved.

Raw flow totals with material unresolved mechanical components MUST NOT be described as clean investor-sentiment evidence.

---

## 13. Crisis Confirmation Contract

Narrative Validation MUST NOT create a new crisis definition.

Crisis Confirmation is imported from the project's existing stress-convergence framework.

Current architecture principle:

```text
Narrative
  ↓
Hypothesis
  ↓
Market Evidence
  ↓
Mechanical-flow Attribution Check
  ↓
Cross-Asset Convergence
  ↓
Persistence / Time Window
  ↓
Existing Stress Detector
  ↓
Crisis Confirmation
```

### Important distinction

```text
Narrative Strength ≠ Evidence Strength ≠ Crisis Confirmation
```

Examples:

```text
High narrative + weak market evidence
→ media/analyst concern, not confirmed stress

Moderate narrative + strong market evidence
→ potentially important market stress even if media attention is low

High narrative + high evidence + no crisis criteria
→ strong warning, not yet crisis

High narrative + high evidence + existing crisis criteria satisfied
→ crisis confirmation candidate
```

Mechanical-flow attribution does not replace the crisis gate.

---

## 14. Output Schema

The canonical result SHOULD conform to the following structure.

```yaml
workflow_version: "NARRATIVE_VALIDATION_WORKFLOW_v0.1"
execution_id:
execution_date:
input:
  source_title:
  source_url:
  publication_date:
  source_tier:
claims:
  - claim_id:
    claim_text:
    claim_type:
    causal_chain: []
    expected_market_implications: []
    falsifier:
    time_horizon:
sources:
  - source_id:
    source_type:
    source_tier:
    publication_date:
    independence_group:
    original_source_if_known:
    claims_supported: []
    claims_opposed: []
    new_evidence_added:
counter_evidence:
  - claim_id:
    strongest_support:
    strongest_opposition:
    unresolved_ambiguity:
    falsifier_status:
market_evidence:
  - indicator:
    observation_date:
    observation:
    direction:
    expected_direction:
    supports_claim: true
    source:
mechanical_flow_adjustment:
  present:
  flow_type:
  entity:
  scheduled_or_discretionary:
  expected_notional:
  execution_window:
  actual_notional:
  market_statistics_bucket:
  attribution_confidence:
  residual_unexplained_flow:
cross_asset:
  groups_checked: []
  convergence_count:
  convergence_status:
time_windows:
  - horizon:
    signal_start:
    confirmation_start:
    confirmation_end:
    allowed_window:
    status:
scores:
  narrative_strength:
  evidence_strength:
  crisis_confirmation:
  confidence_notes:
existing_stress_detector:
  status:
  agreement_or_disagreement:
  reason:
final_classification:
  narrative:
  evidence:
  stress:
  investment_relevance:
lessons_learned:
rule_change_candidate:
git_artifact:
  required: true
  path:
```

---

## 15. Fixed Prompt — v0.1

The following prompt is the canonical execution prompt. This amendment adds a flow-attribution control without changing the project's crisis definition or time-window semantics.

```text
You are executing NARRATIVE_VALIDATION_WORKFLOW_v0.1 for the Investment — Capital Preservation Research project.

Objective:
Convert the supplied market/news narrative into falsifiable claims and validate those claims using independent sources, counter-evidence, observable market data, mechanical-flow attribution, cross-asset convergence, and fixed time windows.

Rules:
1. Do not treat the article's conclusion as a fact.
2. Extract 3–7 testable claims.
3. For every material claim, identify the causal chain and an explicit falsifier.
4. Search for independent confirmation of the mechanism, not merely matching headlines.
5. Search explicitly for counter-evidence and alternative explanations.
6. Deduplicate derivative reporting. Multiple articles based on the same original source count as one underlying evidence event.
7. Prefer authoritative primary data for numerical claims.
8. Validate expected market implications using causally relevant cross-asset data.
9. Do not call one asset's movement cross-asset confirmation.
10. Evaluate timing using 1D, 1W, 1M, 90D, and 1Y horizons as appropriate.
11. Keep Narrative Strength, Evidence Strength, and Crisis Confirmation separate.
12. Do not declare a crisis solely from narrative strength or article count.
13. Use the existing project stress-convergence framework for crisis confirmation; do not invent a new crisis definition during narrative validation.
14. Clearly distinguish facts, sourced interpretations, hypotheses, and unresolved uncertainty.
15. If evidence is missing, report "not established" rather than infer it.
16. If sources conflict, preserve the conflict and explain which evidence has higher quality or relevance.
17. Before interpreting investor-category flow as sentiment, identify material mechanical/non-discretionary components and record the attribution status.
18. Corporate buybacks and other known mechanical flows MUST be separated from discretionary demand when the data permit.
19. If exact attribution is unavailable, label the flow as partially attributed or unresolved rather than treating the full category as discretionary demand.
20. If a mechanical flow is large enough to mask underlying selling/buying pressure, test the market with and without the identified mechanical component.
21. End with: (a) final classification, (b) implications for the investment research system, (c) lesson learned, and (d) whether a rule/schema change is justified.

Required output order:
A. Executive conclusion
B. Extracted claims
C. Causal mechanisms
D. Independent supporting sources
E. Counter-evidence / falsification
F. Market evidence
G. Mechanical-flow attribution
H. Cross-asset convergence
I. Time-window alignment
J. Narrative Strength score
K. Evidence Strength score
L. Existing stress-detector comparison
M. Crisis Confirmation status
N. Final classification
O. Lesson learned
P. Rule/schema change recommendation
Q. Artifact/Git recommendation

Use concise, evidence-linked reasoning. Never convert a plausible narrative into a confirmed event without market evidence.
```

---

## 16. Decision Matrix

| Narrative | Evidence | Crisis | Classification |
|---|---|---|---|
| Low | Low | No | Ignore / monitor |
| High | Low | No | Narrative only |
| Low | High | No | Market anomaly / investigate |
| High | Moderate | No | Warning / monitor |
| High | High | No | Strong warning |
| High | High | Yes | Crisis confirmation candidate |

The matrix is descriptive, not a replacement for the project's quantitative stress detector.

---

## 17. Example: JGB–Yen–Treasury Narrative

### Input narrative

```text
Rising Japanese yields may encourage repatriation,
strengthen the yen, reduce overseas bond demand,
and increase pressure on US long-end yields.
```

### Required validation

```text
JGB yield ↑
      ↓
relative Japanese return ↑
      ↓
Japanese overseas bond demand ↓ ?
      ↓
USD/JPY ↓ ?
      ↓
US long-end demand ↓ ?
      ↓
US 10Y / term premium ↑ ?
```

The workflow must separately verify every arrow.

If JGB yields rise and USD/JPY falls but US Treasury yields fall rather than rise, the first parts of the mechanism may be supported while the final transmission remains unconfirmed.

Therefore:

```text
Narrative Strength: potentially high
Evidence Strength: depends on each causal link
Crisis Confirmation: independent question
```

This example demonstrates why the workflow exists.

---

## 18. Integration with Stress-Convergence Research

The workflow is an **upstream hypothesis generator and evidence validator**.

Existing stress-convergence research remains the downstream quantitative gate.

```text
                 NEWS / RESEARCH
                       │
                       ▼
             NARRATIVE VALIDATION
                       │
            ┌──────────┴──────────┐
            ▼                     ▼
       SUPPORTING              COUNTER
        EVIDENCE               EVIDENCE
            │                     │
            └──────────┬──────────┘
                       ▼
                MARKET EVIDENCE
                       │
                       ▼
            MECHANICAL-FLOW CHECK
                       │
                       ▼
              CROSS-ASSET CHECK
                       │
                       ▼
                TIME-WINDOW CHECK
                       │
                       ▼
             EXISTING STRESS ENGINE
                       │
                       ▼
             INVESTMENT INTERPRETATION
```

This preserves the existing principle that rates-led stress can be an early warning while credit, labor, volatility, and other confirmation layers determine whether broad stress is actually emerging.

---

## 19. Falsification / Failure Modes

The workflow itself must be periodically falsified.

### Known failure modes

1. **Narrative echo chamber** — many sources repeat one original report.
2. **Selection bias** — search finds only articles matching the initial thesis.
3. **Hindsight bias** — historical examples are selected after observing the outcome.
4. **Causal overreach** — correlated moves are described as transmission mechanisms.
5. **Timing mismatch** — a distant earlier signal is incorrectly linked to a current event.
6. **Magnitude neglect** — statistically real but economically immaterial effects are treated as major risks.
7. **Regime mismatch** — historical relationships fail under a new monetary/fiscal regime.
8. **Price-confirmation bias** — one market move is interpreted without checking alternatives.
9. **Source-quality inflation** — a high-profile source is treated as proof rather than interpretation.
10. **Narrative-to-crisis leakage** — strong media concern directly changes crisis status without passing the existing quantitative gate.
11. **Mechanical-flow attribution error** — scheduled or rule-based corporate/passive flows are interpreted as discretionary investor conviction.
12. **Flow masking error** — a large mechanical bid/offer hides the direction of residual discretionary demand.

### Required defense

Every execution should identify which of these failure modes, if any, could materially affect the result.

---

## 20. Artifact and Git Contract

A completed research execution that materially affects the project's understanding of a risk narrative SHOULD produce a reproducible artifact.

Recommended structure:

```text
execution_id/
  input.md
  claims.yaml
  sources.yaml
  counter_evidence.yaml
  market_evidence.yaml
  result.md
  manifest.yaml
```

The canonical workflow contract remains:

```text
docs/research/NARRATIVE_VALIDATION_WORKFLOW_v0.1.md
```

### Versioning rule

- Changes to wording that do not change logic: patch documentation update.
- Changes to schema fields: minor version increment.
- Changes to scoring, source independence rules, time-window logic, or crisis-gate semantics: new workflow version and validation cycle.
- A **flow-attribution clarification** may be applied as a contract amendment only when it does not alter the crisis definition, scoring formula, or time-window semantics; such amendments MUST state the amendment date and rationale.

### Git rule

Do not modify the workflow contract silently during an execution. Record proposed changes separately, validate them, then update the contract with a traceable amendment.

This amendment records the 2026-09-07 lesson that material mechanical/non-discretionary market flows can distort investor-category interpretation. The amendment adds attribution controls while preserving the existing crisis gate, score formulas, source hierarchy, and time-window rules.

---

## 21. Lesson-Learned Rule

At the end of every material execution:

```text
Result
→ What was surprising?
→ What failed?
→ What was ambiguous?
→ Did the workflow encourage confirmation bias?
→ Did time-window logic hold?
→ Did source independence hold?
→ Did mechanical-flow attribution hold?
→ Is a rule/schema/prompt change justified?
→ Git artifact required?
```

A lesson learned becomes a permanent rule only after it is shown to improve reproducibility, falsifiability, or decision quality.

### 2026-09-07 lesson learned

A large investor-category flow can be mechanically generated by corporate actions such as share buybacks. Therefore, raw category flow MUST NOT be used as a clean proxy for investor sentiment until the mechanical component has been identified or explicitly marked unresolved.

---

## 22. v0.1 Amendment Statement

The baseline v0.1 contract remains the reference workflow. The 2026-09-07 amendment adds a **mechanical / non-discretionary flow attribution control** to prevent corporate buybacks and other rule-based flows from being misinterpreted as discretionary investor conviction.

The following remain unchanged:

- Narrative Strength definition and score.
- Evidence Strength definition and score formula.
- Crisis Confirmation definition.
- Existing stress-convergence gate.
- Source hierarchy and source-independence principle.
- Fixed early-warning → confirmation time-window compatibility.

The central invariant remains:

> **News can raise a hypothesis. Independent evidence can strengthen it. Cross-asset and time-aligned market data can validate it. Mechanical flows must be attributed before being interpreted as investor sentiment. Only the existing stress-convergence gate can confirm a crisis.**
