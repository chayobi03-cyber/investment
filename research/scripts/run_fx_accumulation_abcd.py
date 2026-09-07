#!/usr/bin/env python3
"""FX Accumulation A/B/C/D replay.

Implements the P0 open-work item from the 2026-09-08 Claude handover:
compare four accumulation strategies for building a KRW-funded S&P 500
position, on a common benchmark, common weekly decision frequency, and
common total cash budget.

Strategies (see docs/governance/LESSONS_LEARNED_2026-09-07_FX_ACCUMULATION.md
section 8 for the governance definition):

  A. Fixed periodic accumulation (plain weekly DCA).
  B. Asset-price trigger (buy more as S&P 500 falls further below its
     trailing 52-week high).
  C. FX trigger (buy more as USD/KRW falls to a lower point in its
     trailing 3-year distribution, i.e. KRW strengthens).
  D. Combined trigger: FX x Asset-price (multiplicative), matching the
     project's `Buy Intensity = Portfolio Gap x Asset Opportunity x
     Risk Gate x FX Benefit` concept restricted to the Asset Opportunity
     and FX Benefit terms (Portfolio Gap and Risk Gate are held constant
     across all four strategies in this replay so that only the FX/asset
     tilt is being tested).

Every strategy deploys the *same total nominal KRW budget* over the same
weekly dates. Only the timing/weighting of the budget differs. This is a
research script, not a live trading signal.
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
OUT = ROOT / "research/results/fx_accumulation_abcd"
OUT.mkdir(parents=True, exist_ok=True)

START = "2004-01-01"
END = pd.Timestamp.utcnow().tz_localize(None).normalize()

WEEKLY_BASE_KRW = 1_000_000.0  # arbitrary common weekly budget unit
ASSET_HIGH_WINDOW_W = 52       # trailing 52-week high for drawdown tiers
FX_PCTL_WINDOW_W = 156         # trailing 3-year percentile window
FX_PCTL_MIN_PERIODS = 52       # allow start after 1y of history
GOOD_WINDOW_PCTL = 20          # bottom 20th percentile of KRW cost = "good" window
LEAD_LOOKBACK_DAYS = 90        # matches project's primary operating horizon


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
    daily = pd.concat([sp, fx], axis=1).sort_index()
    daily = daily.ffill()
    weekly = daily.resample("W-FRI").last()
    weekly = weekly.dropna(subset=["SP500", "USDKRW"])
    return weekly


def build_signals(weekly: pd.DataFrame) -> pd.DataFrame:
    df = weekly.copy()
    df["krw_cost"] = df["SP500"] * df["USDKRW"]

    roll_high = df["SP500"].rolling(ASSET_HIGH_WINDOW_W, min_periods=ASSET_HIGH_WINDOW_W).max()
    df["asset_drawdown"] = df["SP500"] / roll_high - 1.0

    def pct_rank_last(x: np.ndarray) -> float:
        return float((x <= x[-1]).sum()) / float(len(x)) * 100.0

    df["fx_percentile"] = (
        df["USDKRW"]
        .rolling(FX_PCTL_WINDOW_W, min_periods=FX_PCTL_MIN_PERIODS)
        .apply(pct_rank_last, raw=True)
    )

    # Strategy B raw multiplier: deeper drawdown -> larger tilt.
    dd = df["asset_drawdown"]
    df["raw_B"] = np.select(
        [dd <= -0.20, dd <= -0.10, dd <= -0.05],
        [3.0, 2.0, 1.5],
        default=1.0,
    )
    df.loc[dd.isna(), "raw_B"] = np.nan

    # Strategy C raw multiplier: lower USD/KRW percentile (stronger KRW) -> larger tilt.
    pctl = df["fx_percentile"]
    df["raw_C"] = np.select(
        [pctl < 20, pctl < 40, pctl < 70],
        [2.0, 1.5, 1.0],
        default=0.7,
    )
    df.loc[pctl.isna(), "raw_C"] = np.nan

    df["raw_D"] = df["raw_B"] * df["raw_C"]
    df["raw_A"] = 1.0
    return df


def normalize_and_invest(df: pd.DataFrame) -> pd.DataFrame:
    valid = df.dropna(subset=["raw_B", "raw_C", "raw_D"]).copy()
    n = len(valid)
    for strat in ["A", "B", "C", "D"]:
        raw = valid[f"raw_{strat}"]
        norm = raw * (n / raw.sum())
        valid[f"invested_{strat}"] = norm * WEEKLY_BASE_KRW
        valid[f"shares_{strat}"] = valid[f"invested_{strat}"] / valid["krw_cost"]
    return valid


def strategy_curves(valid: pd.DataFrame, strat: str) -> pd.DataFrame:
    cum_shares = valid[f"shares_{strat}"].cumsum()
    cum_invested = valid[f"invested_{strat}"].cumsum()
    value = cum_shares * valid["krw_cost"]
    value_per_invested = value / cum_invested
    running_peak = value_per_invested.cummax()
    drawdown = value_per_invested / running_peak - 1.0
    return pd.DataFrame(
        {
            "cum_shares": cum_shares,
            "cum_invested": cum_invested,
            "value": value,
            "value_per_invested": value_per_invested,
            "drawdown": drawdown,
        },
        index=valid.index,
    )


def irr_annualized(cashflows: np.ndarray) -> float:
    """Money-weighted annualized return via bisection on an annual rate.

    Exponents use t in years (index / 52) rather than raw weekly steps, so
    a ~20-year, ~1000-period cashflow series does not overflow (1+r)**t.
    """
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


def strategy_metrics(valid: pd.DataFrame, strat: str) -> dict:
    curves = strategy_curves(valid, strat)
    total_invested = float(curves["cum_invested"].iloc[-1])
    final_value = float(curves["value"].iloc[-1])
    total_shares = float(curves["cum_shares"].iloc[-1])
    avg_cost = total_invested / total_shares

    cashflows = -valid[f"invested_{strat}"].to_numpy(dtype=float)
    cashflows = cashflows.copy()
    cashflows[-1] += final_value
    annual_irr = irr_annualized(cashflows)

    mdd = float(curves["drawdown"].min())

    n_weeks = len(valid)
    if strat == "A":
        trigger = pd.Series(False, index=valid.index)
    else:
        trigger = valid[f"raw_{strat}"] > 1.0
    trigger_freq = float(trigger.mean())

    good = valid["krw_cost"] <= valid["krw_cost"].rolling(FX_PCTL_WINDOW_W, min_periods=FX_PCTL_MIN_PERIODS).quantile(GOOD_WINDOW_PCTL / 100.0)
    good = good.fillna(False)
    good_onset = good & ~good.shift(1, fill_value=False)
    trigger_onset = trigger & ~trigger.shift(1, fill_value=False)

    fp_weeks = int((trigger & ~good).sum())
    tp_weeks = int((trigger & good).sum())
    fp_rate = fp_weeks / max(int(trigger.sum()), 1)

    good_run_starts = list(valid.index[good_onset])
    fn = 0
    leads = []
    for start in good_run_starts:
        lookback_start = start - pd.Timedelta(days=LEAD_LOOKBACK_DAYS)
        window_trig = trigger_onset.loc[lookback_start:start]
        run = good.loc[start:]
        run_end_idx = run.index[~run] if (~run).any() else pd.DatetimeIndex([])
        run_end = run_end_idx[0] if len(run_end_idx) else valid.index[-1]
        during = trigger.loc[start:run_end]
        if window_trig.any():
            trig_date = window_trig[window_trig].index[0]
            leads.append((start - trig_date).days)
        elif during.any():
            leads.append(0)
        else:
            fn += 1

    mean_lead = float(np.mean(leads)) if leads else math.nan

    return {
        "strategy": strat,
        "n_weeks": n_weeks,
        "total_invested_krw": total_invested,
        "final_value_krw": final_value,
        "total_return_pct": final_value / total_invested - 1.0,
        "annualized_irr_pct": annual_irr,
        "avg_acquisition_cost_krw_per_index_unit": avg_cost,
        "max_drawdown_pct": mdd,
        "trigger_frequency_pct": trigger_freq,
        "good_windows_n": len(good_run_starts),
        "true_positive_weeks": tp_weeks,
        "false_positive_weeks": fp_weeks,
        "false_positive_rate_of_triggers": fp_rate,
        "false_negative_good_windows": fn,
        "mean_lead_days_when_detected": mean_lead,
    }


def main() -> int:
    weekly = load_weekly()
    signals = build_signals(weekly)
    valid = normalize_and_invest(signals)

    valid.to_csv(OUT / "weekly_panel.csv", index_label="week")

    rows = [strategy_metrics(valid, s) for s in ["A", "B", "C", "D"]]
    summary = pd.DataFrame(rows)
    summary.to_csv(OUT / "strategy_summary.csv", index=False)

    metrics = {
        "data_start": valid.index.min().date().isoformat(),
        "data_end": valid.index.max().date().isoformat(),
        "n_weeks": int(len(valid)),
        "weekly_base_krw": WEEKLY_BASE_KRW,
        "asset_high_window_weeks": ASSET_HIGH_WINDOW_W,
        "fx_percentile_window_weeks": FX_PCTL_WINDOW_W,
        "good_window_percentile": GOOD_WINDOW_PCTL,
        "lead_lookback_days": LEAD_LOOKBACK_DAYS,
        "note": "Research replay only, not a live trading signal. Weekly W-FRI resample of daily Yahoo Finance closes.",
    }
    (OUT / "run_metrics.json").write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# FX Accumulation A/B/C/D Replay — Result",
        "",
        f"Data window: {metrics['data_start']} to {metrics['data_end']} ({metrics['n_weeks']} weeks)",
        f"Common weekly budget unit: KRW {WEEKLY_BASE_KRW:,.0f}",
        "",
        summary.to_string(index=False),
    ]
    (OUT / "RESULT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(summary.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
