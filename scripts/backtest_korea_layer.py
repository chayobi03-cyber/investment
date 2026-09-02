"""Korea Layer historical backtest.

Purpose
-------
Test the provisional KOSPI absolute entry zones and their scale-invariant
52-week-high drawdown equivalents, while applying the Stress Convergence v0.2
confirmation topology as an independent state variable.

Data are fetched at execution time from public reproducible sources:
- KOSPI / USDKRW: FinanceDataReader
- Brent / US 10Y / VIX / HY OAS / NFCI / T5Y5Y: FRED

This is research evidence, not a live trading signal.
"""

from __future__ import annotations

import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

try:
    import FinanceDataReader as fdr
    from pandas_datareader import data as webdata
except ImportError as exc:  # pragma: no cover - CI installs dependencies
    raise SystemExit(f"missing dependency: {exc}")

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts/korea_layer_backtest"
OUT.mkdir(parents=True, exist_ok=True)

START = "2000-01-01"
END = pd.Timestamp("2026-09-03")
HORIZONS = {21: "1m", 63: "3m", 126: "6m", 252: "12m"}

# Provisional KOSPI zones from Korea Layer v0.1.
ABSOLUTE_BANDS = {
    "A_6600_6750": (6600.0, 6750.0),
    "B_6300_6500": (6300.0, 6500.0),
    "C_6000_6300": (6000.0, 6300.0),
}


@dataclass(frozen=True)
class Event:
    start: pd.Timestamp
    anchor: pd.Timestamp
    peak_drawdown: float


def fred(series: str) -> pd.Series:
    df = webdata.DataReader(series, "fred", START, END)
    s = df.iloc[:, 0].copy()
    s.index = pd.to_datetime(s.index)
    return s.rename(series)


def load_daily() -> pd.DataFrame:
    kospi = fdr.DataReader("KS11", START, END)[["Close"]].rename(columns={"Close": "kospi"})
    fx = fdr.DataReader("USD/KRW", START, END)[["Close"]].rename(columns={"Close": "usdkrw"})
    daily = kospi.join(fx, how="outer")

    for series in ["DCOILBRENTEU", "DGS10", "VIXCLS", "BAMLH0A0HYM2", "NFCI", "T5YIE"]:
        try:
            daily = daily.join(fred(series), how="outer")
        except Exception as exc:  # noqa: BLE001
            print(f"WARN unable to fetch {series}: {type(exc).__name__}: {exc}", file=sys.stderr)
            daily[series] = np.nan

    daily = daily.sort_index().loc[START : END]
    return daily


def persistence_5d(s: pd.Series, threshold: float, direction: str = "gt") -> pd.Series:
    x = s > threshold if direction == "gt" else s < threshold
    # v0.2: 5 consecutive trading days OR 2-of-3 consecutive observations.
    # The previous implementation accidentally used 2-of-5, which could
    # materially over-trigger the stress state.
    five = x.rolling(5, min_periods=5).sum() >= 5
    two_of_three = x.rolling(3, min_periods=3).sum() >= 2
    return five | two_of_three


def persistent_monthly_above(s: pd.Series, threshold: float) -> pd.Series:
    monthly = s.resample("ME").last()
    good = monthly > threshold
    two = good & good.shift(1, fill_value=False)
    # State becomes active from the month end where the second consecutive
    # observation is available, then forward-filled to daily dates.
    return two.reindex(s.index, method="ffill").fillna(False)


def persistent_weekly_above(s: pd.Series, threshold: float) -> pd.Series:
    weekly = s.resample("W-FRI").last()
    good = weekly > threshold
    two = good & good.shift(1, fill_value=False)
    return two.reindex(s.index, method="ffill").fillna(False)


