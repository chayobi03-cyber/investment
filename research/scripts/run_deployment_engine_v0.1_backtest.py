#!/usr/bin/env python3
"""Portfolio Deployment Engine v0.1 — Risk Gate cap backtest.

Tests the single riskiest untested design choice in
docs/governance/PORTFOLIO_DEPLOYMENT_ENGINE_v0.1.md section 4.1: does
capping deployment intensity during Stress Convergence EARLY_WARNING /
TIGHTENING_STATE, and pausing it during CRISIS_CONFIRMATION, improve or
hurt outcomes versus not capping at all?

Three variants, same weekly benchmark, same total KRW budget:

  ENGINE_NOCAP   - Asset Opportunity (price-drawdown tiers, same as the
                   FX-accumulation replay's Strategy B) x FX Benefit
                   (bounded x0.3-x1.2 per the deployment engine doc),
                   with NO Risk Gate cap.
  ENGINE_WITHCAP - same as above, but capped at x1.5 combined intensity
                   during EARLY_WARNING/TIGHTENING_STATE, and forced to
                   x0.3 during CRISIS_CONFIRMATION (the deployment
                   engine's "pause new escalation" posture).
  BASELINE_A     - plain fixed periodic accumulation (no tilt at all),
                   same as Strategy A in the FX-accumulation replay.

Window is bounded to 1993-01-01 - 2022-01-10 (not the full 2004-2026 FX
replay window) because that is the coverage of the existing v0.2.3 Stress
Convergence daily-panel definitions this script reuses verbatim from
research/scripts/run_v0.2.3_daily_panel.py. This is a real scope caveat,
not an oversight - see the accompanying results write-up.

Research replay only, not a live trading signal.
"""
from __future__ import annotations

import io
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1].parent
OUT = ROOT / "research/results/deployment_engine_v0.1_backtest"
OUT.mkdir(parents=True, exist_ok=True)

START = "1993-01-01"
END = "2022-01-10"
WEEKLY_BASE_KRW = 1_000_000.0
ASSET_HIGH_WINDOW_W = 52
FX_LOW, FX_HIGH = 0.3, 1.2  # deployment-engine bounds, section 6
EW_TIGHTENING_CAP = 1.5
CRISIS_FORCE = 0.3

FRED = ["DGS10", "DGS2", "CPIAUCSL", "UNRATE"]
HY_URL = "https://raw.githubusercontent.com/TGRADEA/gradea-fred-archive/main/BAMLH0A0HYM2.csv"


def get_fred(sid: str) -> pd.Series:
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={sid}&cosd={START}&coed={END}"
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    d = pd.read_csv(io.StringIO(r.text))
    d.columns = ["date", sid]
    d["date"] = pd.to_datetime(d["date"])
    d[sid] = pd.to_numeric(d[sid], errors="coerce")
    return d.set_index("date")[sid]


def get_yahoo(symbol: str) -> pd.Series:
    p1 = int(pd.Timestamp(START, tz="UTC").timestamp())
    p2 = int((pd.Timestamp(END, tz="UTC") + pd.Timedelta(days=2)).timestamp())
    url = (
        f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        f"?period1={p1}&period2={p2}&interval=1d&events=history&includeAdjustedClose=true"
    )
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=60)
    r.raise_for_status()
    j = r.json()["chart"]["result"][0]
    dates = pd.to_datetime(j["timestamp"], unit="s", utc=True).tz_convert(None).normalize()
    vals = j["indicators"]["quote"][0]["close"]
    return pd.Series(vals, index=dates, name=symbol).astype(float)


