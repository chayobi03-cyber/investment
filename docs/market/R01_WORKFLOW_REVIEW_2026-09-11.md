# R01 Workflow Review — 2026-09-11

## Scope

Review the R01 investigation workflow from research planning through source verification, methodology validation, PIT control, falsification, lesson learned, reporting, and Git evidence capture.

## Evidence basis

- REB 2025-07 official PDF raw capture verified in the current session.
- REB official survey documentation and publication schedule.
- National Data Office statistical change-approval notices for National Housing Price Trend Survey.
- National Data Office 2026.07 statistical error correction/publication management regulation.

## Findings

### 1. Release and methodology provenance must be independent

The 2025-07 report has a release identity, observation period, publication date, raw binary, and SHA-256. Separately, official change-approval notices show methodology changes, including sample frame, sample size, and index base changes. These are different provenance dimensions and must not be collapsed into one revision field.

### 2. Unknown is not equivalent to no revision

No explicit release-specific revision/vintage chain has been demonstrated for the 2025-07 report. The system therefore records `NOT_VERIFIED` rather than inferring `no_revision`.

### 3. PDF metadata is not release availability

PDF creation/modification timestamps are document-production metadata. They are not substitutes for the official publication/availability timestamp.

### 4. PIT needs explicit resolution handling

When only a publication date is defensible, the system must preserve date precision and use a conservative PIT policy. Exact timestamps must not be reconstructed from unrelated metadata.

### 5. Historical panels need methodology boundaries

A later index-base or sampling change can make a current R-ONE observation non-equivalent to the value visible in an earlier published report. Historical panels therefore require methodology version tags and structural-break boundaries.

## Workflow hardening requirements

```text
Research Planning
→ Source Registry
→ Evidence Capture
→ Release Provenance Gate
→ Methodology Provenance Gate
→ PIT Gate
→ Data Quality Gate
→ Panel Construction
→ Hypothesis Freeze
→ Threshold Preregistration
→ Backtest
→ Falsification
→ Lesson Learned
→ Human Review
→ Promotion/Rejection
→ Git Evidence Commit
```

Each stage emits a machine-readable result. Downstream stages are blocked when a critical upstream gate is unresolved.

## Automation rules

1. Automated validation may classify evidence but may not invent missing facts.
2. `PRIMARY_VERIFIED` is derived from all mandatory gates; it is never manually toggled.
3. Raw observations are append-only; revised records create new records.
4. Hypothesis/threshold changes after freeze create new versions and new run manifests.
5. Lesson learned may be auto-generated, but contract/rule changes require human review.
6. Git commit occurs when substantive evidence or workflow assets change; no empty/status-only commit is required.

## Current REB 2025-07 state

```yaml
release_provenance:
  official_source: verified
  observation_period: verified
  publication_date: verified
  raw_binary: verified
  sha256: verified
  revision_vintage: not_verified

methodology_provenance:
  change_evidence: verified
  methodology_version: recorded
  structural_break_risk: true

pit:
  available_at: "2025-08-18"
  precision: date
  exact_timestamp: not_verified
  executable_test: blocked

promotion:
  status: PROVISIONAL
```

## Lesson learned

The previous workflow correctly prevented premature backtesting but mixed two different questions: “Was this release changed later?” and “Did the statistical methodology change?” Separating these tracks makes provenance auditable and prevents false confidence from either a clean raw hash or a documented methodology change.

The next implementation priority is not threshold design. It is the automated provenance runner, release/revision evidence capture protocol, methodology-version registry, and deterministic gate report that feeds the R01 promotion decision.
