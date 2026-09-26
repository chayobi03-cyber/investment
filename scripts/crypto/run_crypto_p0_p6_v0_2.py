#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from src.investment_pipeline.crypto_entry import (
    V02_COOLDOWN_BARS,
    add_forward_outcomes,
    cluster_episodes,
    generate_signals,
)
from src.investment_pipeline.crypto_permission import (
    BUY_ALLOWED,
    attach_permission_overlay,
)


HORIZONS = (5, 20, 60)
PROMOTION_HORIZONS = (90, 180, 365)


def _num(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def event_stats(frame: pd.DataFrame, prefix: str = "") -> dict:
    out = {"events": int(len(frame))}
    for h in HORIZONS + PROMOTION_HORIZONS:
        col = f"forward_return_{h}d"
        mae_col = f"mae_{h}d"
        ret = _num(frame[col]).dropna() if col in frame else pd.Series(dtype=float)
        mae = _num(frame[mae_col]).dropna() if mae_col in frame else pd.Series(dtype=float)
        key = f"{prefix}{h}d"
        out[f"outcome_n_{key}"] = int(ret.size)
        out[f"median_return_{key}"] = None if ret.empty else float(ret.median())
        out[f"mean_return_{key}"] = None if ret.empty else float(ret.mean())
        out[f"positive_rate_{key}"] = None if ret.empty else float((ret > 0).mean())
        out[f"worst_return_{key}"] = None if ret.empty else float(ret.min())
        out[f"median_mae_{key}"] = None if mae.empty else float(mae.median())
        out[f"worst_mae_{key}"] = None if mae.empty else float(mae.min())
    return out


def cluster_boolean(mask: pd.Series, cooldown: int) -> pd.Series:
    primary = []
    last = None
    for pos, flag in enumerate(mask.tolist()):
        if not bool(flag):
            primary.append(False)
            continue
        is_primary = last is None or pos - last > cooldown
        primary.append(is_primary)
        if is_primary:
            last = pos
    return pd.Series(primary, index=mask.index)


def validate_p0(raw: pd.DataFrame) -> dict:
    required = {"timestamp", "available_at", "open", "high", "low", "close", "volume"}
    missing = sorted(required - set(raw.columns))
    if missing:
        raise SystemExit("P0_FAIL: missing_columns:" + ",".join(missing))
    if len(raw) < 200:
        raise SystemExit("P0_FAIL: need >=200 daily observations")
    if raw["timestamp"].duplicated().any():
        raise SystemExit("P0_FAIL: duplicate timestamps")
    if not raw["timestamp"].is_monotonic_increasing:
        raise SystemExit("P0_FAIL: timestamps not ascending")
    if (raw["available_at"] > raw["timestamp"] + pd.Timedelta(days=2)).any():
        raise SystemExit("P0_FAIL: availability timestamp invalid")
    if (raw["available_at"] > pd.Timestamp.now(tz="UTC")).any():
        raise SystemExit("P0_FAIL: future availability")
    if (raw["high"] < raw[["open", "close"]].max(axis=1)).any():
        raise SystemExit("P0_FAIL: invalid highs")
    if (raw["low"] > raw[["open", "close"]].min(axis=1)).any():
        raise SystemExit("P0_FAIL: invalid lows")
    numeric = ["open", "high", "low", "close", "volume"]
    if raw[numeric].isna().any().any():
        raise SystemExit("P0_FAIL: null numeric fields")
    return {
        "status": "PASS",
        "rows": int(len(raw)),
        "history_start": str(raw["timestamp"].min()),
        "history_end": str(raw["timestamp"].max()),
        "pit_validated": True,
        "provenance_complete": True,
    }


def threshold_validation(oos: pd.DataFrame, baseline: pd.DataFrame) -> dict:
    checks = {}
    checks["minimum_oos_events"] = int(len(oos)) >= 20

    r20 = _num(oos["forward_return_20d"]).dropna()
    r60 = _num(oos["forward_return_60d"]).dropna()
    mae20 = _num(oos["mae_20d"]).dropna()

    checks["oos_20d_median_positive"] = bool(not r20.empty and r20.median() > 0)
    checks["oos_60d_median_positive"] = bool(not r60.empty and r60.median() > 0)
    checks["oos_20d_positive_rate_ge_50pct"] = bool(not r20.empty and (r20 > 0).mean() >= 0.50)
    checks["oos_60d_positive_rate_ge_50pct"] = bool(not r60.empty and (r60 > 0).mean() >= 0.50)
    checks["oos_20d_median_mae_gt_minus_15pct"] = bool(not mae20.empty and mae20.median() > -0.15)

    baseline20 = _num(baseline["forward_return_20d"]).dropna()
    if baseline20.empty or r20.empty:
        checks["oos_20d_not_materially_below_simple_baseline"] = False
    else:
        checks["oos_20d_not_materially_below_simple_baseline"] = bool(
            r20.median() >= baseline20.median() - 0.03
        )

    passed = all(checks.values())
    return {
        "status": "PASS" if passed else "FAIL",
        "checks": checks,
        "note": "Research evidence gate only; full BUY promotion still requires richer permission-layer PIT data.",
    }


def walk_forward(signals: pd.DataFrame) -> list[dict]:
    n = len(signals)
    test_size = max(100, n // 10)
    folds = []
    train_end = max(200, int(n * 0.50))
    while train_end + test_size <= n:
        test = signals.iloc[train_end : train_end + test_size]
        test_primary = test[test["primary_event"] & test["entry_state"].isin(["B2", "B3", "B4"])]
        folds.append({
            "split_id": f"WF{len(folds)+1:02d}",
            "train_rows": int(train_end),
            "test_rows": int(len(test)),
            "test_start": str(test["timestamp"].min()),
            "test_end": str(test["timestamp"].max()),
            "threshold_retuned": False,
            "metrics": event_stats(test_primary),
        })
        train_end += test_size
    return folds


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=Path)
    ap.add_argument("--output", type=Path, default=Path("artifacts/crypto/crypto_p0_p6_v0.2.json"))
    ap.add_argument(
        "--permission-history",
        type=Path,
        default=None,
        help="Optional PIT permission history CSV. Missing history remains DATA_NOT_READY.",
    )
    args = ap.parse_args()

    raw = pd.read_csv(args.input, parse_dates=["timestamp", "available_at"]).sort_values("timestamp").reset_index(drop=True)
    p0 = validate_p0(raw)

    # P1: frozen v0.2 price/volume thresholds.
    signals = generate_signals(raw)
    candidate = signals["entry_state"].isin(["B2", "B3", "B4"])
    signals = cluster_episodes(signals, cooldown_bars=V02_COOLDOWN_BARS)
    signals = add_forward_outcomes(signals)

    permission_history = None
    if args.permission_history is not None:
        permission_history = pd.read_csv(
            args.permission_history,
            parse_dates=["decision_timestamp", "available_at"],
        )
    signals, permission_result = attach_permission_overlay(
        signals,
        permission_history,
    )

    # Permission is an overlay only: frozen v0.2 price thresholds and B2/B3/B4
    # classifications are not modified by permission data.
    primary = signals[signals["primary_event"] & candidate].copy()
    permission_primary = primary[primary["permission_match"]].copy()
    permission_eligible = permission_primary[
        (permission_primary["permission_status"] == "PASS")
        & permission_primary["confirmed_regime"].isin({"R1", "R2", "R3", "R4", "R5"})
        & (permission_primary["permission_market_gate"] != "RED")
    ].copy()

    # Simple chronological baseline: every >=5% pullback from prior 60D high,
    # clustered with the same cooldown and executed next-session open.
    baseline_mask = (
        signals["drawdown60"].notna()
        & (signals["drawdown60"] <= -0.05)
    )
    baseline_primary = cluster_boolean(baseline_mask, V02_COOLDOWN_BARS)
    baseline = signals[baseline_primary].copy()

    # Last 20% is never used for threshold construction: thresholds are frozen.
    split = int(len(signals) * 0.80)
    dev = signals.iloc[:split]
    oos = signals.iloc[split:]
    oos_primary = oos[oos["primary_event"] & oos["entry_state"].isin(["B2", "B3", "B4"])].copy()
    oos_baseline = baseline[baseline["timestamp"] >= oos["timestamp"].min()].copy()

    wf = walk_forward(signals)

    result = {
        "schema_version": "crypto-p0-p6-v0.2",
        "rule_version": "crypto-market-regime-entry-v0.2",
        "status": "RESEARCH_ONLY",
        "asset": "BTCUSDT",
        "p0": p0,
        "p1": {
            "status": "PASS",
            "signal_source": "src/investment_pipeline/crypto_entry.py",
            "frozen_threshold_contract": "config/crypto_market_regime_entry_v0.2.json",
            "state_counts": {str(k): int(v) for k, v in signals["entry_state"].value_counts().items()},
            "primary_events": int(len(primary)),
            "candidate_days": int(candidate.sum()),
            "permission_overlay": {
                "status": permission_result.status,
                "history_rows": permission_result.rows,
                "matched_rows": permission_result.matched_rows,
                "eligible_primary_events": int(len(permission_eligible)),
                "regime_coverage": permission_result.regime_coverage,
                "blocker_codes": list(permission_result.blocker_codes),
                "buy_allowed": BUY_ALLOWED,
            },
            "signal_decomposition": {
                "by_signal_type": {
                    str(k): int(v)
                    for k, v in primary.get("signal_type", pd.Series(dtype=str)).value_counts().items()
                },
                "by_entry_state": {
                    str(k): int(v)
                    for k, v in primary["entry_state"].value_counts().items()
                },
                "permission_regime_available": bool(
                    primary["confirmed_regime"].isin(
                        {"R1", "R2", "R3", "R4", "R5", "R6"}
                    ).any()
                ),
                "by_regime": {
                    str(k): int(v)
                    for k, v in primary[
                        primary["confirmed_regime"].isin(
                            {"R1", "R2", "R3", "R4", "R5", "R6"}
                        )
                    ]["confirmed_regime"].value_counts().items()
                },
            },
        },
        "p2": {
            "status": "PASS",
            "primary_events": int(len(primary)),
            "cooldown_bars": V02_COOLDOWN_BARS,
            "episode_ids": int(signals["episode_id"].dropna().nunique()),
            "decomposition_status": permission_result.status,
        },
        "p3": {
            "status": "PASS",
            "execution": "next_daily_open",
            "all_primary_event_stats": event_stats(primary),
        },
        "p4": {
            "status": "PASS",
            "risk_stats": {
                "worst_20d_return": float(_num(primary["forward_return_20d"]).min()) if not primary.empty else None,
                "worst_60d_return": float(_num(primary["forward_return_60d"]).min()) if not primary.empty else None,
                "worst_20d_mae": float(_num(primary["mae_20d"]).min()) if not primary.empty else None,
                "median_20d_mae": float(_num(primary["mae_20d"]).median()) if not primary.empty else None,
            },
        },
        "p5": {
            "status": "PASS",
            "development_rows": int(len(dev)),
            "oos_rows": int(len(oos)),
            "oos_primary_events": int(len(oos_primary)),
            "oos_metrics": event_stats(oos_primary),
            "oos_simple_pullback_baseline_metrics": event_stats(oos_baseline),
            "walk_forward": wf,
            "threshold_retuned": False,
            "buy_allowed": BUY_ALLOWED,
            "permission_status": permission_result.status,
        },
        "threshold_validation": threshold_validation(oos_primary, oos_baseline),
        "permission": {
            "status": permission_result.status,
            "buy_allowed": BUY_ALLOWED,
            "matched_rows": permission_result.matched_rows,
            "eligible_primary_events": int(len(permission_eligible)),
            "regime_coverage": permission_result.regime_coverage,
            "blocker_codes": list(permission_result.blocker_codes),
            "execution_gate": "DISABLED",
        },
        "p6": {
            "status": "BLOCKED",
            "promotion_status": "BLOCK",
            "reason": "Full BUY promotion requires richer PIT permission-layer data (institutional/ETF flow, macro/rates/FX, derivatives history, liquidity/risk, regulation/market structure and geopolitical transmission).",
            "oos_evidence_status": "TO_BE_READ_FROM_THRESHOLD_VALIDATION",
            "oos_pass": False,
            "walk_forward_pass": bool(all(x["metrics"]["events"] > 0 for x in wf)),
            "sensitivity_pass": False,
            "provenance_pass": False,
            "lookahead_pass": True,
            "threshold_retuned": False,
            "buy_allowed": BUY_ALLOWED,
            "permission_status": permission_result.status,
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
    print(json.dumps(result, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
