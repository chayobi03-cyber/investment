#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from src.investment_pipeline.crypto_entry import (
    add_forward_outcomes,
    cluster_episodes,
    generate_signals,
)


def median_or_none(series: pd.Series) -> float | None:
    s = pd.to_numeric(series, errors="coerce").dropna()
    return None if s.empty else float(s.median())


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=Path)
    ap.add_argument("--output", type=Path, default=Path("artifacts/crypto/btc_entry_backtest.json"))
    args = ap.parse_args()

    raw = pd.read_csv(args.input, parse_dates=["timestamp", "available_at"])
    raw = raw.sort_values("timestamp").reset_index(drop=True)

    # P0: Data QA / PIT.
    if len(raw) < 200:
        raise SystemExit("P0_FAIL: need >=200 daily observations")
    if raw["timestamp"].duplicated().any():
        raise SystemExit("P0_FAIL: duplicate timestamps")
    if not raw["timestamp"].is_monotonic_increasing:
        raise SystemExit("P0_FAIL: timestamps not ascending")
    if (raw["available_at"] > raw["timestamp"] + pd.Timedelta(days=2)).any():
        raise SystemExit("P0_FAIL: unexpected availability lag")
    if (raw["high"] < raw[["open", "close"]].max(axis=1)).any():
        raise SystemExit("P0_FAIL: invalid highs")
    if (raw["low"] > raw[["open", "close"]].min(axis=1)).any():
        raise SystemExit("P0_FAIL: invalid lows")

    # P1: deterministic timing signal.
    sig = generate_signals(raw)

    # P2: episode clustering.
    sig = cluster_episodes(sig, cooldown_bars=5)

    # P3/P4: next-session execution and forward outcomes.
    sig = add_forward_outcomes(sig)

    candidate_mask = sig["entry_state"].isin(["B2", "B3", "B4"])
    primary_mask = sig["primary_event"] & candidate_mask
    primary = sig[primary_mask]
    candidates = sig[candidate_mask]

    def stats(frame: pd.DataFrame) -> dict:
        return {
            "events": int(len(frame)),
            "median_forward_return_5d": median_or_none(frame["forward_return_5d"]),
            "median_forward_return_20d": median_or_none(frame["forward_return_20d"]),
            "median_forward_return_60d": median_or_none(frame["forward_return_60d"]),
            "median_mae_20d": median_or_none(frame["mae_20d"]),
            "median_mfe_20d": median_or_none(frame["mfe_20d"]),
        }

    state_stats = {
        state: stats(primary[primary["entry_state"] == state])
        for state in ["B2", "B3", "B4"]
    }

    # P5: chronological walk-forward with fixed preregistered rules.
    split = int(len(sig) * 0.70)
    dev = sig.iloc[:split]
    oos = sig.iloc[split:]
    oos_primary = oos[
        oos["primary_event"] & oos["entry_state"].isin(["B2", "B3", "B4"])
    ]

    result = {
        "status": "RESEARCH_ONLY",
        "p0": {
            "status": "PASS",
            "rows": int(len(raw)),
            "start": str(raw["timestamp"].min()),
            "end": str(raw["timestamp"].max()),
        },
        "p1": {
            "status": "PASS",
            "state_counts": {
                str(k): int(v) for k, v in sig["entry_state"].value_counts().items()
            },
            "candidate_days": int(len(candidates)),
        },
        "p2": {
            "status": "PASS",
            "primary_events": int(len(primary)),
            "cooldown_bars": 5,
        },
        "p3_p4": {
            "status": "PASS",
            "all_primary_event_stats": stats(primary),
            "state_stats": state_stats,
        },
        "p5": {
            "status": "PASS",
            "development_rows": int(len(dev)),
            "oos_rows": int(len(oos)),
            "oos_primary_events": int(len(oos_primary)),
            "oos_median_forward_return_20d": median_or_none(
                oos_primary["forward_return_20d"]
            ),
            "oos_median_mae_20d": median_or_none(oos_primary["mae_20d"]),
        },
        "p6": {
            "status": "DATA_NOT_READY",
            "reason": "price_only_run; richer permission-layer PIT history is required",
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
    print(json.dumps(result, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
