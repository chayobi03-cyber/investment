# Investment Next Session Handoff — 2026-08-20 Cold Project Audit

## Session Purpose

The next session is an **Investment project cold-audit session**, not a new implementation session.

Primary goal:

> Determine how close the Investment project is to its actual capital-preservation objective and identify the highest-priority work required to reach the next meaningful outcome.

## Canonical Project Context

- Top-level project: `investment`
- Repository: `chayobi03-cyber/investment`
- Canonical branch: `main`
- Supporting repositories/components must be treated as supporting scope unless explicitly promoted to top-level project scope.

## Canonical Objective

The repository describes the program as a capital-preservation-oriented public-equity investment system. Its research principle is to optimize for long-term capital survival and risk-adjusted compounding before maximizing raw returns.

## Current Milestone Chain

```text
M0 Risk Contract
   ↓
M1 Data Integrity
   ↓
M2 Portfolio Risk Engine
   ↓
M3 Asset Allocation Backtest
```

No strategy should be promoted past an upstream milestone while the upstream gate is not GREEN.

## Cold Audit Scope

The audit must produce an evidence-backed view of:

1. Project objective
2. Required outcomes
3. Milestones and acceptance criteria
4. Workstreams
5. Complete task inventory
6. Task-to-outcome traceability
7. Implemented versus tested versus primary-evidence-verified work
8. Current milestone state
9. Blockers, risks, dependencies, and governance debt
10. Scope drift or unnecessary work
11. Priority-ranked action items
12. Recommended next milestone

## Required Status Model

For each major task or capability, distinguish:

```text
DEFINED
IMPLEMENTED
TESTED
PRIMARY-EVIDENCE-VERIFIED
PROMOTED
```

Do not infer a later state from an earlier state.

## Cold-Audit Questions

### Objective

- What exactly is the Investment system being built to achieve?
- Which outcomes represent capital-preservation success rather than merely research progress?

### Milestones

- Does each milestone have a measurable outcome?
- Is the current milestone actually the highest-value next bottleneck?
- Are any milestone definitions inherited from supporting infrastructure rather than Investment requirements?

### Tasks

- Which tasks directly contribute to Investment outcomes?
- Which are prerequisites?
- Which are supporting infrastructure?
- Which are discretionary optimization?
- Which should be stopped or deferred?

### Evidence

- What claims are backed by primary execution evidence?
- Which states exist only in documentation/session state?
- Where does the evidence chain stop?

### Risk

- What is the dominant current risk: data integrity, portfolio-risk logic, tooling, evidence, governance, or scope?
- What dependency blocks meaningful progress?

## Supporting Component Rule

AgentFactory and other supporting components must be evaluated by their contribution to Investment outcomes:

```text
Investment Objective
 -> Investment Outcome
 -> Investment Milestone
 -> Supporting Capability
 -> Task
 -> Acceptance Criterion
 -> Evidence
```

Do not audit a supporting repository as though its local product objective were the top-level Investment objective.

Do not classify supporting work as contamination merely because its terminology differs from Investment terminology. Ownership and objective contribution must be established first.

## Forbidden During Cold Audit

- jumping directly into a new major milestone implementation;
- declaring GREEN from documentation alone;
- treating implementation volume as project progress;
- redefining Investment milestones based on a supporting repository's local roadmap;
- promoting strategies without the required upstream evidence;
- changing canonical objectives merely to fit current implementation.

## Required End State

Finish the audit with one of:

- `PROJECT_ALIGNED`
- `PROJECT_REALIGNMENT_REQUIRED`
- `REVIEW_REQUIRED`
- `BLOCKED`

Use `PROJECT_ALIGNED` only when objective, outcomes, milestones, tasks, evidence, and next actions are mutually consistent.

## Closing Sequence

```text
Project Identity Check
 -> Objective Review
 -> Outcome Definition
 -> Milestone Audit
 -> Workstream / Task Audit
 -> Evidence-State Audit
 -> Risk / Dependency Audit
 -> Scope / Governance Audit
 -> Gap Analysis
 -> Priority Ranking
 -> Recommended Next Milestone
 -> Git Evidence
 -> Session Handoff
```
