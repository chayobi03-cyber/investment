# Lessons Learned — Project Boundary / Cold Audit

Date: 2026-08-20
Repository: `chayobi03-cyber/investment`

## 1. Session Lesson

The most important failure in the session was not a technical implementation error. It was a **project-context error**: the active conversation belonged to the Investment project, but analysis was temporarily redirected to the internal product objective of a supporting AgentFactory repository.

This produced an invalid audit because the repository/component under inspection was treated as the top-level product instead of as a component of the Investment research system.

## 2. Permanent Rules

### Rule 1 — Top-Level Project Context Is Authoritative

At session start, establish the top-level project explicitly.

```text
TOP_LEVEL_PROJECT
    -> CANONICAL_REPOSITORY
    -> ACTIVE_BRANCH
    -> CURRENT_MILESTONE
```

A supporting repository must not replace the top-level project as the unit of outcome analysis unless the user explicitly switches project context.

### Rule 2 — Component Scope Must Be Resolved Before Audit

When multiple repositories/components are involved, classify each as:

- top-level project;
- supporting component;
- external dependency;
- historical/reference source.

Do not infer project ownership from the name of the repository currently being inspected.

### Rule 3 — Objective Must Be Audited at the Correct Level

Project audits must start from the objective of the **top-level project**, not the local objective of a supporting implementation repository.

For Investment, the current top-level objective is capital preservation and risk-adjusted compounding for a public-equity research system. The current milestone gates are M0 Risk Contract, M1 Data Integrity, M2 Portfolio Risk Engine, and M3 Asset Allocation Backtest.

### Rule 4 — Do Not Reclassify Supporting Work as Contamination Without Ownership Evidence

A supporting component may legitimately contain domain-specific implementation required by the top-level project.

Therefore:

```text
different project vocabulary
    !=
project contamination
```

Contamination or scope drift requires evidence from project ownership, objective mismatch, repository governance, commit/file/hunk intent, or explicit source-of-truth rules.

### Rule 5 — Cold Audit Precedes Major Milestone Execution

Before entering or executing a major Investment milestone, audit:

```text
Project Objective
    -> Required Outcomes
    -> Milestones
    -> Workstreams
    -> Task Inventory
    -> Evidence State
    -> Gaps / Risks / Dependencies
    -> Priority-ranked Actions
    -> Recommended Next Milestone
```

The audit must challenge whether current work is actually contributing to the intended outcome.

### Rule 6 — Implementation Volume Is Not Progress

The following states must remain distinct:

```text
DEFINED
IMPLEMENTED
TESTED
PRIMARY-EVIDENCE-VERIFIED
PROMOTED
```

A large number of files, tests, contracts, or governance artifacts does not prove milestone completion.

### Rule 7 — Evidence State Must Be Evaluated Per Outcome

Each major task must be mapped to the outcome it is intended to establish and the evidence required to declare that outcome complete.

Documentation/state files are not substitutes for primary execution evidence when execution is being claimed.

### Rule 8 — Supporting Architecture Must Be Evaluated by Contribution to Investment Outcomes

For components such as AgentFactory, evaluate:

1. what Investment outcome the component supports;
2. which Investment milestone requires it;
3. what capability is actually implemented;
4. what evidence proves that capability;
5. whether further work is necessary now.

Do not allow supporting infrastructure to become a self-referential milestone system detached from Investment outcomes.

### Rule 9 — Major Milestones Require Objective-to-Task Traceability

Every planned task must be traceable through:

```text
Investment Objective
 -> Outcome
 -> Milestone
 -> Task
 -> Acceptance Criterion
 -> Evidence
```

If the chain cannot be established, classify the task as `REVIEW_REQUIRED` until clarified.

### Rule 10 — Governance Must Stay Layered

Investment governance is authoritative for the Investment project.

Supporting repositories may define local implementation contracts, but those contracts cannot redefine Investment objectives, milestone meaning, promotion criteria, or project state without an explicit Investment-level decision.

## 3. Current Cold-Audit Requirement

The next session is not an implementation session. It is an Investment project cold-audit session.

The required questions are:

- Are we solving the correct Investment problem?
- What outcomes must be true to consider the project successful?
- What is the current state of every milestone?
- Which tasks directly contribute to those outcomes?
- Which tasks are prerequisites, supporting infrastructure, or discretionary optimization?
- What has primary evidence and what is only declared state?
- Where are the current bottlenecks: technical, data, evidence, tooling, governance, or scope?
- What should be stopped, continued, deferred, or started?

## 4. Boundary Correction From 2026-08-20 Session

The session demonstrated that an analyst can incorrectly audit a supporting repository as though it were the top-level Investment project.

Preventive control:

```text
SESSION START
 -> identify top-level project
 -> identify canonical repository
 -> identify supporting repositories
 -> identify current milestone
 -> only then begin technical or governance audit
```

If the top-level project cannot be established unambiguously, do not perform a project-level milestone audit. Mark the state `REVIEW_REQUIRED`.