def build_stress_state(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()

    out["energy_warn"] = persistence_5d(out["DCOILBRENTEU"], 90)
    out["energy_severe"] = persistence_5d(out["DCOILBRENTEU"], 100)
    out["rates_warn"] = persistence_5d(out["DGS10"], 4.75)
    out["credit_warn"] = persistence_5d(out["BAMLH0A0HYM2"], 400)
    out["credit_severe"] = persistence_5d(out["BAMLH0A0HYM2"], 500)
    out["vix_warn"] = persistence_5d(out["VIXCLS"], 25)
    out["vix_severe"] = persistence_5d(out["VIXCLS"], 35)
    out["nfci_warn"] = persistent_weekly_above(out["NFCI"], 0)
    out["nfci_severe"] = persistent_weekly_above(out["NFCI"], 0.5)
    out["inflation_warn"] = persistent_monthly_above(out["T5YIE"], 2.5)
    out["inflation_severe"] = persistent_monthly_above(out["T5YIE"], 3.0)

    # v0.2 gate A. "Energy materially worsening" is operationalized by the
    # severe energy condition when the comparable inflation series is absent.
    inflationary_leg = (
        out["energy_warn"]
        & out["credit_warn"]
        & (out["inflation_warn"] | out["energy_severe"])
        & out["rates_warn"]
    )
    financial_leg = out["credit_severe"] & out["vix_severe"] & out["nfci_warn"]

    out["inflationary_leg"] = inflationary_leg.fillna(False)
    out["financial_leg"] = financial_leg.fillna(False)
    out["l2_trigger"] = (out["inflationary_leg"] | out["financial_leg"]).fillna(False)

    # Research-only state, intentionally not called the full 0-24 score because
    # Fed-hike-probability and AI-financing axes are not reconstructed here.
    warning_count = sum(
        out[c].fillna(False).astype(int)
        for c in [
            "energy_warn",
            "inflation_warn",
            "rates_warn",
            "credit_warn",
            "nfci_warn",
            "vix_warn",
        ]
    )
    out["stress_warning_axes"] = warning_count
    out["stress_state"] = np.select(
        [out["l2_trigger"], warning_count >= 3],
        [2, 1],
        default=0,
    )
    return out


def first_true_after(series: pd.Series, dates: pd.DatetimeIndex) -> pd.Series:
    values = []
    for d in dates:
        sub = series.loc[d:]
        idx = sub.index[sub.astype(bool)]
        values.append(idx[0] if len(idx) else pd.NaT)
    return pd.Series(values, index=dates)


def define_drawdown_events(df: pd.DataFrame, threshold: float = -0.15, merge_days: int = 60) -> list[Event]:
    dd = df["drawdown_252"].dropna()
    hits = dd[dd <= threshold]
    if hits.empty:
        return []

    events: list[Event] = []
    start = None
    last = None
    trough = None
    for ts, value in hits.items():
        if start is None:
            start = ts
            last = ts
            trough = value
            continue
        gap = (ts - last).days
        if gap > merge_days:
            events.append(Event(start, last, float(trough)))
            start = ts
            trough = value
        else:
            trough = min(float(trough), float(value))
        last = ts
    events.append(Event(start, last, float(trough)))
    return events


def event_metrics(df: pd.DataFrame, events: list[Event]) -> tuple[pd.DataFrame, pd.DataFrame]:
    triggers = df.index[df["l2_trigger"]]
    rows = []
    used_trigger_dates: set[pd.Timestamp] = set()
    for ev in events:
        candidates = triggers[(triggers >= ev.start - pd.Timedelta(days=365)) & (triggers <= ev.start)]
        trig = candidates[0] if len(candidates) else pd.NaT
        if pd.notna(trig):
            used_trigger_dates.add(trig)
            lead = (ev.start - trig).days
            trig_state = int(df.loc[trig, "stress_state"])
        else:
            lead = math.nan
            trig_state = 0
        rows.append(
            {
                "event_start": ev.start.date().isoformat(),
                "event_anchor": ev.anchor.date().isoformat(),
                "peak_drawdown": ev.peak_drawdown,
                "trigger": trig.date().isoformat() if pd.notna(trig) else None,
                "lead_days": lead,
                "trigger_state": trig_state,
            }
        )

    # FP = L2 trigger with no >=15% drawdown in the next 60 calendar days.
    fp_rows = []
    for trig in triggers:
        future = df.loc[trig : trig + pd.Timedelta(days=60), "drawdown_252"].dropna()
        reaches = bool((future <= -0.15).any()) if not future.empty else False
        if not reaches:
            fp_rows.append({"trigger": trig.date().isoformat(), "fp": True})
    return pd.DataFrame(rows), pd.DataFrame(fp_rows)


def band_metrics(df: pd.DataFrame, name: str, low: float, high: float, current_high: float) -> pd.DataFrame:
    lo_dd = low / current_high - 1.0
    hi_dd = high / current_high - 1.0
    # Band is represented as a drawdown interval; values are negative.
    dd_low = min(lo_dd, hi_dd)
    dd_high = max(lo_dd, hi_dd)
    in_band = df["drawdown_252"].between(dd_low, dd_high, inclusive="both")
    starts = in_band & ~in_band.shift(1, fill_value=False)
    idxs = list(df.index[starts])
    rows = []
    for ts in idxs:
        base = float(df.loc[ts, "kospi"])
        row = {
            "band": name,
            "entry_date": ts.date().isoformat(),
            "entry_kospi": base,
            "entry_drawdown": float(df.loc[ts, "drawdown_252"]),
            "stress_state": int(df.loc[ts, "stress_state"]),
            "l2_trigger": bool(df.loc[ts, "l2_trigger"]),
        }
        for days, label in HORIZONS.items():
            target = ts + pd.Timedelta(days=days)
            future_idx = df.index[df.index >= target]
            if len(future_idx):
                ft = future_idx[0]
                row[f"ret_{label}"] = float(df.loc[ft, "kospi"] / base - 1.0)
            else:
                row[f"ret_{label}"] = np.nan
            window = df.loc[ts : ts + pd.Timedelta(days=days), "kospi"]
            row[f"mdd_{label}"] = float(window.min() / base - 1.0) if not window.empty else np.nan
        recovery = df.loc[ts:, "kospi"] >= base
        row["recovery_days"] = float((recovery.index[0] - ts).days) if bool(recovery.any()) else np.nan
        rows.append(row)
    return pd.DataFrame(rows)


def summarize_band(events: pd.DataFrame) -> pd.DataFrame:
    if events.empty:
        return pd.DataFrame([{"n": 0}])
    result = {
        "n": len(events),
        "stress_l2_n": int(events["l2_trigger"].sum()),
        "non_l2_n": int((~events["l2_trigger"]).sum()),
    }
    for label in HORIZONS.values():
        result[f"avg_ret_{label}"] = float(events[f"ret_{label}"].mean()) if events[f"ret_{label}"].notna().any() else np.nan
        result[f"median_ret_{label}"] = float(events[f"ret_{label}"].median()) if events[f"ret_{label}"].notna().any() else np.nan
        result[f"avg_mdd_{label}"] = float(events[f"mdd_{label}"].mean()) if events[f"mdd_{label}"].notna().any() else np.nan
    result["median_recovery_days"] = float(events["recovery_days"].median()) if events["recovery_days"].notna().any() else np.nan
    return pd.DataFrame([result])


def main() -> int:
    df = load_daily()
    df = build_stress_state(df)
    df["rolling_high_252"] = df["kospi"].rolling(252, min_periods=252).max()
    df["drawdown_252"] = df["kospi"] / df["rolling_high_252"] - 1.0
    df = df.dropna(subset=["kospi", "rolling_high_252"]).copy()

    analysis_date = df.index.max()
    current_close = float(df.loc[analysis_date, "kospi"])
    current_high = float(df.loc[analysis_date, "rolling_high_252"])

    band_rows = []
    detail_rows = []
    for name, (low, high) in ABSOLUTE_BANDS.items():
        lo_dd = low / current_high - 1.0
        hi_dd = high / current_high - 1.0
        band_rows.append(
            {
                "band": name,
                "absolute_low": low,
                "absolute_high": high,
                "equivalent_dd_low": min(lo_dd, hi_dd),
                "equivalent_dd_high": max(lo_dd, hi_dd),
            }
        )
        detail = band_metrics(df, name, low, high, current_high)
        if not detail.empty:
            detail_rows.append(detail)

    entries = pd.concat(detail_rows, ignore_index=True) if detail_rows else pd.DataFrame()
    summary = entries.groupby("band", as_index=False).apply(lambda x: summarize_band(x).assign(band=x.name), include_groups=False).reset_index(drop=True) if not entries.empty else pd.DataFrame()

    events = define_drawdown_events(df, threshold=-0.15)
    event_df, fp_df = event_metrics(df, events)

    # Episode diagnostics requested by the existing v0.2 benchmark.
    benchmark_dates = {
        "2000_dotcom_proxy": "2000-09-01",
        "2008_gfc": "2008-01-22",
        "2020_covid": "2020-03-16",
        "2022_inflation_rates": "2022-03-07",
        "2011_false_positive_control": "2011-08-03",
        "2018_false_positive_control": "2018-12-24",
    }
    benchmark_rows = []
    for name, date in benchmark_dates.items():
        idx = df.index[df.index >= pd.Timestamp(date)]
        if len(idx):
            ts = idx[0]
            benchmark_rows.append(
                {
                    "episode": name,
                    "first_available_on_or_after": ts.date().isoformat(),
                    "kospi": float(df.loc[ts, "kospi"]),
                    "drawdown_252": float(df.loc[ts, "drawdown_252"]),
                    "l2_trigger": bool(df.loc[ts, "l2_trigger"]),
                    "inflationary_leg": bool(df.loc[ts, "inflationary_leg"]),
                    "financial_leg": bool(df.loc[ts, "financial_leg"]),
                    "stress_warning_axes": int(df.loc[ts, "stress_warning_axes"]),
                }
            )
    benchmark_df = pd.DataFrame(benchmark_rows)

    entries.to_csv(OUT / "korea_layer_entry_events.csv", index=False)
    summary.to_csv(OUT / "korea_layer_entry_summary.csv", index=False)
    event_df.to_csv(OUT / "stress_convergence_kospi_events.csv", index=False)
    fp_df.to_csv(OUT / "stress_convergence_false_positives.csv", index=False)
    pd.DataFrame(band_rows).to_csv(OUT / "absolute_to_drawdown_mapping.csv", index=False)
    benchmark_df.to_csv(OUT / "stress_convergence_benchmark_episodes.csv", index=False)

    metrics = {
        "analysis_date": analysis_date.date().isoformat(),
        "current_close": current_close,
        "current_252d_high": current_high,
        "drawdown_events_n": len(events),
        "l2_trigger_days": int(df["l2_trigger"].sum()),
        "false_positive_days_n": len(fp_df),
        "data_start": df.index.min().date().isoformat(),
        "data_end": df.index.max().date().isoformat(),
        "persistence_definition": "5 consecutive trading days OR 2-of-3 consecutive observations",
        "note": "Research-only; full 0-24 Stress Convergence score is not reconstructed.",
    }
    (OUT / "run_metrics.json").write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")

    result_lines = [
        "# Korea Layer Backtest Result",
        "",
        f"Analysis date: {analysis_date.date().isoformat()}",
        f"KOSPI close: {current_close:.2f}",
        f"252-day high: {current_high:.2f}",
        f">=15% drawdown events: {len(events)}",
        f"L2 trigger days: {int(df['l2_trigger'].sum())}",
        f"False-positive trigger days (60d horizon): {len(fp_df)}",
        "",
        "Persistence definition: 5 consecutive trading days OR 2-of-3 consecutive observations.",
        "This backtest remains research-only and does not reconstruct the full 0-24 Stress Convergence score.",
    ]
    (OUT / "RESULT.md").write_text("\n".join(result_lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
