#!/usr/bin/env python3
"""Per-asset review of the frozen v0.2 entry rule and a volatility-scaled variant.

Contract: config/crypto_asset_review_v0.1.json. Research only; nothing here
changes the frozen thresholds, the live monitor or buy permission.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

from scripts.crypto.run_crypto_p0_p6_v0_2 import (
    cluster_boolean,
    event_stats,
    fold_boundaries,
    threshold_validation,
    validate_p0,
)
from src.investment_pipeline.crypto_entry import (
    V02_COOLDOWN_BARS,
    add_entry_features,
    add_forward_outcomes,
    cluster_episodes,
    signal_from_row,
)

CANDIDATE_STATES = ("B2", "B3", "B4")
DAY = pd.Timedelta(1, unit="D")


def latest_contiguous(frame: pd.DataFrame, max_gap_days: int) -> tuple[pd.DataFrame, int]:
    """Keep the most recent run of bars without a gap (e.g. a relisted product)."""
    gaps = frame["timestamp"].diff() > max_gap_days * DAY
    if not gaps.any():
        return frame.reset_index(drop=True), 0
    start = gaps[gaps].index[-1]
    return frame.loc[start:].reset_index(drop=True), int(gaps.sum())


def log_returns(frame: pd.DataFrame) -> pd.Series:
    return np.log(frame.set_index("timestamp")["close"]).diff().dropna()


def scale_factor(asset: pd.DataFrame, btc: pd.DataFrame, rows: int, cfg: dict) -> float:
    """k = sigma(asset) / sigma(BTC) over the asset's first `rows` bars only."""
    window = asset.iloc[:rows]
    a = log_returns(window)
    b = log_returns(btc).loc[lambda s: (s.index >= window["timestamp"].min()) & (s.index <= window["timestamp"].max())]
    common = a.index.intersection(b.index)
    if len(common) < 60:
        return 1.0
    k = float(a.loc[common].std() / b.loc[common].std())
    lo, hi = cfg["k_clip"]
    return round(min(max(k, lo), hi), cfg["k_rounding_decimals"])


def signals_for(raw: pd.DataFrame, k: float) -> pd.DataFrame:
    """Frozen classifier on drawdown60 / k. k = 1 reproduces generate_signals exactly."""
    df = add_entry_features(raw)
    raw_dd = df["drawdown60"].copy()
    if k != 1.0:
        dd = raw_dd / k
        df["drawdown60"] = dd
        df["zone"] = "Z3"
        df.loc[dd.isna(), "zone"] = "UNKNOWN"
        df.loc[dd > -0.05, "zone"] = "Z0"
        df.loc[(dd <= -0.05) & (dd > -0.08), "zone"] = "Z1"
        df.loc[(dd <= -0.08) & (dd > -0.12), "zone"] = "Z2"
    sig = df.apply(signal_from_row, axis=1)
    df["entry_state"] = sig.map(lambda s: s.state)
    df["entry_reason"] = sig.map(lambda s: "|".join(s.reason_codes))
    df["drawdown60"] = raw_dd  # outcomes and the baseline use real drawdowns
    df = cluster_episodes(df, cooldown_bars=V02_COOLDOWN_BARS)
    return add_forward_outcomes(df)


def primary_events(signals: pd.DataFrame) -> pd.DataFrame:
    return signals[signals["primary_event"] & signals["entry_state"].isin(CANDIDATE_STATES)]


def baseline_events(signals: pd.DataFrame) -> pd.DataFrame:
    mask = signals["drawdown60"].notna() & (signals["drawdown60"] <= -0.05)
    return signals[cluster_boolean(mask, V02_COOLDOWN_BARS)]


def walk_forward_summary(raw: pd.DataFrame, btc: pd.DataFrame, cfg: dict | None) -> dict:
    """Same fold layout as run_crypto_p0_p6_v0_2.walk_forward; k re-fit per fold when scaled."""
    folds = []
    frozen = signals_for(raw, 1.0) if cfg is None else None
    for fold in fold_boundaries(len(raw)):
        k = 1.0 if cfg is None else scale_factor(raw, btc, fold["train_rows"], cfg)
        signals = frozen if frozen is not None else signals_for(raw, k)
        test = signals.iloc[fold["test_start"] : fold["test_end"]]
        r20 = pd.to_numeric(primary_events(test)["forward_return_20d"], errors="coerce").dropna()
        folds.append({
            "test_start": str(test["timestamp"].min().date()),
            "k": k,
            "events": int(len(primary_events(test))),
            "median_return_20d": None if r20.empty else float(r20.median()),
        })
    with_events = [f for f in folds if f["events"] > 0]
    return {
        "folds": folds,
        "folds_total": len(folds),
        "folds_with_events": len(with_events),
        "folds_positive_median_20d": sum(1 for f in with_events if (f["median_return_20d"] or 0) > 0),
    }