def build_stress_states(daily: pd.DataFrame, cpi_monthly_raw: pd.Series) -> pd.DataFrame:
    """Reuses the v0.2.3 EARLY_WARNING / TIGHTENING_STATE / CRISIS_CONFIRMATION
    definitions verbatim from research/scripts/run_v0.2.3_daily_panel.py."""
    df = daily.copy()
    r_low = df["DGS10"].rolling("365D", min_periods=20).min()
    df["R"] = (df["DGS10"] >= r_low + 0.40).fillna(False).astype(bool)
    cpi_month = cpi_monthly_raw.dropna().resample("MS").last()
    cpi_yoy = cpi_month.pct_change(12) * 100
    i_month = ((cpi_yoy - cpi_yoy.shift(3)) >= 0.40).fillna(False).astype(bool)
    df["I"] = i_month.reindex(df.index, method="ffill").fillna(False).astype(bool)
    l_low = df["UNRATE"].rolling("365D", min_periods=3).min()
    df["L"] = (df["UNRATE"] >= l_low + 0.30).fillna(False).astype(bool)
    c_low = df["BAMLH0A0HYM2"].rolling("183D", min_periods=20).min()
    df["C"] = (df["BAMLH0A0HYM2"] >= c_low + 0.75).fillna(False).astype(bool)
    v25 = df["VIXCLS"] >= 25
    df["V"] = (v25.rolling(5, min_periods=5).sum() >= 5).fillna(False).astype(bool)
    sp_hi = df["SP500"].rolling(60, min_periods=20).max()
    df["E"] = (df["SP500"] <= sp_hi * 0.90).fillna(False).astype(bool)

    ri = df["R"] & df["I"]
    weekly = ri.resample("W-FRI").last().fillna(False).astype(bool)
    ew_week = weekly & weekly.shift(1, fill_value=False)
    df["EARLY_WARNING"] = ew_week.reindex(df.index, method="ffill").fillna(False).astype(bool)

    d2_low = df["DGS2"].rolling("365D", min_periods=20).min()
    d2_bps = (df["DGS2"] - d2_low) * 100
    df["TIGHTENING_STATE"] = (df["EARLY_WARNING"] & (d2_bps >= 40)).fillna(False).astype(bool)

    credit = df["C"] & df["V"] & (df["L"] | df["E"])
    growth = df["L"] & (df["E"] | df["V"]) & (df["C"] | df["R"])
    df["CRISIS_CONFIRMATION"] = (credit | growth).fillna(False).astype(bool)
    return df[["EARLY_WARNING", "TIGHTENING_STATE", "CRISIS_CONFIRMATION", "SP500", "USDKRW"]]


