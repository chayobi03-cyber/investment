#!/usr/bin/env python3
"""Deployment Engine v0.1 -- full pipeline end-to-end backtest.

The last unchecked row in
docs/governance/PORTFOLIO_DEPLOYMENT_ENGINE_v0.1.md section 8. Combines
every piece that has actually been VALIDATED (not rejected) by this
session's separate replays into one static-total stock simulation, reusing
research/scripts/run_dry_powder_floor_backtest.py's structure:

  - Asset Opportunity tiers (price drawdown from 52w high) -- validated
    as the primary staging driver.
  - FX Benefit bounded modifier (x0.3-x1.2, USD/KRW trailing-3y percentile)
    -- validated bounds, applied as intended (a modifier, not a driver).
  - JPY confidence modifier (x0.9 caution flag when JPY/KRW rises while
    USD/JPY falls over a trailing window, per section 4.2) -- validated as
    a bounded, non-gating adjustment.
  - Dry Powder 28% floor -- replayed favorably (reduced max drawdown at
    negligible CAGR cost).

Deliberately EXCLUDED: the Stress Convergence Risk Gate cap from section
4.1. That specific design was replayed and rejected (cost IRR, no measured
drawdown benefit) in
research/deployment-engine-v0.1-risk-gate-cap-backtest-result-2026-09-08.md.
Including a rejected mechanism in the "full pipeline" test would not
reflect the actually-validated configuration, so this script tests stages
2 (JPY only, no Stress Convergence cap), 3, 4, and 5 (Dry Powder floor)
together, and reports that omission explicitly rather than silently.

Three paths, same starting static-total portfolio, same weekly benchmark:

  BASELINE        - no tactical tilt at all; annual non-drawdown rebalance
                    to 42/58 only (same "do nothing extra" concept as the
                    Dry Powder floor backtest's implicit baseline).
  FULL_NOFLOOR    - Asset Opportunity x FX Benefit x JPY caution tilt,
                    no Dry Powder floor.
  FULL_WITHFLOOR  - same tilt, with the 28% Dry Powder floor.

Research replay only, not a live trading signal.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1].parent
OUT = ROOT / "research/results/deployment_engine_v0.1_full_pipeline"
OUT.mkdir(parents=True, exist_ok=True)

START = "2004-01-01"
END = pd.Timestamp.now(tz="UTC").tz_localize(None).normalize()

ASSET_HIGH_WINDOW_W = 52
FX_PCTL_WINDOW_W = 156
FX_PCTL_MIN_PERIODS = 52
FX_LOW, FX_HIGH = 0.3, 1.2
JPY_MOMENTUM_WINDOW_W = 5
JPY_CAUTION_MULTIPLIER = 0.9

FLOOR_FRACTION = 0.28
INITIAL_TOTAL_KRW = 100_000_000.0
INITIAL_DRY_POWDER_FRACTION = 0.42
BASE_TRANCHE_FRACTION_OF_DP0 = 0.02
CASH_ANNUAL_YIELD = 0.035


def get_yahoo_daily(symbol: str) -> pd.Series:
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


def load_weekly() -> pd.DataFrame:
    sp = get_yahoo_daily("%5EGSPC").rename("SP500")
    fx = get_yahoo_daily("KRW=X").rename("USDKRW")
    jpykrw = get_yahoo_daily("JPYKRW=X").rename("JPYKRW")
    usdjpy = get_yahoo_daily("JPY=X").rename("USDJPY")
    daily = pd.concat([sp, fx, jpykrw, usdjpy], axis=1).sort_index().ffill()
    weekly = daily.resample("W-FRI").last().dropna(subset=["SP500", "USDKRW"])
    weekly["krw_cost"] = weekly["SP500"] * weekly["USDKRW"]

    roll_high = weekly["SP500"].rolling(ASSET_HIGH_WINDOW_W, min_periods=ASSET_HIGH_WINDOW_W).max()
    dd = weekly["SP500"] / roll_high - 1.0
    weekly["tier"] = np.select([dd <= -0.20, dd <= -0.10, dd <= -0.05], [3.0, 2.0, 1.5], default=1.0)
    weekly.loc[dd.isna(), "tier"] = np.nan

    fx_pctl = weekly["USDKRW"].rolling(FX_PCTL_WINDOW_W, min_periods=FX_PCTL_MIN_PERIODS).apply(
        lambda x: float((x <= x[-1]).sum()) / len(x) * 100.0, raw=True
    )
    raw_fx = np.select([fx_pctl < 20, fx_pctl < 40, fx_pctl < 70], [1.2, 1.05, 1.0], default=0.85)
    weekly["fx_benefit"] = np.clip(raw_fx, FX_LOW, FX_HIGH)
    weekly.loc[fx_pctl.isna(), "fx_benefit"] = np.nan

    jpy_up = weekly["JPYKRW"].pct_change(JPY_MOMENTUM_WINDOW_W) > 0
    usdjpy_down = weekly["USDJPY"].pct_change(JPY_MOMENTUM_WINDOW_W) < 0
    jpy_caution = (jpy_up & usdjpy_down).fillna(False)
    weekly["jpy_multiplier"] = np.where(jpy_caution, JPY_CAUTION_MULTIPLIER, 1.0)

    return weekly.dropna(subset=["tier", "fx_benefit"])


def simulate(valid: pd.DataFrame, tilt: bool, with_floor: bool) -> pd.DataFrame:
    dp0 = INITIAL_TOTAL_KRW * INITIAL_DRY_POWDER_FRACTION
    base_tranche = BASE_TRANCHE_FRACTION_OF_DP0 * dp0
    weekly_cash_rate = (1.0 + CASH_ANNUAL_YIELD) ** (1.0 / 52.0) - 1.0

    dry_powder = dp0
    shares = (INITIAL_TOTAL_KRW - dp0) / valid["krw_cost"].iloc[0]
    last_rebalance_year = None

    rows = []
    for ts, row in valid.iterrows():
        dry_powder *= 1.0 + weekly_cash_rate
        risk_asset_value = shares * row["krw_cost"]
        total = dry_powder + risk_asset_value

        if row["tier"] == 1.0 and ts.year != last_rebalance_year:
            target_dp = INITIAL_DRY_POWDER_FRACTION * total
            dry_powder = target_dp
            shares = (total - target_dp) / row["krw_cost"]
            risk_asset_value = shares * row["krw_cost"]
            last_rebalance_year = ts.year

        deployed = 0.0
        intended = 0.0
        if tilt and row["tier"] > 1.0:
            intended = base_tranche * row["tier"] * row["fx_benefit"] * row["jpy_multiplier"]
            if with_floor:
                max_allowed = max(0.0, dry_powder - FLOOR_FRACTION * total)
                deployed = min(intended, max_allowed, dry_powder)
            else:
                deployed = min(intended, dry_powder)
            if deployed > 0:
                shares += deployed / row["krw_cost"]
                dry_powder -= deployed
                risk_asset_value = shares * row["krw_cost"]
                total = dry_powder + risk_asset_value

        rows.append(
            {
                "week": ts,
                "tier": row["tier"],
                "dry_powder": dry_powder,
                "risk_asset_value": risk_asset_value,
                "total": total,
                "dry_powder_pct": dry_powder / total,
                "intended_tranche": intended,
                "deployed": deployed,
                "blocked": max(0.0, intended - deployed),
            }
        )
    return pd.DataFrame(rows).set_index("week")


def main() -> int:
    valid = load_weekly()

    results = {}
    for label, tilt, with_floor in [
        ("BASELINE", False, False),
        ("FULL_NOFLOOR", True, False),
        ("FULL_WITHFLOOR", True, True),
    ]:
        sim = simulate(valid, tilt, with_floor)
        sim.to_csv(OUT / f"path_{label}.csv")
        results[label] = sim

    summary_rows = []
    for label, sim in results.items():
        total = sim["total"]
        mdd = float((total / total.cummax() - 1.0).min())
        n_years = len(sim) / 52.0
        cagr = float((total.iloc[-1] / total.iloc[0]) ** (1.0 / n_years) - 1.0)
        summary_rows.append(
            {
                "path": label,
                "n_weeks": len(sim),
                "final_total_krw": float(total.iloc[-1]),
                "total_return_pct": float(total.iloc[-1] / total.iloc[0] - 1.0),
                "cagr_pct": cagr,
                "max_drawdown_pct": mdd,
                "min_dry_powder_pct": float(sim["dry_powder_pct"].min()),
                "total_deployed_krw": float(sim["deployed"].sum()),
                "total_blocked_krw": float(sim["blocked"].sum()),
            }
        )
    summary = pd.DataFrame(summary_rows)
    summary.to_csv(OUT / "summary.csv", index=False)

    metrics = {
        "data_start": valid.index.min().date().isoformat(),
        "data_end": valid.index.max().date().isoformat(),
        "n_weeks": int(len(valid)),
        "excluded_from_full_pipeline": "Stress Convergence Risk Gate cap (rejected replay 2026-09-08)",
        "included_pieces": ["asset_opportunity_tier", "fx_benefit_bounded", "jpy_caution_modifier", "dry_powder_floor(WITHFLOOR only)"],
        "note": "Research replay only, not a live trading signal.",
    }
    (OUT / "run_metrics.json").write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")

    print(summary.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