def evaluate(raw: pd.DataFrame, btc: pd.DataFrame, k: float, oos_fraction: float, wf_cfg: dict | None) -> dict:
    signals = signals_for(raw, k)
    split = int(len(signals) * (1 - oos_fraction))
    oos = signals.iloc[split:]
    oos_primary = primary_events(oos)
    oos_baseline = baseline_events(signals).loc[lambda b: b["timestamp"] >= oos["timestamp"].min()]
    gate = threshold_validation(oos_primary, oos_baseline)
    stats = event_stats(oos_primary)
    return {
        "k": k,
        "zone_depths": {"Z1": round(-0.05 * k, 4), "Z2": round(-0.08 * k, 4), "Z3": round(-0.12 * k, 4)},
        "oos_start": str(oos["timestamp"].min().date()),
        "oos_primary_events": int(len(oos_primary)),
        "threshold_validation": gate,
        "checks_passed": sum(gate["checks"].values()),
        "oos_metrics": {
            key: stats[key]
            for key in (
                "median_return_20d", "positive_rate_20d", "median_return_60d", "positive_rate_60d",
                "median_mae_20d", "worst_mae_20d", "worst_return_60d",
            )
        },
        "oos_baseline_median_return_20d": event_stats(oos_baseline)["median_return_20d"],
        "walk_forward": walk_forward_summary(raw, btc, wf_cfg),
        "current_state": str(signals["entry_state"].iloc[-1]),
    }


def profile(raw: pd.DataFrame, btc: pd.DataFrame) -> dict:
    a, b = log_returns(raw), log_returns(btc)
    common = a.index.intersection(b.index)
    close = raw["close"]
    usd_volume = (raw["close"] * raw["volume"]).tail(90)
    return {
        "rows": int(len(raw)),
        "start": str(raw["timestamp"].min().date()),
        "end": str(raw["timestamp"].max().date()),
        "history_days": int((raw["timestamp"].max() - raw["timestamp"].min()) / DAY) + 1,
        "median_usd_volume_90d": float(usd_volume.median()),
        "annualized_vol": float(a.std() * math.sqrt(365)),
        "vol_ratio_vs_btc": float(a.loc[common].std() / b.loc[common].std()) if len(common) > 60 else None,
        "corr_vs_btc": float(a.loc[common].corr(b.loc[common])) if len(common) > 60 else None,
        "max_drawdown": float((close / close.cummax() - 1).min()),
        "current_drawdown_from_ath": float(close.iloc[-1] / close.max() - 1),
    }


def rule_fit(variants: dict) -> str:
    passed = [name for name, v in variants.items() if v["threshold_validation"]["status"] == "PASS"]
    if not passed:
        return "NEITHER_PASS"
    return "BOTH_PASS" if len(passed) == 2 else f"{passed[0].upper()}_PASS"


def tier(screen_ok: bool, variants: dict) -> str:
    if screen_ok and any(v["threshold_validation"]["status"] == "PASS" for v in variants.values()):
        return "ADD_TO_MONITOR_CANDIDATE"
    if screen_ok and max(v["checks_passed"] for v in variants.values()) >= 5:
        return "WATCH"
    return "NOT_RECOMMENDED"


def review_asset(sym: str, raw: pd.DataFrame, btc: pd.DataFrame, cfg: dict) -> dict:
    raw, gaps = latest_contiguous(raw, cfg["history"]["max_gap_days"])
    try:
        validate_p0(raw)
    except SystemExit as exc:  # one bad series must not abort the other assets
        return {"asset": sym, "status": "P0_FAIL", "reason": str(exc), "rows": int(len(raw)), "gaps_dropped": gaps}
    if len(raw) < 400:
        return {"asset": sym, "status": "DATA_NOT_READY", "rows": int(len(raw)), "gaps_dropped": gaps}

    oos_fraction = cfg["evaluation"]["oos_fraction"]
    dev_rows = int(len(raw) * (1 - oos_fraction))
    scaled_cfg = cfg["scaled_variant"]
    k = 1.0 if sym == cfg["benchmark"] else scale_factor(raw, btc, dev_rows, scaled_cfg)

    prof = profile(raw, btc)
    screen = {
        "history_ok": prof["history_days"] >= cfg["screen"]["min_history_days"],
        "liquidity_ok": prof["median_usd_volume_90d"] >= cfg["screen"]["min_median_usd_volume_90d"],
    }
    variants = {"frozen": evaluate(raw, btc, 1.0, oos_fraction, None)}
    if k != 1.0:
        variants["scaled"] = evaluate(raw, btc, k, oos_fraction, scaled_cfg)
    best = max(variants.values(), key=lambda v: v["checks_passed"])
    return {
        "asset": sym,
        "status": "REVIEWED",
        "gaps_dropped": gaps,
        "profile": prof,
        "screen": screen,
        "variants": variants,
        "best_checks_passed": best["checks_passed"],
        "rule_fit": rule_fit(variants),
        "tier": "MONITORED" if sym in cfg["monitored"] else tier(all(screen.values()), variants),
    }