def main() -> int:
    raw = {s: get_fred(s) for s in FRED}
    df = pd.concat(raw, axis=1)
    hy = requests.get(HY_URL, timeout=60)
    hy.raise_for_status()
    hy_s = pd.read_csv(io.StringIO(hy.text), parse_dates=["observation_date"]).set_index(
        "observation_date"
    )["value"].rename("BAMLH0A0HYM2")
    sp = get_yahoo("%5EGSPC").rename("SP500")
    vix = get_yahoo("%5EVIX").rename("VIXCLS")
    fx = get_yahoo("KRW=X").rename("USDKRW")
    df = df.join([hy_s, sp, vix, fx], how="outer").sort_index()
    df[["CPIAUCSL", "UNRATE"]] = df[["CPIAUCSL", "UNRATE"]].ffill()
    df[["DGS10", "DGS2", "BAMLH0A0HYM2", "SP500", "VIXCLS", "USDKRW"]] = df[
        ["DGS10", "DGS2", "BAMLH0A0HYM2", "SP500", "VIXCLS", "USDKRW"]
    ].ffill()

    states = build_stress_states(df, raw["CPIAUCSL"])
    weekly = states.resample("W-FRI").last()
    weekly[["EARLY_WARNING", "TIGHTENING_STATE", "CRISIS_CONFIRMATION"]] = weekly[
        ["EARLY_WARNING", "TIGHTENING_STATE", "CRISIS_CONFIRMATION"]
    ].fillna(False).astype(bool)
    weekly = weekly.dropna(subset=["SP500", "USDKRW"])

    weekly["krw_cost"] = weekly["SP500"] * weekly["USDKRW"]
    roll_high = weekly["SP500"].rolling(ASSET_HIGH_WINDOW_W, min_periods=ASSET_HIGH_WINDOW_W).max()
    dd = weekly["SP500"] / roll_high - 1.0
    weekly["asset_opportunity"] = np.select(
        [dd <= -0.20, dd <= -0.10, dd <= -0.05], [3.0, 2.0, 1.5], default=1.0
    )
    weekly.loc[dd.isna(), "asset_opportunity"] = np.nan

    fx_pctl = (
        weekly["USDKRW"].rolling(156, min_periods=52).apply(
            lambda x: float((x <= x[-1]).sum()) / len(x) * 100.0, raw=True
        )
    )
    raw_fx = np.select([fx_pctl < 20, fx_pctl < 40, fx_pctl < 70], [1.2, 1.05, 1.0], default=0.85)
    weekly["fx_benefit"] = np.clip(raw_fx, FX_LOW, FX_HIGH)
    weekly.loc[fx_pctl.isna(), "fx_benefit"] = np.nan

    valid = weekly.dropna(subset=["asset_opportunity", "fx_benefit"]).copy()
    n = len(valid)

    combined = valid["asset_opportunity"] * valid["fx_benefit"]
    valid["raw_NOCAP"] = combined
    capped = combined.where(
        ~(valid["EARLY_WARNING"] | valid["TIGHTENING_STATE"]), np.minimum(combined, EW_TIGHTENING_CAP)
    )
    capped = capped.where(~valid["CRISIS_CONFIRMATION"], CRISIS_FORCE)
    valid["raw_WITHCAP"] = capped
    valid["raw_BASE"] = 1.0

    for strat in ["BASE", "NOCAP", "WITHCAP"]:
        raw_s = valid[f"raw_{strat}"]
        norm = raw_s * (n / raw_s.sum())
        valid[f"invested_{strat}"] = norm * WEEKLY_BASE_KRW
        valid[f"shares_{strat}"] = valid[f"invested_{strat}"] / valid["krw_cost"]

    valid.to_csv(OUT / "weekly_panel.csv", index_label="week")

    def irr_annualized(cashflows: np.ndarray) -> float:
        t_years = np.arange(len(cashflows)) / 52.0

        def npv(r: float) -> float:
            with np.errstate(over="ignore", invalid="ignore"):
                return float(np.sum(cashflows / (1.0 + r) ** t_years))

        lo, hi = -0.99, 5.0
        f_lo, f_hi = npv(lo), npv(hi)
        if not (np.isfinite(f_lo) and np.isfinite(f_hi)) or f_lo * f_hi > 0:
            return math.nan
        for _ in range(200):
            mid = (lo + hi) / 2
            f_mid = npv(mid)
            if not np.isfinite(f_mid):
                return math.nan
            if abs(f_mid) < 1e-6:
                return mid
            if f_lo * f_mid < 0:
                hi = mid
            else:
                lo, f_lo = mid, f_mid
        return (lo + hi) / 2

    rows = []
    for strat in ["BASE", "NOCAP", "WITHCAP"]:
        cum_shares = valid[f"shares_{strat}"].cumsum()
        cum_invested = valid[f"invested_{strat}"].cumsum()
        value = cum_shares * valid["krw_cost"]
        vpi = value / cum_invested
        mdd = float((vpi / vpi.cummax() - 1.0).min())

        cashflows = -valid[f"invested_{strat}"].to_numpy(dtype=float)
        cashflows = cashflows.copy()
        cashflows[-1] += float(value.iloc[-1])
        irr = irr_annualized(cashflows)

        ew_weeks = int((valid["EARLY_WARNING"] | valid["TIGHTENING_STATE"]).sum())
        crisis_weeks = int(valid["CRISIS_CONFIRMATION"].sum())
        invested_during_crisis = float(valid.loc[valid["CRISIS_CONFIRMATION"], f"invested_{strat}"].sum())

        rows.append(
            {
                "strategy": strat,
                "n_weeks": n,
                "ew_tightening_weeks": ew_weeks,
                "crisis_confirmation_weeks": crisis_weeks,
                "total_invested_krw": float(cum_invested.iloc[-1]),
                "final_value_krw": float(value.iloc[-1]),
                "total_return_pct": float(value.iloc[-1] / cum_invested.iloc[-1] - 1.0),
                "annualized_irr_pct": irr,
                "avg_acquisition_cost": float(cum_invested.iloc[-1] / cum_shares.iloc[-1]),
                "max_drawdown_pct": mdd,
                "invested_during_crisis_confirmation_krw": invested_during_crisis,
            }
        )

    summary = pd.DataFrame(rows)
    summary.to_csv(OUT / "strategy_summary.csv", index=False)

    metrics = {
        "data_start": valid.index.min().date().isoformat(),
        "data_end": valid.index.max().date().isoformat(),
        "n_weeks": int(n),
        "ew_tightening_cap": EW_TIGHTENING_CAP,
        "crisis_force_multiplier": CRISIS_FORCE,
        "fx_bounds": [FX_LOW, FX_HIGH],
        "note": "Research replay only, bounded to Stress Convergence v0.2.3 coverage (1993-2022-01-10), not a live trading signal.",
    }
    (OUT / "run_metrics.json").write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")

    print(summary.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
