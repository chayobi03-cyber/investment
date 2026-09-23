#!/usr/bin/env python3
"""Episode-clustered P0~P6 backtest harness.

P0-P5 are executable when the historical price/market panel and forward
outcomes are present. P6 stays DATA_NOT_READY until archival PIT fundamentals
are connected; no fundamental values are fabricated.

This module never derives a classification false-positive rate from a return
positive-rate complement. A classification target needs an explicit predicted
label and an explicit realized label across a defined target universe.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import median
from typing import Any

from scripts.market_monitor.pit_contract import validate_pit_manifest

HORIZONS = (5, 20, 60)
REQUIRED = {
    "schema_version",
    "date",
    "split",
    "asset_id",
    "episode_id",
    "close",
    "price_signal",
    "price_location_pass",
    "extension_pass",
    "leadership_pass",
    "macro_pass",
    "attribution_pass",
    "fundamentals_pass",
    "entry_open",
    "asset_rows",
}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    out = []
    with path.open(encoding="utf-8") as fh:
        for number, line in enumerate(fh, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            missing = REQUIRED - row.keys()
            if missing:
                raise ValueError(f"line {number}: missing fields {sorted(missing)}")
            out.append(row)
    return out


def signal_level(row: dict[str, Any]) -> int:
    layers = [
        ["price_signal"],
        ["price_signal", "price_location_pass"],
        ["price_signal", "price_location_pass", "extension_pass"],
        ["price_signal", "price_location_pass", "extension_pass", "leadership_pass"],
        ["price_signal", "price_location_pass", "extension_pass", "leadership_pass", "macro_pass"],
        [
            "price_signal",
            "price_location_pass",
            "extension_pass",
            "leadership_pass",
            "macro_pass",
            "attribution_pass",
        ],
        [
            "price_signal",
            "price_location_pass",
            "extension_pass",
            "leadership_pass",
            "macro_pass",
            "attribution_pass",
            "fundamentals_pass",
        ],
    ]
    level = -1
    for index, fields in enumerate(layers):
        if all(bool(row.get(field)) for field in fields):
            level = index
    return level


def dedupe_episode_entries(rows: list[dict[str, Any]], split: str) -> dict[int, list[dict[str, Any]]]:
    selected: dict[tuple[str, str], dict[str, Any]] = {}

    for row in rows:
        if row.get("split") != split:
            continue
        level = signal_level(row)
        if level < 0:
            continue
        key = (str(row["asset_id"]), str(row["episode_id"]))
        current = selected.get(key)
        if current is None or signal_level(current) < level:
            selected[key] = row

    out = {level: [] for level in range(7)}
    for row in selected.values():
        level = signal_level(row)
        for p in range(level + 1):
            out[p].append(row)
    return out


def _forward_metrics(rows: list[dict[str, Any]], horizon: int) -> dict[str, Any]:
    returns: list[float] = []
    maes: list[float] = []
    rebound_sessions: list[int] = []

    for row in rows:
        entry = row.get("entry_open")
        series = row.get("asset_rows")
        if entry is None or not isinstance(series, list) or len(series) < horizon:
            continue

        entry = float(entry)
        future = series[:horizon]
        final_close = float(future[-1]["close"])
        returns.append((final_close / entry - 1.0) * 100.0)

        lows = [float(x["low"]) for x in future if x.get("low") is not None]
        if lows:
            maes.append((min(lows) / entry - 1.0) * 100.0)

        hit = next(
            (index for index, point in enumerate(future, 1) if float(point["close"]) >= entry),
            None,
        )
        if hit is not None:
            rebound_sessions.append(hit)

    return {
        "n_evaluable": len(returns),
        "mean_return_pct": sum(returns) / len(returns) if returns else None,
        "median_return_pct": median(returns) if returns else None,
        "positive_rate": (sum(x > 0 for x in returns) / len(returns)) if returns else None,
        "worst_return_pct": min(returns) if returns else None,
        "max_adverse_excursion_pct": min(maes) if maes else None,
        "post_entry_drawdown_pct": min(maes) if maes else None,
        "time_to_rebound_median_sessions": median(rebound_sessions) if rebound_sessions else None,
    }


def classification_metrics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    pairs = [
        (row.get("signal_predicted_positive"), row.get("actual_positive_label"))
        for row in rows
    ]
    pairs = [(bool(pred), bool(actual)) for pred, actual in pairs if pred is not None and actual is not None]
    if not pairs:
        return {
            "status": "DATA_NOT_READY",
            "reason": (
                "explicit signal_predicted_positive and actual_positive_label "
                "are required across a defined target universe"
            ),
        }

    tp = sum(pred and actual for pred, actual in pairs)
    fp = sum(pred and not actual for pred, actual in pairs)
    tn = sum(not pred and not actual for pred, actual in pairs)
    fn = sum(not pred and actual for pred, actual in pairs)
    predicted_positive = tp + fp
    actual_positive = tp + fn

    return {
        "status": "OK",
        "n": len(pairs),
        "true_positive": tp,
        "false_positive": fp,
        "true_negative": tn,
        "false_negative": fn,
        "false_positive_rate": fp / (fp + tn) if (fp + tn) else None,
        "false_negative_rate": fn / actual_positive if actual_positive else None,
        "positive_predictive_value": tp / predicted_positive if predicted_positive else None,
    }


def metrics(
    rows: list[dict[str, Any]],
    *,
    universe_asset_days: int | None = None,
) -> dict[str, Any]:
    out: dict[str, Any] = {"n_episodes": len(rows)}

    if universe_asset_days:
        out["trigger_frequency_per_100_asset_days"] = (
            len(rows) / universe_asset_days * 100.0
        )
    else:
        out["trigger_frequency_per_100_asset_days"] = None

    for horizon in HORIZONS:
        horizon_metrics = _forward_metrics(rows, horizon)
        for key, value in horizon_metrics.items():
            out[f"{horizon}d_{key}"] = value

    out["classification"] = classification_metrics(rows)
    return out


def _walk_forward(rows: list[dict[str, Any]], universe_asset_days_by_year: dict[str, int]) -> dict[str, Any]:
    years = sorted(
        {
            str(row.get("date", ""))[:4]
            for row in rows
            if str(row.get("date", ""))[:4].isdigit()
        }
    )

    folds: dict[str, Any] = {}
    for year in years:
        test_rows = [row for row in rows if str(row["date"]).startswith(year)]
        if not test_rows:
            continue
        folds[year] = {
            f"P{level}": metrics(
                [row for row in test_rows if signal_level(row) >= level],
                universe_asset_days=universe_asset_days_by_year.get(year),
            )
            for level in range(6)
        }
    return folds


def run(path: Path, manifest_path: Path | None = None) -> dict[str, Any]:
    try:
        rows = load_jsonl(path)
    except ValueError as exc:
        return {"status": "DATA_NOT_READY", "reason": str(exc)}
    if not rows:
        return {"status": "DATA_NOT_READY", "reason": "empty PIT event dataset"}

    missing = REQUIRED - set(rows[0])
    if missing:
        return {"status": "DATA_NOT_READY", "reason": f"missing gate fields: {sorted(missing)}"}

    if not all(isinstance(row.get("asset_rows"), list) for row in rows):
        return {"status": "DATA_NOT_READY", "reason": "forward asset path required"}

    manifest: dict[str, Any] = {}
    if manifest_path and manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    pit_gate = validate_pit_manifest(manifest)
    if manifest.get("pit_status") != "VENDOR_HISTORY_PROXY":
        return {
            "status": "DATA_NOT_READY",
            "reason": "unexpected or missing PIT provenance status",
            "pit_gate": pit_gate,
        }

    if int(manifest.get("pit_rows", 0)) <= 0:
        return {"status": "DATA_NOT_READY", "reason": "no PIT observation rows", "pit_gate": pit_gate}

    universe_asset_days = int(manifest.get("pit_asset_rows", 0) or 0)
    if universe_asset_days <= 0:
        return {"status": "DATA_NOT_READY", "reason": "no asset-level PIT rows", "pit_gate": pit_gate}

    result: dict[str, Any] = {}
    for split in ("development", "validation", "oos"):
        by_level = dedupe_episode_entries(rows, split)
        levels: dict[str, Any] = {}

        previous_return = None
        for level in range(7):
            if level == 6:
                levels["P6"] = {
                    "status": "DATA_NOT_READY",
                    "reason": "archival PIT fundamentals are not connected",
                    "n_episodes": 0,
                }
                continue

            level_rows = by_level[level]
            current = metrics(level_rows, universe_asset_days=universe_asset_days)
            current["status"] = "OK"
            current["level_definition"] = f"P{level}"
            current["incremental_lift_20d_vs_previous_pct"] = (
                current.get("20d_mean_return_pct") - previous_return
                if current.get("20d_mean_return_pct") is not None and previous_return is not None
                else None
            )
            if current.get("20d_mean_return_pct") is not None:
                previous_return = current["20d_mean_return_pct"]
            levels[f"P{level}"] = current

        result[split] = levels

    # Walk-forward is a stability diagnostic over frozen thresholds; it does not
    # fit parameters from test folds.
    by_year = {
        str(year): int(count)
        for year, count in (manifest.get("pit_asset_days_by_year") or {}).items()
    }

    walk_forward: dict[str, Any] = {}
    for level in range(6):
        eligible = [row for row in rows if signal_level(row) >= level]
        walk_forward[f"P{level}"] = _walk_forward(
            eligible,
            by_year,
        )

    return {
        "status": "PARTIAL_OK",
        "pit_status": manifest.get("pit_status"),
        "pit_gate": pit_gate,
        "pit_archival_revisions": bool(manifest.get("pit_archival_revisions")),
        "price_vintage_policy": manifest.get("price_vintage_policy"),
        "fundamentals_status": manifest.get("fundamentals_status", "DATA_NOT_READY"),
        "splits": result,
        "walk_forward_frozen_thresholds": walk_forward,
        "research_note": (
            "P0-P5 are actual episode-clustered results on the historical vendor "
            "price/market panel. Classification false-positive metrics remain "
            "DATA_NOT_READY until explicit prediction and outcome labels exist "
            "across the target universe. P6 is explicitly blocked because archival "
            "PIT fundamental revision data is unavailable. This is research "
            "evidence, not promotion-grade trading validation."
        ),
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=Path)
    ap.add_argument("--manifest", type=Path)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()

    payload = json.dumps(
        run(args.input, args.manifest),
        ensure_ascii=False,
        indent=2,
    )
    if args.output:
        args.output.write_text(payload + "\n", encoding="utf-8")
    print(payload)
