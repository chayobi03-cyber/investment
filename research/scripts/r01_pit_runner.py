"""Deterministic, fail-closed R01 PIT decision runner.

Examples:
    python research/scripts/r01_pit_runner.py \
      docs/market/fixtures/r01/reb_house_price_2025-07_capture_manifest.yaml \
      2025-08-17

    python research/scripts/r01_pit_runner.py \
      docs/market/fixtures/r01/reb_house_price_2025-07_capture_manifest.yaml \
      2025-08-18

The current REB fixture has date precision only. Same-day decisions therefore
return HUMAN_REVIEW rather than being silently allowed.
"""

from __future__ import annotations

import argparse
from datetime import date, datetime
from pathlib import Path
from typing import Any

import yaml


def parse_date_or_datetime(value: str) -> datetime:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return datetime.combine(date.fromisoformat(value), datetime.min.time())


def run_pit(manifest: dict[str, Any], decision_timestamp: str) -> dict[str, Any]:
    availability = manifest.get("availability", {}) or {}
    available_raw = availability.get("available_at")
    precision = availability.get("precision", "unknown")
    decision = parse_date_or_datetime(decision_timestamp)

    if not available_raw:
        return {
            "decision": "BLOCK",
            "reason": "missing available_at",
            "precision": precision,
        }

    available = parse_date_or_datetime(str(available_raw))

    if precision == "date":
        decision_day = decision.date()
        available_day = available.date()
        if decision_day < available_day:
            decision_name = "BLOCK"
            reason = "decision date precedes source release date"
        elif decision_day == available_day:
            decision_name = "HUMAN_REVIEW"
            reason = "same-day decision with date-level availability precision"
        else:
            decision_name = "ALLOW"
            reason = "decision date is after source release date"
    else:
        if decision < available:
            decision_name = "BLOCK"
            reason = "decision timestamp precedes source availability"
        else:
            decision_name = "ALLOW"
            reason = "decision timestamp is at or after source availability"

    return {
        "source_id": manifest.get("source_id"),
        "observation_period": manifest.get("observation_period"),
        "decision_timestamp": decision_timestamp,
        "available_at": available_raw,
        "availability_precision": precision,
        "decision": decision_name,
        "reason": reason,
        "fail_closed": decision_name != "ALLOW" or precision == "date",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("decision_timestamp")
    args = parser.parse_args()

    with args.manifest.resolve().open("r", encoding="utf-8") as handle:
        manifest = yaml.safe_load(handle) or {}

    result = run_pit(manifest, args.decision_timestamp)
    print(yaml.safe_dump(result, allow_unicode=True, sort_keys=False).rstrip())

    # ALLOW is the only successful PIT execution state.
    return 0 if result["decision"] == "ALLOW" else 2


if __name__ == "__main__":
    raise SystemExit(main())
