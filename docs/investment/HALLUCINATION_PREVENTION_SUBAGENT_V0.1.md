# Hallucination Prevention Sub-Agent V0.1

Date: 2026-09-26
Status: RESEARCH STRUCTURE — NOT LIVE

## Purpose

The Hallucination Guard is a separate control-plane agent. It does not select assets, forecast returns, or optimize thresholds.

It verifies whether claims used by the investment system are:

- explicitly typed as FACT, CALCULATION, or INFERENCE;
- supported by identifiable evidence;
- point-in-time eligible;
- scope-bounded;
- arithmetically consistent when a calculation is supplied;
- explicitly labeled when an inference is made;
- backed by verified supporting claims when inference is used;
- free of unresolved conflicts.

## Verification contract

Claim
  -> Claim Type
  -> Source / Timestamp / available_at
  -> PIT Eligibility
  -> Calculation Check
  -> Support Graph
  -> Conflict Check
  -> Verification Status

## Status

- VERIFIED
- UNSUPPORTED
- LOOKAHEAD
- CALCULATION_UNVERIFIED
- SCOPE_UNSPECIFIED
- CONFLICT_UNRESOLVED
- DATA_NOT_READY

Any non-VERIFIED claim blocks promotion of the related decision artifact.

## Anti-hallucination rules

1. No source = no factual claim.
2. available_at > decision_timestamp = hard block.
3. A current label may not be used as a historical fact without historical availability evidence.
4. Numerical results must be reproducible from declared inputs/calculation.
5. Inference must be labeled as inference and reference verified supporting claims.
6. Conflicting evidence must remain visible and unresolved conflict blocks promotion.
7. Scope must identify the asset, population, period, or decision context.
8. The Guard never converts an unsupported claim into a probabilistic "probably true" pass.
9. The Guard cannot override the Data/PIT gate.
10. BUY_ALLOWED=false remains independent and immutable.

## Relationship to Evidence Agent

Evidence Agent answers:

"Can I trace this field to evidence?"

Hallucination Guard answers:

"Does the claim itself remain valid under the evidence contract?"

Both gates are required.

## Current limitation

This deterministic v0.1 checks structured claims and evidence metadata. It does not independently establish the real-world truth of an arbitrary external statement. External source retrieval, source-quality ranking, semantic contradiction detection, and human-review escalation are later layers.
