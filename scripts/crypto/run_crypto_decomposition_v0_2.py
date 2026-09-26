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
from src.investment_pipeline.signal_decomposition_agent import (
    SignalDecompositionAgent,
)

OUTCOME_HORIZONS = (5, 20, 60, 90, 180, 365)
CANDIDATE_STATES = {"B2", "B3", "B4"}


def _num(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def add_signal_type(signals: pd.DataFrame) -> pd.DataFrame:
    """Backward-compatible wrapper around the deterministic decomposition agent."""
    out = SignalDecompositionAgent().apply(signals)
    out["signal_type"] = out["signal_type"].str.lower()
    return out


def summarize(frame: pd.DataFrame) -> dict:
    out = {"events": int(len(frame))}
    for h in OUTCOME_HORIZONS:
        ret_col = f"forward_return_{h}d"
        mae_col = f"mae_{h}d"
        ret = _num(frame[ret_col]).dropna() if ret_col in frame else pd.Series(dtype=float)
        mae = _num(frame[mae_col]).dropna() if mae_col in frame else pd.Series(dtype=float)
        out[f"outcome_n_{h}d"] = int(ret.size)
        out[f"median_return_{h}d"] = None if ret.empty else float(ret.median())
        out[f"positive_rate_{h}d"] = None if ret.empty else float((ret > 0).mean())
        out[f"worst_return_{h}d"] = None if ret.empty else float(ret.min())
        out[f"median_mae_{h}d"] = None if mae.empty else float(mae.median())
    return out


def grouped_summary(frame: pd.DataFrame, group_cols: list[str]) -> list[dict]:
    if frame.empty:
        return []
    rows: list[dict] = []
    for key, group in frame.groupby(group_cols, dropna=False, sort=True):
        if not isinstance(key, tuple):
            key = (key,)
        row = {
            col: (None if pd.isna(value) else value)
            for col, value in zip(group_cols, key)
        }
        row.update(summarize(group))
        rows.append(row)
    return rows


def fold_boundaries(n: int) -> list[dict]:
    if n <= 0:
        return []
    test_size = max(100, n // 10)
    train_end = max(200, int(n * 0.50))
    folds: list[dict] = []
    while train_end + test_size <= n:
        folds.append(
            {
                "split_id": f"WF{len(folds) + 1:02d}",
                "train_rows": int(train_end),
                "test_start": int(train_end),
                "test_end": int(train_end + test_size),
            }
        )
        train_end += test_size
    return folds


def prepare_primary(raw: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    required = {"timestamp", "open", "high", "low", "close", "volume"}
    missing = sorted(required - set(raw.columns))
    if missing:
        raise SystemExit("DECOMPOSITION_FAIL: missing_columns:" + ",".join(missing))

    signals = generate_signals(raw.sort_values("timestamp").reset_index(drop=True))
    signals = cluster_episodes(signals, cooldown_bars=V02_COOLDOWN_BARS)
    signals = add_forward_outcomes(signals)
    signals = add_signal_type(signals)

    primary = signals[
        signals["primary_event"] & signals["entry_state"].isin(CANDIDATE_STATES)
    ].copy()
    primary["year"] = primary["timestamp"].dt.year.astype(int)
    return primary, signals


def decompose(
    raw: pd.DataFrame,
    oos_fraction: float = 0.20,
    permission_history: pd.DataFrame | None = None,
) -> dict:
    primary, signals = prepare_primary(raw)
    signals, permission_result = attach_permission_overlay(
        signals,
        permission_history,
    )
    signals = SignalDecompositionAgent().apply(signals)
    primary = signals[
        signals["primary_event"] & signals["entry_state"].isin(CANDIDATE_STATES)
    ].copy()

    split = int(len(signals) * (1.0 - oos_fraction))
    oos = primary[primary.index >= split].copy()
    oos_permission_eligible = oos[
        (oos["permission_status"] == "PASS")
        & oos["confirmed_regime"].isin({"R1", "R2", "R3", "R4", "R5"})
        & (oos["permission_market_gate"] != "RED")
    ].copy()

    wf_rows: list[dict] = []
    for fold in fold_boundaries(len(signals)):
        test = primary[
            (primary.index >= fold["test_start"])
            & (primary.index < fold["test_end"])
        ].copy()
        wf_rows.append(
            {
                **fold,
                "events": int(len(test)),
                "by_signal_type": grouped_summary(test, ["signal_type"]),
                "by_zone": grouped_summary(test, ["zone"]),
                "by_entry_state": grouped_summary(test, ["entry_state"]),
                "by_regime_and_signal_type": grouped_summary(
                    test, ["decomposition_regime", "signal_type"]
                ),
                "by_regime_and_entry_state": grouped_summary(
                    test, ["decomposition_regime", "entry_state"]
                ),
                "by_regime_state_signal": grouped_summary(
                    test,
                    ["decomposition_regime", "entry_state", "signal_type"],
                ),
            }
        )

    result = {
        "schema_version": "crypto-decomposition-v0.2",
        "rule_version": "crypto-market-regime-entry-v0.2",
        "status": "RESEARCH_ONLY",
        "threshold_retuned": False,
        "cooldown_bars": V02_COOLDOWN_BARS,
        "full_sample": {
            "rows": int(len(signals)),
            "primary_events": int(len(primary)),
            "by_signal_type": grouped_summary(primary, ["signal_type"]),
            "by_zone": grouped_summary(primary, ["zone"]),
            "by_entry_state": grouped_summary(primary, ["entry_state"]),
            "by_signal_type_and_entry_state": grouped_summary(
                primary, ["signal_type", "entry_state"]
            ),
            "by_year": grouped_summary(primary, ["year"]),
        },
        "fixed_oos": {
            "split_rule": "last_20_percent_of_chronological_signal_history",
            "split_index": int(split),
            "primary_events": int(len(oos)),
            "by_signal_type": grouped_summary(oos, ["signal_type"]),
            "by_zone": grouped_summary(oos, ["zone"]),
            "by_entry_state": grouped_summary(oos, ["entry_state"]),
            "by_signal_type_and_entry_state": grouped_summary(
                oos, ["signal_type", "entry_state"]
            ),
            "permission_eligible_primary_events": int(len(oos_permission_eligible)),
        },
        "permission_overlay": {
            "status": permission_result.status,
            "history_rows": permission_result.rows,
            "matched_rows": permission_result.matched_rows,
            "eligible_primary_events": int(permission_result.eligible_rows),
            "regime_coverage": permission_result.regime_coverage,
            "blocker_codes": list(permission_result.blocker_codes),
            "buy_allowed": BUY_ALLOWED,
        },
        "market_regime": {
            "status": (
                "AVAILABLE"
                if primary["decomposition_regime"].isin(
                    {"R1", "R2", "R3", "R4", "R5", "R6"}
                ).any()
                else "DATA_NOT_READY"
            ),
            "column": "decomposition_regime",
            "by_regime": grouped_summary(primary, ["decomposition_regime"]),
            "oos_by_regime": grouped_summary(oos, ["decomposition_regime"]),
            "by_regime_and_signal_type": grouped_summary(
                primary, ["decomposition_regime", "signal_type"]
            ),
            "oos_by_regime_and_signal_type": grouped_summary(
                oos, ["decomposition_regime", "signal_type"]
            ),
            "by_regime_and_entry_state": grouped_summary(
                primary, ["decomposition_regime", "entry_state"]
            ),
            "oos_by_regime_and_entry_state": grouped_summary(
                oos, ["decomposition_regime", "entry_state"]
            ),
            "by_regime_state_signal": grouped_summary(
                primary,
                ["decomposition_regime", "entry_state", "signal_type"],
            ),
            "oos_by_regime_state_signal": grouped_summary(
                oos,
                ["decomposition_regime", "entry_state", "signal_type"],
            ),
        },
        "walk_forward": wf_rows,
        "guardrails": [
            "No threshold was changed after observing OOS results.",
            "Next-open execution is preserved from the v0.2 contract.",
            "This artifact is decomposition evidence only; it cannot promote P6.",
        ],
    }
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=Path)
    ap.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/crypto/crypto_decomposition_v0.2.json"),
    )
    ap.add_argument(
        "--permission-history",
        type=Path,
        default=None,
        help="Optional PIT permission history CSV used only for regime decomposition.",
    )
    args = ap.parse_args()

    raw = pd.read_csv(
        args.input,
        parse_dates=["timestamp", "available_at"],
    )
    permission_history = None
    if args.permission_history is not None:
        permission_history = pd.read_csv(
            args.permission_history,
            parse_dates=["decision_timestamp", "available_at"],
        )
    result = decompose(raw, permission_history=permission_history)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, indent=2, default=str),
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
