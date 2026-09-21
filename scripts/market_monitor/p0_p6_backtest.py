#!/usr/bin/env python3
"""Episode-clustered P0~P6 backtest harness.

P0-P5 are executable when the historical PIT-like price/market panel and
forward outcomes are present. P6 stays DATA_NOT_READY until archival PIT
fundamentals are connected; no fundamental values are fabricated.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import median
from typing import Any

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
    opportunity_labels: list[bool] = []

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

        if row.get("entry_opportunity_label") is not None:
            opportunity_labels.append(bool(row["entry_opportunity_label"]))

    result = {
        "n_evaluable": len(returns),
        "mean_return_pct": sum(returns) / len(returns) if returns else None,
        "median_return_pct": median(returns) if returns else None,
        "positive_rate": (sum(x > 0 for x in returns) / len(returns)) if returns else None,
        "worst_return_pct": min(returns) if returns else None,
        "max_adverse_excursion_pct": min(maes) if maes else None,
        "post_entry_drawdown_pct": min(maes) if maes else None,
        "time_to_rebound_median_sessions": median(rebound_sessions) if rebound_sessions else None,
    }
    if opportunity_labels:
        result["false_positive_rate"] = 1.0 - (sum(opportunity_labels) / len(opportunity_labels))
        result["opportunity_base_n"] = len(opportunity_labels)
    return result


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
    rows = load_jsonl(path)
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

    if manifest.get("pit_status") != "VENDOR_HISTORY_PROXY":
        return {
            "status": "DATA_NOT_READY",
            "reason": "unexpected or missing PIT provenance status",
        }

    if int(manifest.get("pit_rows", 0)) <= 0:
        return {"status": "DATA_NOT_READY", "reason": "no PIT observation rows"}

    asset_count = int(manifest.get("asset_count", 0) or 0)
    universe_asset_days = (
        int(manifest["pit_rows"] / asset_count)
        if asset_count > 0
        else None
    )

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
    by_year: dict[str, int] = {}
    for row in rows:
        year = str(row["date"])[:4]
        by_year[year] = by_year.get(year, 0) + 1

    walk_forward: dict[str, Any] = {}
    for level in range(6):
        eligible = [row for row in rows if signal_level(row) >= level]
        walk_forward[f"P{level}"] = _walk_forward(
            eligible,
            {year: max(1, count) for year, count in by_year.items()},
        )

    return {
        "status": "PARTIAL_OK",
        "pit_status": manifest.get("pit_status"),
        "pit_archival_revisions": bool(manifest.get("pit_archival_revisions")),
        "fundamentals_status": manifest.get("fundamentals_status", "DATA_NOT_READY"),
        "splits": result,
        "walk_forward_frozen_thresholds": walk_forward,
        "research_note": (
            "P0-P5 are actual episode-clustered results on the historical vendor "
            "price/market panel. P6 is explicitly blocked because archival PIT "
            "fundamental revision data is unavailable. This is research evidence, "
            "not a promotion-grade trading validation."
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
