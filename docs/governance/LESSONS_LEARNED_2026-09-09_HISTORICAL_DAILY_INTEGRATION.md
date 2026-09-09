# Lessons Learned — 2026-09-09 Historical Daily Integration

## Finding

The historical store is useful only when the daily market-review output is converted into explicit, versioned records at decision time.

## Rule

Every daily review must preserve:

- observation timestamp
- data version
- model version
- market snapshot
- stock snapshot
- explicit decision record
- later outcome record

The ingestion layer must never synthesize unavailable market values merely to complete a record.

## Implementation lesson

The repository's existing investment pipeline and the historical persistence layer should remain separated by an explicit daily-ingest adapter. This keeps upstream data-quality failures visible instead of allowing them to be hidden by persistence logic.

## Git/storage lesson

V1 remains in the existing `investment` repository. Re-evaluate external database/object storage only when data volume or query workload materially justifies it.
