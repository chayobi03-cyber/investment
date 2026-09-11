# R01 CI Evidence Contract v0.1

## Purpose

Define the distinction between CI execution health and R01 provenance promotion.

## Core rule

A successful GitHub Actions run proves that the configured validation machinery executed successfully. It does **not** by itself prove that a source is `PRIMARY_VERIFIED`.

Promotion remains fail-closed and requires every R01 provenance gate to pass.

## CI states

| State | Meaning |
|---|---|
| NOT_IMPLEMENTED | R01 workflow does not exist |
| NOT_EXECUTED | Workflow exists but no execution evidence exists for the commit |
| EXECUTED | Workflow completed and evidence artifact was produced |
| FAILED | Validation machinery failed to execute or a test failed |

## Promotion states

| Gate result | Promotion behavior |
|---|---|
| PASS | Satisfies that gate |
| FAIL | Blocks promotion |
| UNKNOWN | Blocks promotion |
| HUMAN_REVIEW | Blocks automatic promotion |
| NOT_VERIFIED | Blocks promotion |

## Required CI evidence

Every executed R01 workflow should record:

- workflow name
- commit SHA
- workflow run ID
- job identifier
- Gate Report
- Gate Report SHA-256
- promotion eligibility
- blocking reasons

## Artifact rule

The Gate Report must distinguish:

`raw_capture_evidence` = historical evidence recorded in the manifest

from

`raw_artifact_runtime_integrity` = artifact actually available and hash-verified in the CI runtime.

Historical capture evidence cannot substitute for runtime artifact verification.

## Current REB interpretation

The July 2025 REB fixture has verified historical raw-capture evidence, but its declared PDF is not currently present in the repository runtime. CI therefore records runtime artifact integrity as `UNKNOWN` until an immutable CI-accessible artifact is supplied and hash-verified.

The REB revision/vintage status also remains unverified. Therefore `PRIMARY_VERIFIED` remains blocked even when the CI machinery itself executes successfully.
