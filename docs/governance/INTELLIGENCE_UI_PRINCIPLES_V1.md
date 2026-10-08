# Investment Intelligence UI Principles v1

Date: 2026-10-09

## Context

OpenAI's October 7, 2026 Intelligent UI release demonstrates a shift from fixed application screens to interfaces composed around the user's immediate task. The relevant design ideas are:
- choose layout and interaction based on intent;
- combine text, visuals, controls, charts, and interactive components;
- progressively surface information as work proceeds;
- use an explicit component library rather than arbitrary UI generation.

Source: https://openai.com/index/gpt-6-for-everyone/

## Investment-system interpretation

The existing `mobile/` experience is an **Entry Monitor UI**, not the full Intelligence UI.

The investment system should use a layered model:

```
User intent
  -> Intelligence View / UI composition
  -> deterministic state + evidence objects
  -> Decision controls
  -> Entry detail
  -> Final DecisionGate
```

### Intelligence Home

The primary view should answer:
1. What is the current market state?
2. What changed since the previous state?
3. What is causing the change?
4. Which assets/sectors are affected?
5. What conditions would change the decision?

Core sections:
- Global Market Regime
- State Delta
- Trigger Exceptions
- Trend / Breadth / Vol-Risk / Rates-Liquidity / Cross-Asset
- Oil / FX / Gold / Geopolitics
- Causal chain
- Asset intelligence
- Evidence / provenance / PIT status
- Risk / conflict / hallucination controls
- Final DecisionGate state

### Intent-driven views

The same data should be composed differently depending on the task:
- Morning market check -> compact state + delta + exceptions
- Why did it change? -> causal chain + evidence
- Compare assets -> side-by-side matrix
- When can I buy? -> prerequisites + current distance-to-trigger + gate blockers
- Stress test -> scenario controls + risk outcomes
- Asset detail -> existing Entry Monitor UI

### Progressive rendering rule

Progressive UI is allowed for information gathering, but never for premature investment permission.

Safe sequence:
```
DATA/PIT readiness
  -> observed facts
  -> derived state
  -> evidence-backed explanation
  -> risk/permission checks
  -> DecisionGate
```

A provisional or partially generated screen must never imply BUY_ALLOWED=true or EXECUTION_ALLOWED=true.

### Critical separation

LLM/model-driven UI composition may decide:
- which panels are useful;
- ordering and density;
- whether a table/chart/form/diagram improves comprehension;
- how to explain already-computed evidence.

LLM/model-driven UI composition must not decide:
- market thresholds;
- risk limits;
- PIT eligibility;
- permission overrides;
- BUY_ALLOWED;
- EXECUTION_ALLOWED;
- final DecisionGate state.

Those remain deterministic, fail-closed controls.

## Architecture rule

The component library should be schema-driven.

Suggested high-level contract:

```
Intent
  -> ViewSpec
  -> ComponentSpec[]
  -> Evidence/State references
  -> deterministic renderer
```

This allows a future "Intelligence UI Agent" to compose the interface without giving it control over the investment decision plane.

## Repository implication

Keep the current Entry Monitor as an asset-level detail surface. Add an upstream Intelligence Home rather than replacing the existing monitor.

No investment threshold changes are implied by this UI rule.

No BUY/EXECUTE promotion is implied by this UI rule.
