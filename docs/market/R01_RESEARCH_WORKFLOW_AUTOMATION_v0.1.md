# R01 Research Workflow Automation v0.1

## Purpose

Automate the R01 research lifecycle from planning through validation, falsification, lesson-learned reporting, and Git evidence capture while preserving fail-closed provenance rules.

## Non-negotiable principle

Automation may collect, validate, compare, classify, and report evidence. Automation must not silently promote a source, tune a threshold, overwrite a historical observation, or mutate a frozen research contract.

## Execution graph

```text
Research Planning
→ Source Registry
→ Evidence Capture
→ Release Provenance Gate
→ Methodology Provenance Gate
→ PIT Gate
→ Data Quality Gate
→ Historical Panel Construction
→ Hypothesis Freeze
→ Threshold Preregistration
→ Backtest
→ Falsification
→ Lesson Learned
→ Human Review
→ Promotion / Rejection
→ Git Commit
```

Backtest and threshold work remain blocked until the upstream provenance gates are green.

## Two provenance tracks

### Release Provenance

```text
publication
→ raw binary
→ SHA-256
→ revision / vintage
→ available_at
→ executable PIT test
```

### Methodology Provenance

```text
sample design
→ extraction frame
→ weighting
→ index base
→ methodology version
→ structural-break flag
```

A methodology change is not a release revision. Both must be represented independently.

## State machine

```yaml
PLANNED
SOURCE_REGISTERED
EVIDENCE_PENDING
RAW_CAPTURED
RAW_HASH_VERIFIED
RELEASE_METADATA_VERIFIED
METHODOLOGY_VERIFIED
REVISION_PENDING
PIT_PENDING
PROVISIONAL
PRIMARY_VERIFIED
PANEL_READY
HYPOTHESIS_FROZEN
THRESHOLD_FROZEN
BACKTESTED
FALSIFICATION_REVIEW
PROMOTED
REJECTED
SUSPENDED
```

State transitions are monotonic for a single evidence snapshot. A failed gate moves to `PROVISIONAL`, `REJECTED`, or `SUSPENDED`; it never jumps directly to a downstream research state.

## Automated gate outputs

Every gate produces a machine-readable result with:

- gate name and version
- input artifact identifiers
- source locator
- evidence references
- pass/fail/blocked status
- blocking reasons
- execution timestamp
- code version
- input hashes

## Revision handling

Raw captures are append-only. A revised release must create a new raw record rather than overwriting the prior record. The historical research view must be reconstructable for a decision timestamp.

When no source-issued revision rule is found, the status remains `NOT_VERIFIED`; absence of evidence is not converted to `no_revision`.

## PIT handling

`available_at` is the earliest defensible timestamp at which the exact observation/version was available. If only the release date is known, timestamp precision remains `date` and the PIT test must use a conservative date-level policy. Exact timestamps must not be invented from PDF metadata.

## Methodology handling

A change notice must be linked to the affected methodology fields. At minimum record:

```yaml
methodology:
  methodology_version: <explicit-or-unknown>
  sample_design_version: <explicit-or-unknown>
  extraction_frame: <explicit-or-unknown>
  weighting_rule: <explicit-or-unknown>
  index_base_period: <explicit-or-unknown>
  structural_break_risk: <true-or-false>
  change_evidence: []
```

If a methodology change occurs between two observations, the panel must retain the boundary and prevent silent cross-version comparability.

## Research freeze

After `HYPOTHESIS_FROZEN`:

- observable definitions are immutable for the run;
- lookback/persistence logic is immutable;
- thresholds are immutable after `THRESHOLD_FROZEN`;
- event labels and falsifiers are immutable;
- any substantive change creates a new version and a new run manifest.

## Falsification and lesson learned

Every backtest must emit:

```text
false_positive_checks
false_negative_checks
lead_time_checks
regime_dependence_checks
sensitivity_checks
lesson_learned
rule_change_candidates
```

`rule_change_candidates` are recommendations only. Human review is required before changing the research contract.

## Promotion policy

```python
primary_verified = all([
    official_source_confirmed,
    measurement_definition_confirmed,
    observation_basis_confirmed,
    publication_rule_confirmed,
    availability_rule_confirmed,
    revision_rule_confirmed,
    methodology_version_recorded,
    raw_capture_verified,
    raw_sha256_recorded,
    pit_test_passed,
])
```

Unknown or missing critical evidence is fail-closed.

## R01 example: REB 2025-07

Current intended state:

```text
RAW CAPTURE       = VERIFIED
SHA-256           = VERIFIED
RELEASE METADATA  = VERIFIED
METHODOLOGY       = EVIDENCED / VERSIONED
REVISION POLICY   = NOT_VERIFIED
PIT EXECUTION     = BLOCKED
PRIMARY_VERIFIED  = NO
```

This example remains blocked from Historical Pre-event Panel, Hypothesis Freeze, Threshold Preregistration, and Backtest until the missing gates are resolved.
