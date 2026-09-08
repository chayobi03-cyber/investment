# Lessons Learned — 2026-09-08 Data Pipeline Connection

## Findings

1. The investment engine already had frozen Market Regime V1 and Stock Score V1 specifications, but the stock layer was explicitly marked `DATA CONNECTION PENDING`.
2. The first implementation must stop at `KRX/OpenDART raw data -> completeness -> raw factors -> point-in-time normalization`; ranking must not be regenerated from manually entered numbers.
3. KRX integration should be configuration-driven around the approved API contract. Undocumented KRX web endpoints must not be hard-coded as a production dependency.
4. OpenDART financial facts require `available_at`/filing-time semantics. Later revised facts must not leak into earlier decision timestamps.
5. Completeness is a gate, not a descriptive statistic. Missing critical KRX rows prevents downstream ranking publication.
6. Historical percentile normalization must use observations available at the current timestamp only.

## Rule Update

`Production data pipeline rule: no score/rank publication when critical source completeness is not GREEN; no silent proxy substitution; all time-varying normalization and financial joins must be point-in-time.`

## Next Gate

Provide the approved KRX API endpoint/key and OpenDART API key, collect the ten-name raw datasets, run the pipeline, inspect completeness failures, then freeze the first real raw/normalized factor snapshot before connecting Stock Score V1.
