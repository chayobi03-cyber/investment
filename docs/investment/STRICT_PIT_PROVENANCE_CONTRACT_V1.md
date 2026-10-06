# Strict PIT Provenance Contract V1

Date: 2026-09-22  
Status: RESEARCH DATA CONTRACT — NOT YET GREEN

## Purpose

Separate an executable historical vendor panel from a promotion-grade point-in-time (PIT) dataset.

A dataset is not strict PIT merely because it has `observed_at` and `available_at`. The source must preserve the information state that was actually available at the decision time, including revision/vintage control.

## Statuses

- `VENDOR_HISTORY_PROXY`: usable for pipeline integration and research diagnostics; not suitable for promotion.
- `STRICT_PIT_ARCHIVAL`: eligible for the strict PIT gate only when all required provenance checks pass.

## Required strict manifest fields

```text
pit_status = STRICT_PIT_ARCHIVAL
pit_archival_revisions = true
price_vintage_policy = AS_PUBLISHED | ACTION_AWARE
source_version = non-empty
artifact_sha256 = non-empty
```

For `ACTION_AWARE`, the source must also provide:

```text
corporate_action_ledger_status = ARCHIVAL_GREEN
```

## Price policy

The current vendor-history builder now stores raw vendor OHLC without applying `Adj Close` factors.

This removes one known contamination path: adjusted equity prices can incorporate later dividend/corporate-action information. Raw vendor OHLC is therefore safer for research replay, but it remains `VENDOR_CURRENT_RAW` until revision/vintage history is archived.

## Fundamental PIT policy

OpenDART is the preferred official Korean source for financial statements and filings. Financial facts must be keyed to the filing/reception timestamp and revision lineage, not to the latest restated database view. OpenDART's XBRL endpoint is addressed by disclosure receipt number (`rcept_no`), which provides a concrete filing-level provenance key. 

## Market-data source policy

The KRX Data Marketplace provides historical security and market datasets, including individual-security prices, investor trading, foreign ownership, and related market statistics. A strict price release must retain the retrieval/source version and frozen universe metadata alongside the observation rows.

## Promotion rule

`STRICT_PIT_ARCHIVAL` is a data gate, not a conclusion about model quality.

The sequence remains:

```text
raw source
→ immutable artifact
→ SHA-256
→ provenance manifest
→ PIT gate
→ P0→P6 backtest
→ sensitivity/falsification
→ promotion review
```

Until the archival evidence exists, P0-P5 research can continue with `VENDOR_HISTORY_PROXY`, but live MarketScore/BuyStrength changes remain blocked and P6 remains fail-closed.

## False-positive metric rule

`false_positive_rate` must never be defined as `1 - positive_return_rate`.

A valid classification metric requires an explicit predicted label, an explicit realized label, and a defined target universe containing both positive and negative cases. The current research pipeline therefore reports classification metrics as `DATA_NOT_READY` until those labels exist.