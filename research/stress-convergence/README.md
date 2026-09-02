# Stress Convergence Research Reproducibility Layer

This directory is the reproducibility boundary for quantitative Stress Convergence experiments.

## Run gate

A quantitative run is **OFFICIAL** only when the following are all recorded:

1. fixture identity and SHA-256
2. anchor registry identity and SHA-256
3. rule specification identity and SHA-256
4. code commit
5. environment/dependency specification
6. run ID and execution timestamp
7. output hashes

A run reconstructed from an official artifact is labeled **RECOVERED**. A newly re-executed run from independently recreated upstream data is **RECONSTRUCTED**. These are not silently interchangeable.

## Experiment lifecycle

`HYPOTHESIS -> SPEC FREEZE -> FIXTURE FREEZE -> RULE HASH -> CODE COMMIT -> RUN -> RESULT HASH -> FALSIFICATION -> LESSON -> RULE CHANGE?`

## v0.2.3 baseline

The v0.2.3 daily panel used in the time-window experiment was recovered from GitHub Actions workflow run `33640923172`, artifact `v0.2.3-daily-panel-results`, artifact digest `sha256:94d74c114e3197b3f01c2cadb9378fc987a1a95e08977ce563404e8aed9c529d`.

The fixture SHA-256 is frozen in `fixtures/v0.2.3/manifest.json`.

## v0.2.4 rule

Primary confirmation is a Crisis Confirmation onset occurring strictly after the Early Warning onset and within 90 calendar days. 91-365 days is long-term connection only. More than 365 days is unrelated. A crisis confirmation before Early Warning is `PRE_EW` and cannot confirm the Early Warning.
