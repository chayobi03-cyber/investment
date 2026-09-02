# Stress Convergence Artifact Status — 2026-09-03

## OFFICIAL

- v0.2.3 daily-panel implementation: Git commit `36ce6c8c15ef5211d64c5f8b563749e893ce7ad3`.
- v0.2.3 execution head: `616cdd6c78f3ffe754833a51fc504a8a08332734`.
- CI workflow: `.github/workflows/v0.2.3-daily-panel.yml`.
- Successful workflow run: `33640923172`.
- CI artifact: `v0.2.3-daily-panel-results`, artifact id `9850771333`, digest `sha256:94d74c114e3197b3f01c2cadb9378fc987a1a95e08977ce563404e8aed9c529d`.
- Extracted daily panel and other outputs, with SHA-256 values recorded in `manifest.json`.
- Historical v0.2.3 report: `research/stress-convergence-v0.2.3-three-stage-daily-panel-2026-09-02.md`.

## RECOVERED

- The historical execution bundle was rehydrated from the official CI artifact into the working environment for TTC analysis. This is recovery of an official result, not an independent upstream-data rerun.

## RECONSTRUCTED

- None yet. No newly regenerated v0.2.3 daily panel is being substituted for the official artifact.

## MISSING

- Original raw FRED snapshots for DGS10, DGS2, CPIAUCSL and UNRATE.
- Original raw Yahoo snapshots for S&P 500 and VIX.
- Original HY OAS snapshot used by the run.
- Pinned package lock with exact pandas/numpy/requests/tabulate versions.
- Standalone historical run manifest from the original v0.2.3 execution.

## Gate consequence

The v0.2.3 output is valid as an **official recovered baseline artifact** for deterministic downstream transformations. It is not yet a fully reproducible upstream-data fixture. Future runs must preserve raw source snapshots or equivalent immutable source artifacts before claiming full upstream reproducibility.
