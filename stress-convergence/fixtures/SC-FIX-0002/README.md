# SC-FIX-0002 — scope-corrected + provenance-aware baseline

Status: `RECONSTRUCTED_PENDING_CI`

Purpose:
- Replace the v0.2.3 official-recovered-only fixture with a newly reconstructed baseline.
- Freeze the benchmark scope and TTC linkage rules before running v0.2.4.
- Preserve raw upstream snapshots and SHA-256 hashes so the run is independently auditable.

Important distinction:
- SC-FIX-0002 is **not** a byte-for-byte recovery of the historical v0.2.3 artifact.
- It is a reconstructed fixture generated from the declared upstream sources at the CI execution time.
- Therefore any metric difference versus SC-FIX-0001 must be attributed first to fixture/provenance differences, not automatically to v0.2.4 logic.

## Frozen benchmark scope

The 11 benchmark windows are the same research set used in v0.2.3/v0.2.4:

| Window | Kind | Anchor |
|---|---|---|
| 1994_tightening | FP | — |
| 2000_dotcom | CRISIS | 2000-03-24 |
| 2004_05_tightening | FP | — |
| 2008_gfc | CRISIS | 2007-10-09 |
| 2013_taper | FP | — |
| 2016_china_energy | FP | — |
| 2017_reflation_fed | FP | — |
| 2018_q4_tightening_selloff | FP | — |
| 2020_covid | CRISIS | 2020-02-19 |
| 2021_reflation_taper | FP | — |
| 2022_rate_shock | CRISIS | 2022-01-03 |

## Frozen TTC policy

For crisis windows, a Crisis Confirmation is linked to an Early Warning only when:

`0 <= (CC_onset - EW_onset) <= 90 days`

and the linked CC is also inside the benchmark's declared scope. Confirmations outside the 90-day TTC window are retained as observations but are **not** accepted as linked crisis confirmation.

For FP windows, any stage onset inside the declared benchmark window is evaluated as a false-alarm candidate.

## Provenance requirement

The generated artifact must include:
- source URL for every upstream input;
- retrieval timestamp;
- raw snapshot SHA-256;
- transformation/code commit SHA;
- Python/package versions;
- benchmark/spec version;
- final panel SHA-256.

See `manifest.json` produced by the CI fixture-generation workflow.
