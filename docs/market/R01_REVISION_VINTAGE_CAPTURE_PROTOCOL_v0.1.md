# R01 Revision / Vintage Capture Protocol v0.1

## Purpose

Define a source-agnostic, fail-closed protocol for proving the release lineage of an R01 observation without overwriting earlier evidence.

## Core rule

`Unknown != No Revision`.

Absence of a discovered correction notice or revision identifier is not evidence that no revision occurred.

## Provenance axes

```text
Release Provenance
  publication
  raw binary
  SHA-256
  revision / vintage
  PIT

Methodology Provenance
  sample design
  extraction frame
  weighting
  index base
  methodology version
  structural break
```

## Vintage identity

Each captured release is an immutable observation of a source release.

```yaml
vintage:
  vintage_id: <source>_<observation>_<publication-date>_<sequence>
  source_id: <source_id>
  observation_period: <period>
  release:
    publication_date: <date>
    available_at: <timestamp-or-date>
    release_label: <official label>
  revision:
    status: ORIGINAL_VERIFIED | REVISED_VERIFIED | NO_REVISION_VERIFIED | UNKNOWN | NOT_VERIFIED
    revision_number: <integer-or-null>
    previous_vintage_id: <id-or-null>
    successor_vintage_id: <id-or-null>
    correction_notice_id: <id-or-null>
  artifact:
    storage_uri: <path>
    sha256: <sha256>
```

## Revision status semantics

| Status | Meaning | Promotion effect |
|---|---|---|
| `ORIGINAL_VERIFIED` | Primary evidence establishes this is the original released vintage and no earlier release in the lineage is being substituted | PASS for revision gate |
| `REVISED_VERIFIED` | Primary evidence establishes that this release supersedes an earlier vintage | PASS for revision gate |
| `NO_REVISION_VERIFIED` | Producer-issued evidence explicitly establishes no retrospective revision for the applicable release/series | PASS for revision gate |
| `UNKNOWN` | The available evidence is insufficient to establish lineage | FAIL |
| `NOT_VERIFIED` | Revision evidence work has not been completed | FAIL |

## Capture requirements

A revision/vintage capture is complete only when all applicable evidence is recorded:

1. Official release locator.
2. Publication date and, when available, publication time.
3. Raw artifact and SHA-256.
4. Producer-issued revision, correction, or version evidence; or producer-issued evidence explicitly stating no retrospective revision.
5. Previous/next vintage relation when applicable.
6. Search/capture method and retrieval date.
7. Evidence classification: primary, corroborative, or insufficient.

## Append-only lineage

Never replace an earlier artifact or mutate its historical metadata solely because a later version is discovered.

```text
observation 2025-07
  ├─ vintage v1 / published 2025-08-18
  ├─ vintage v2 / corrected 2025-09-03
  └─ vintage v3 / revised 2025-10-15
```

A later capture adds a new node and links it to the predecessor. Historical panel construction must select the vintage available at the decision timestamp rather than the latest vintage.

## Evidence hierarchy

```text
Producer-issued correction/version/revision record
        > producer-issued methodology/release policy
        > official release page / attachment metadata
        > secondary research
        > search-result inference
```

Secondary material may corroborate a claim but cannot, by itself, satisfy the R01 primary-source revision gate.

## Fail-closed rules

- Missing lineage evidence => `UNKNOWN` or `NOT_VERIFIED`; never `NO_REVISION_VERIFIED`.
- Hash mismatch => `REJECTED` / `SUSPENDED`.
- Conflicting release metadata => `SUSPENDED` until reconciled by primary evidence.
- Later revisions must not rewrite the prior vintage record.
- Current/latest data must not be silently substituted for a historical PIT vintage.

## Exit criteria

A source may pass the revision gate only when the release lineage is supported by producer-issued evidence and the captured artifact is hash-verifiable.

For the current REB 2025-07 fixture, this protocol does **not** change the existing status. The current manifest remains `revision.status = NOT_VERIFIED` until primary-source revision/vintage evidence is captured.
