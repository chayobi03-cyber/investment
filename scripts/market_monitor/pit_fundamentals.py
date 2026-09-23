#!/usr/bin/env python3
"""Validate and materialize OpenDART filing-level PIT fundamentals.

Input is an immutable capture of OpenDART regular-report financial facts.
Each fact is tied to the filing receipt number and filing/publication time.
No latest-value lookup is substituted for an as-published capture.

This module intentionally stays DATA_NOT_READY when captures do not contain the
required filing-level provenance.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


REQUIRED = {
    "corp_code",
    "corp_name",
    "stock_code",
    "rcept_no",
    "rcept_dt",
    "bsns_year",
    "reprt_code",
    "fs_div",
    "sj_div",
    "account_id",
    "account_nm",
    "thstrm_amount",
}


def parse_available_at(value: str) -> datetime:
    """Parse DART filing timestamp in YYYYMMDD or ISO form as UTC date boundary."""
    raw = str(value).strip()
    if len(raw) == 8 and raw.isdigit():
        return datetime.strptime(raw, "%Y%m%d").replace(tzinfo=timezone.utc)
    return datetime.fromisoformat(raw.replace("Z", "+00:00")).astimezone(timezone.utc)


def validate_fact(row: dict[str, Any]) -> list[str]:
    missing = sorted(REQUIRED - row.keys())
    blockers = [f"missing:{field}" for field in missing]

    rcept_no = str(row.get("rcept_no", "")).strip()
    if rcept_no and (not rcept_no.isdigit() or len(rcept_no) != 14):
        blockers.append("invalid:rcept_no")

    try:
        parse_available_at(str(row.get("rcept_dt", "")))
    except (TypeError, ValueError):
        blockers.append("invalid:rcept_dt")

    if str(row.get("fs_div", "")) not in {"CFS", "OFS"}:
        blockers.append("invalid:fs_div")

    if not str(row.get("account_id", "")).strip():
        blockers.append("missing:account_id")

    return blockers


def available_facts(
    facts: Iterable[dict[str, Any]],
    *,
    decision_at: datetime,
) -> dict[str, Any]:
    decision_at = decision_at.astimezone(timezone.utc)
    eligible: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []

    for row in facts:
        blockers = validate_fact(row)
        if blockers:
            excluded.append({"row": row, "reason": blockers})
            continue

        available_at = parse_available_at(str(row["rcept_dt"]))
        if available_at <= decision_at:
            clean = dict(row)
            clean["available_at"] = available_at.isoformat().replace("+00:00", "Z")
            clean["pit_status"] = "DART_AS_PUBLISHED_CAPTURE"
            clean["revision_status"] = "FILING_LEVEL_CAPTURE"
            eligible.append(clean)
        else:
            excluded.append(
                {
                    "row": row,
                    "reason": ["not_available_at_decision_time"],
                }
            )

    return {
        "status": "OK" if eligible else "DATA_NOT_READY",
        "decision_at": decision_at.isoformat().replace("+00:00", "Z"),
        "eligible_count": len(eligible),
        "excluded_count": len(excluded),
        "facts": eligible,
        "excluded": excluded,
    }


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open(encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"line {line_no}: invalid JSON: {exc}") from exc
            if not isinstance(row, dict):
                raise ValueError(f"line {line_no}: expected object")
            rows.append(row)
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--decision-at", required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    decision_at = datetime.fromisoformat(args.decision_at.replace("Z", "+00:00"))
    result = available_facts(load_jsonl(args.input), decision_at=decision_at)
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(payload + "\n", encoding="utf-8")
    print(payload)
    return 0 if result["status"] == "OK" else 2


if __name__ == "__main__":
    raise SystemExit(main())