def rank_key(r: dict):
    best = max(r["variants"].values(), key=lambda v: v["checks_passed"])
    mae = best["oos_metrics"]["worst_mae_20d"]
    corr = r["profile"]["corr_vs_btc"]
    return (-r["best_checks_passed"], -(mae if mae is not None else -9), corr if corr is not None else 9)


def markdown(result: dict) -> str:
    pct = lambda x: "—" if x is None else f"{x * 100:.1f}%"
    lines = [
        "## Crypto asset review v0.1 (research only)",
        "",
        "| Asset | Tier | Rule fit | History | 90D USD vol | Vol×BTC | Corr | k | Frozen gate | Scaled gate | OOS evts F/S | OOS med 20D F/S | Worst 20D MAE F/S | WF folds +/events/total (F) | Now |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in result["assets"]:
        if r["status"] != "REVIEWED":
            lines.append(f"| {r['asset']} | {r['status']} | | {r.get('rows', 0)} rows | | | | | | | | | | | |")
            continue
        p, v = r["profile"], r["variants"]
        f, s = v["frozen"], v.get("scaled")
        both = lambda key: f"{pct(f['oos_metrics'][key])} / {pct(s['oos_metrics'][key]) if s else '—'}"
        wf = f["walk_forward"]
        lines.append(
            f"| {r['asset']} | {r['tier']} | {r['rule_fit']} | {p['history_days']}d | ${p['median_usd_volume_90d'] / 1e6:,.0f}M "
            f"| {p['vol_ratio_vs_btc'] or 1:.2f} | {p['corr_vs_btc'] or 1:.2f} | {s['k'] if s else 1.0} "
            f"| {f['threshold_validation']['status']} {f['checks_passed']}/7 "
            f"| {(s['threshold_validation']['status'] + ' ' + str(s['checks_passed']) + '/7') if s else '—'} "
            f"| {f['oos_primary_events']} / {s['oos_primary_events'] if s else '—'} "
            f"| {both('median_return_20d')} | {both('worst_mae_20d')} "
            f"| {wf['folds_positive_median_20d']}/{wf['folds_with_events']}/{wf['folds_total']} "
            f"| {(s or f)['current_state']} |"
        )
    lines += ["", "Recommendation order: " + (", ".join(result["recommendation_order"]) or "none")]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=Path, help="CSV from fetch_multi_asset_daily.py")
    ap.add_argument("--config", type=Path, default=Path("config/crypto_asset_review_v0.1.json"))
    ap.add_argument("--output", type=Path, default=Path("artifacts/crypto/asset_review_v0.1.json"))
    ap.add_argument("--summary", type=Path, default=None, help="Optional markdown summary path")
    args = ap.parse_args()

    cfg = json.loads(args.config.read_text(encoding="utf-8"))
    data = pd.read_csv(args.input, parse_dates=["timestamp", "available_at"])
    by_asset = {
        sym: g.sort_values("timestamp").drop_duplicates("timestamp").reset_index(drop=True)
        for sym, g in data.groupby("asset")
    }
    btc_sym = cfg["benchmark"]
    if btc_sym not in by_asset:
        raise SystemExit("DATA_NOT_READY: benchmark BTC missing")
    btc = by_asset[btc_sym]

    order = cfg["monitored"] + cfg["candidates"]
    assets = [review_asset(sym, by_asset[sym], btc, cfg) for sym in order if sym in by_asset]
    missing = [sym for sym in order if sym not in by_asset]
    reviewed_candidates = [
        r for r in assets if r["status"] == "REVIEWED" and r["asset"] in cfg["candidates"]
    ]
    tiers = ("ADD_TO_MONITOR_CANDIDATE", "WATCH", "NOT_RECOMMENDED")
    ranked = sorted(reviewed_candidates, key=lambda r: (tiers.index(r["tier"]), rank_key(r)))

    result = {
        "schema_version": "crypto-asset-review-v0.1",
        "status": "RESEARCH_ONLY",
        "rule_version": "crypto-market-regime-entry-v0.2",
        "contract": str(args.config),
        "buy_allowed": False,
        "assets": assets,
        "missing_assets": missing,
        "recommendation_order": [f"{r['asset']}:{r['tier']}" for r in ranked],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
    md = markdown(result)
    if args.summary:
        args.summary.write_text(md + "\n", encoding="utf-8")
    print(md)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
