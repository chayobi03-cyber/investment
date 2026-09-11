# R01 Market Panel Expansion Contract v0.1

## Status

- Gate: R01
- Current state: ACTIVE / BACKTEST BLOCKED
- Purpose: expand `market_series_001` into a PIT-safe, provenance-complete market panel without allowing post-hoc threshold tuning.

## Fixed execution order

```text
R01 Market Panel Expansion
→ Primary-source Provenance Completion
→ Historical Pre-event Panel
→ Operational Hypothesis Freeze
→ Threshold Preregistration
→ Backtest
→ Falsification
```

Backtest is explicitly blocked until the first four upstream gates are satisfied.

## Panel domains

1. Price / transactions
2. Volume / liquidity
3. Rates / financing
4. Credit / household leverage
5. Supply / construction / inventory
6. Unsold housing
7. Auction / distress
8. Policy / regulation
9. Geography / regional segmentation

Initial regional scopes: Korea-wide, 수도권, 비수도권. Finer regions may be added only after the base panel passes completeness and provenance checks.

## Canonical record

Every observation intended for research or backtest must expose:

- `panel_id`
- `metric_name`
- `observation_start`
- `observation_end`
- `publication_date`
- `available_at`
- `retrieved_at`
- `geographic_scope`
- `property_scope`
- `value`
- `unit`
- `frequency`
- `adjustment_rule`
- `revision_status`
- `revision_number`
- `source_id`
- `dataset_name`
- `source_locator`
- `raw_record_id`
- `raw_sha256`
- `normalization_rule`

## PIT / future-information rule

`available_at` is the earliest timestamp at which the exact observation/version is considered available to the decision process. Backtest input is valid only when:

```text
available_at <= decision_timestamp
```

A later vendor revision must never silently overwrite the historical value used by an earlier decision timestamp.

Records without a verifiable publication/availability date are classified `PROVISIONAL` and are not eligible for PIT backtest input.

## Revision rule

Revisions are append-only at the raw layer. A revised observation must retain:

- prior record identifier
- revision number
- revision publication date
- replacement relationship

The normalized research view must be reconstructable for any historical decision timestamp.

## Quality states

```text
PRIMARY_VERIFIED   = source, publication, availability, revision and hash evidence complete
PROVISIONAL        = usable for exploration, blocked from PIT backtest
REJECTED           = provenance/data-contract failure
```

No silent proxy, interpolation, forward-fill, or fabricated value is allowed for a missing critical observation.

## Historical event window contract

For each labeled event anchor `T0`, retain at minimum:

```text
T-365, T-180, T-90, T-30, T-7, T-1, T0, T+30, T+90
```

The event anchor and the decision timestamp are separate fields. Policy announcement and policy implementation may be distinct anchors.

## Freeze rule

After `Operational Hypothesis Freeze`, any change to observable definitions, sign conventions, lookback periods, persistence logic, threshold values, event labels, or falsifiers creates a new version. It must not mutate the preregistered run.

## Backtest gate

Backtest may start only when:

- all critical panel fields have defined provenance status;
- PIT availability checks pass;
- the historical pre-event panel is reproducible;
- hypotheses are frozen;
- thresholds are preregistered;
- the run manifest identifies exact dataset and code hashes.

## Falsification gate

Every backtest result must include explicit tests for false positives, false negatives, lead-time instability, regime dependence, and sensitivity to reasonable perturbations. A result that survives only because of post-hoc threshold selection is invalid.
