#!/usr/bin/env python3
"""Deployment Engine v0.1 -- Dry Powder 28% floor backtest.

Tests the last unbacktested row in
docs/governance/PORTFOLIO_DEPLOYMENT_ENGINE_v0.1.md section 7/8: does a
hard floor that blocks further deployment once Dry Powder would fall below
28% of the active sandbox change outcomes versus no floor?

Unlike the FX-accumulation and Risk-Gate-cap replays (which model a
recurring weekly budget being added over time), a Dry Powder floor is a
STOCK question: you start with a fixed pool of dry powder and risk assets,
tactically move money from the pool into the risk asset as drawdown
opportunities appear, and the floor asks whether you should ever refuse to
do so because the pool itself is getting too small. This script therefore
simulates a static-total-size portfolio (no new external contributions)
rather than reusing the earlier normalized weekly-budget machinery.

Two paths, same starting portfolio, same weekly benchmark:

  NOFLOOR   - deploy the full opportunity-scaled tranche every drawdown
              week, capped only by whatever Dry Powder remains (can go to
              zero).
  WITHFLOOR - same tranche logic, but never deploy an amount that would
              push Dry Powder below 28% of the current total portfolio
              value.

Research replay only, not a live trading signal.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[1].parent
OUT = ROOT / "research/results/dry_powder_floor_backtest"
OUT.mkdir(parents=True, exist_ok=True)

START = "2004-01-01"
END = pd.Timestamp.now(tz="UTC").tz_localize(None).normalize()

ASSET_HIGH_WINDOW_W = 52
FLOOR_FRACTION = 0.28
INITIAL_TOTAL_KRW = 100_000_000.0
INITIAL_DRY_POWDER_FRACTION = 0.42  # Balanced target, Portfolio Allocation Rule v0.1
BASE_TRANCHE_FRACTION_OF_DP0 = 0.02  # per drawdown-week at tier=1.0-equivalent intensity
CASH_ANNUAL_YIELD = 0.035  # Dry Powder = CD-rate ETF + cash + SGOV, approximate yield


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
    daily = pd.concat([sp, fx], axis=1).sort_index().ffill()
    weekly = daily.resample("W-FRI").last().dropna(subset=["SP500", "USDKRW"])
    weekly["krw_cost"] = weekly["SP500"] * weekly["USDKRW"]
    roll_high = weekly["SP500"].rolling(ASSET_HIGH_WINDOW_W, min_periods=ASSET_HIGH_WINDOW_W).max()
    dd = weekly["SP500"] / roll_high - 1.0
    weekly["tier"] = np.select([dd <= -0.20, dd <= -0.10, dd <= -0.05], [3.0, 2.0, 1.5], default=1.0)
    weekly.loc[dd.isna(), "tier"] = np.nan
    return weekly.dropna(subset=["tier"])


def simulate(valid: pd.DataFrame, with_floor: bool) -> pd.DataFrame:
    """Multi-decade equity appreciation would otherwise passively erode the
    Dry Powder weight over the full window regardless of any deployment
    decision (equities compound faster than the cash yield), which would
    swamp the specific question this backtest asks. To isolate the effect
    of *tactical crisis-driven deployment* (what the 28% floor is actually
    meant to guard against) from ordinary long-run portfolio drift, this
    simulation rebalances back to the 42/58 target split once a year, but
    ONLY in a week with no active drawdown (tier == 1.0) - never mid-crisis,
    since rebalancing mid-crisis would erase the exact dynamic being tested.
    """
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

        rebalanced = False
        if row["tier"] == 1.0 and ts.year != last_rebalance_year:
            target_dp = INITIAL_DRY_POWDER_FRACTION * total
            dry_powder = target_dp
            shares = (total - target_dp) / row["krw_cost"]
            risk_asset_value = shares * row["krw_cost"]
            last_rebalance_year = ts.year
            rebalanced = True

        deployed = 0.0
        intended = 0.0
        if row["tier"] > 1.0:
            intended = base_tranche * row["tier"]
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
                "krw_cost": row["krw_cost"],
                "rebalanced": rebalanced,
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
    for label, with_floor in [("NOFLOOR", False), ("WITHFLOOR", True)]:
        sim = simulate(valid, with_floor)
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
                "weeks_dry_powder_below_28pct": int((sim["dry_powder_pct"] < FLOOR_FRACTION).sum()),
                "total_deployed_krw": float(sim["deployed"].sum()),
                "total_blocked_krw": float(sim["blocked"].sum()),
                "drawdown_weeks_n": int((sim["tier"] > 1.0).sum()),
            }
        )
    summary = pd.DataFrame(summary_rows)
    summary.to_csv(OUT / "summary.csv", index=False)

    metrics = {
        "data_start": valid.index.min().date().isoformat(),
        "data_end": valid.index.max().date().isoformat(),
        "n_weeks": int(len(valid)),
        "initial_total_krw": INITIAL_TOTAL_KRW,
        "initial_dry_powder_fraction": INITIAL_DRY_POWDER_FRACTION,
        "floor_fraction": FLOOR_FRACTION,
        "base_tranche_fraction_of_dp0": BASE_TRANCHE_FRACTION_OF_DP0,
        "cash_annual_yield_assumption": CASH_ANNUAL_YIELD,
        "note": "Static-total-size tactical reallocation research replay, not a live trading signal.",
    }
    (OUT / "run_metrics.json").write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")

    print(summary.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
