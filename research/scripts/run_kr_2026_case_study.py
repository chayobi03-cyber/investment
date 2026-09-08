#!/usr/bin/env python3
"""
Korea (KOSPI) 2026 case study, using the same Market Regime v0.1 pipeline as
research/scripts/run_market_regime_v0.1_backtest.py.

Motivated by that script's first exploratory result (framework section 9.1):
a non-monotonic, partly mean-reversion-looking score-bucket-vs-forward-return
pattern over 1996-2026, and the new P0 item to decompose that result by
historical episode rather than trust one full-sample average. This script is
a first, narrow step in that direction: it does not re-run the full episode
decomposition (2000-02 / 2008-09 / 2020 / 2022 are still open work), but asks
a related, answerable question -- "where does 2026 itself sit, on the same
scale, against its own 30-year history?" -- as a live example, since the user
asked specifically for Korea's current-year data.

Status: EXPLORATORY, same caveats as the parent script (no frozen
fixture/spec hash; single full-sample run; R1/R6 cut points not yet
recalibrated; do not use this to size or trigger a real trade).
"""
import importlib.util
from pathlib import Path

import pandas as pd

OUT = Path("research/results/kr_2026_case_study")
OUT.mkdir(parents=True, exist_ok=True)

_spec = importlib.util.spec_from_file_location(
    "market_regime_backtest", str(Path(__file__).parent / "run_market_regime_v0.1_backtest.py")
)
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)


def main():
    df, panel, regions = m.load_and_score()
    kr_market, kr_breadth, kr_regime, kospi = regions["KOSPI"]
    last_available = df.index.max()

    panel_2026 = panel.loc["2026-01-01":"2026-12-31"]
    if panel_2026.empty:
        print("No 2026 rows in the combined panel -- nothing to report.")
        return

    print(f"2026 KOSPI panel: {panel_2026.index.min().date()} to {panel_2026.index.max().date()}, {len(panel_2026)} rows")

    full_history_regime_share = kr_regime.value_counts(normalize=True).mul(100).round(1)
    y2026_regime_share = panel_2026["KR_Regime"].value_counts(normalize=True).mul(100).round(1)
    regime_compare = pd.DataFrame({
        "2026 share %": y2026_regime_share,
        "full-history share %": full_history_regime_share,
    }).reindex(["R1", "R2", "R3", "R4", "R5", "R6"]).fillna(0.0)
    regime_compare.to_csv(OUT / "regime_share_2026_vs_full_history.csv")
    print("\n=== KOSPI Regime share: 2026 vs. full 1996-2026 history ===")
    print(regime_compare.to_string())

    score_compare = pd.DataFrame({
        "2026": panel_2026["KR_Market_Score"].describe(),
        "full-history": kr_market.describe(),
    })
    print("\n=== KR_Market_Score distribution: 2026 vs. full history ===")
    print(score_compare.to_string())

    # regime transitions within 2026 (onset dates only, to see how many times
    # and when the regime label actually changed this year)
    regime_2026 = panel_2026["KR_Regime"]
    onsets = regime_2026[regime_2026 != regime_2026.shift(1)]
    print("\n=== KOSPI regime onsets during 2026 (date -> new regime) ===")
    for dt, r in onsets.items():
        print(f"  {dt.date()}  -> {r}  (Market_Score={panel_2026.loc[dt, 'KR_Market_Score']:.1f}, "
              f"Breadth={panel_2026.loc[dt, 'KR_Breadth']:.1f}, KOSPI={panel_2026.loc[dt, 'KOSPI']:.1f})")
    onsets_df = pd.DataFrame({
        "date": [d.date().isoformat() for d in onsets.index],
        "new_regime": onsets.values,
        "market_score": panel_2026.loc[onsets.index, "KR_Market_Score"].values,
        "breadth_score": panel_2026.loc[onsets.index, "KR_Breadth"].values,
        "kospi": panel_2026.loc[onsets.index, "KOSPI"].values,
    })
    onsets_df.to_csv(OUT / "kospi_2026_regime_onsets.csv", index=False)

    # realized forward returns for 2026 start dates, using the SAME row-based
    # shift(-h) convention as score_bucket_table/regime_performance_table in
    # the parent script (not a separate calendar-day computation), so results
    # here are directly comparable to framework section 9's tables. A window
    # that has not yet matured as of the data's last available row comes back
    # NaN from shift(-h) and is reported as "OPEN", not silently dropped.
    fwd_by_horizon = {h: (kospi.shift(-h) / kospi - 1) * 100 for h in m.FORWARD_HORIZONS}
    rows = []
    for dt in panel_2026.index:
        row = {"date": dt.date().isoformat(), "regime": panel_2026.loc[dt, "KR_Regime"],
               "market_score": float(panel_2026.loc[dt, "KR_Market_Score"])}
        for h in m.FORWARD_HORIZONS:
            val = fwd_by_horizon[h].loc[dt]
            row[f"fwd_{h}d_pct"] = float(val) if pd.notna(val) else "OPEN"
        rows.append(row)
    fwd_2026 = pd.DataFrame(rows)
    fwd_2026.to_csv(OUT / "kospi_2026_forward_returns.csv", index=False)

    matured_120d = fwd_2026[fwd_2026["fwd_120d_pct"] != "OPEN"]
    print(f"\n=== 2026 dates with a matured 120-trading-day forward window (as of {last_available.date()}): {len(matured_120d)} of {len(fwd_2026)} ===")
    if len(matured_120d):
        by_regime = matured_120d.copy()
        by_regime["fwd_120d_pct"] = by_regime["fwd_120d_pct"].astype(float)
        summary = by_regime.groupby("regime")["fwd_120d_pct"].agg(["count", "mean", "min", "max"])
        print(summary.to_string())
        summary.to_csv(OUT / "kospi_2026_matured_120d_by_regime.csv")

    report_lines = [
        "# KOSPI 2026 case study (Market Regime v0.1, exploratory)",
        "",
        f"2026 panel window: {panel_2026.index.min().date()} to {panel_2026.index.max().date()} ({len(panel_2026)} rows). "
        f"Full-history comparison base: {df.index.min().date()} to {df.index.max().date()} ({len(df)} rows).",
        "",
        "Status: EXPLORATORY -- same caveats as the parent backtest (framework section 9.1): "
        "single full-sample run, R1/R6 cut points not yet recalibrated, not an OFFICIAL "
        "reproducibility-gated run. This is a narrow, current-year slice, not the full "
        "episode decomposition still listed as an open P0 item.",
        "",
        "## Regime share: 2026 vs. full 1996-2026 history",
        "",
        regime_compare.to_markdown(),
        "",
        "## KR_Market_Score distribution: 2026 vs. full history",
        "",
        score_compare.to_markdown(),
        "",
        "## Regime onsets during 2026",
        "",
        onsets_df.to_markdown(index=False),
        "",
    ]
    if len(matured_120d):
        report_lines += [
            f"## 2026 dates with a matured 120-day forward window (as of {last_available.date()})",
            "",
            summary.to_markdown(),
            "",
        ]
    (OUT / "report.md").write_text("\n".join(report_lines), encoding="utf-8")


if __name__ == "__main__":
    main()
