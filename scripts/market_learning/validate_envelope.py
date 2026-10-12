#!/usr/bin/env python3
"""Validate the market-run envelope's critical safety and point-in-time invariants.

This stdlib-only validator complements schemas/market-run-envelope-v1.schema.json.
It deliberately fails closed on missing provenance, future-available evidence, or
non-false buy/execution flags. It does not calculate forecasts or outcomes.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
VALID_SESSIONS = {"KOREA", "US", "OVERLAP", "GLOBAL_TRANSITION"}
VALID_RUN_KINDS = {"INTRADAY_MONITOR", "EOD_ANALYSIS", "MANUAL_ANALYSIS", "BACKFILL"}
VALID_DATA_QUALITY = {"GREEN", "AMBER", "RED", "DATA_NOT_READY"}
VALID_DECISION_STATES = {"DATA_NOT_READY", "BLOCKED", "RESEARCH_ONLY", "SHADOW"}
VALID_HORIZON_UNITS = {"INTRADAY_MINUTES", "TRADING_SESSIONS", "CALENDAR_DAYS"}
VALID_QUALITY = {"VALID", "STALE", "MISSING", "REJECTED", "REVISED"}
VALID_FRESHNESS = {"FRESH_ACTIVE_SESSION", "VALID_CLOSED_SESSION", "STALE", "MISSING", "UNKNOWN"}
DECISION_USABLE_FRESHNESS = {"FRESH_ACTIVE_SESSION", "VALID_CLOSED_SESSION"}


def _timestamp(value: Any, field: str, errors: list[str]) -> datetime | None:
    if not isinstance(value, str) or not value:
        errors.append(f"{field}: expected ISO-8601 timestamp")
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        errors.append(f"{field}: invalid ISO-8601 timestamp")
        return None
    if parsed.tzinfo is None:
        errors.append(f"{field}: timezone offset is required")
        return None
    return parsed


def validate_envelope(payload: Any) -> list[str]:
    """Return critical contract errors; an empty list means the envelope passed."""
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["$: expected a JSON object"]

    required = {
        "schema_version", "idempotency_key", "analysis_asof", "session_date",
        "run_kind", "session", "data_quality", "provenance", "market_state",
        "forecasts", "decision",
    }
    missing = sorted(required - payload.keys())
    if missing:
        errors.append(f"$: missing required keys: {', '.join(missing)}")
        return errors

    if payload["schema_version"] != "1.0":
        errors.append("$.schema_version: unsupported schema version")
    if not isinstance(payload["idempotency_key"], str) or not payload["idempotency_key"].strip():
        errors.append("$.idempotency_key: must be non-empty")
    if payload["session"] not in VALID_SESSIONS:
        errors.append("$.session: invalid session")
    if payload["run_kind"] not in VALID_RUN_KINDS:
        errors.append("$.run_kind: invalid run kind")
    if payload["data_quality"] not in VALID_DATA_QUALITY:
        errors.append("$.data_quality: invalid data quality state")

    asof = _timestamp(payload["analysis_asof"], "$.analysis_asof", errors)

    provenance = payload["provenance"]
    if not isinstance(provenance, dict):
        errors.append("$.provenance: expected object")
        provenance = {}
    input_hash = provenance.get("input_sha256")
    if not isinstance(input_hash, str) or not SHA256_RE.fullmatch(input_hash):
        errors.append("$.provenance.input_sha256: expected lowercase SHA-256")
    for field in ("code_sha", "config_version", "prompt_version", "calculation_version"):
        if not isinstance(provenance.get(field), str) or not provenance[field].strip():
            errors.append(f"$.provenance.{field}: must be non-empty")

    market_state = payload["market_state"]
    if not isinstance(market_state, dict):
        errors.append("$.market_state: expected object")
        market_state = {}
    dimensions = market_state.get("dimensions", {})
    if not isinstance(dimensions, dict):
        errors.append("$.market_state.dimensions: expected object")
        dimensions = {}
    metrics = market_state.get("metrics", {})
    if not isinstance(metrics, dict):
        errors.append("$.market_state.metrics: expected object")
        metrics = {}

    required_evidence_bad = False
    if asof is not None:
        for key, metric in metrics.items():
            prefix = f"$.market_state.metrics.{key}"
            if not isinstance(metric, dict):
                errors.append(f"{prefix}: expected object")
                continue
            available_at = _timestamp(metric.get("available_at"), f"{prefix}.available_at", errors)
            observed_at = _timestamp(metric.get("observed_at"), f"{prefix}.observed_at", errors)
            published_value = metric.get("published_at")
            published_at = None
            if published_value is not None:
                published_at = _timestamp(published_value, f"{prefix}.published_at", errors)
            if available_at is not None and available_at > asof:
                errors.append(f"{prefix}.available_at: point-in-time violation (later than analysis_asof)")
            if observed_at is not None and observed_at > asof:
                errors.append(f"{prefix}.observed_at: observation is later than analysis_asof")
            if published_at is not None and published_at > asof:
                errors.append(f"{prefix}.published_at: publication is later than analysis_asof")
            quality_status = metric.get("quality_status")
            if quality_status not in VALID_QUALITY:
                errors.append(f"{prefix}.quality_status: invalid quality state")
            freshness_status = metric.get("freshness_status")
            if freshness_status not in VALID_FRESHNESS:
                errors.append(f"{prefix}.freshness_status: invalid or missing freshness state")
            required_for_decision = metric.get("required_for_decision")
            if not isinstance(required_for_decision, bool):
                errors.append(f"{prefix}.required_for_decision: explicit boolean is required")
            if quality_status == "VALID" and metric.get("value") is None:
                errors.append(f"{prefix}.value: VALID metric cannot have null value")
            if quality_status in {"MISSING", "REJECTED"} and metric.get("value") is not None:
                errors.append(f"{prefix}.value: MISSING/REJECTED metric cannot supply a decision value")
            if required_for_decision is True and (
                quality_status != "VALID"
                or freshness_status not in DECISION_USABLE_FRESHNESS
                or metric.get("value") is None
            ):
                required_evidence_bad = True
                errors.append(f"{prefix}: required evidence is not decision-usable")

    for name, dimension in dimensions.items():
        prefix = f"$.market_state.dimensions.{name}"
        if not isinstance(dimension, dict):
            errors.append(f"{prefix}: expected object")
            continue
        score = dimension.get("score")
        if score is not None and (not isinstance(score, (int, float)) or isinstance(score, bool) or not 0 <= score <= 100):
            errors.append(f"{prefix}.score: expected number from 0 to 100 or null")
        confidence = dimension.get("confidence")
        if confidence is not None and (
            not isinstance(confidence, (int, float)) or isinstance(confidence, bool) or not 0 <= confidence <= 1
        ):
            errors.append(f"{prefix}.confidence: expected number from 0 to 1 or null")

    decision = payload["decision"]
    if not isinstance(decision, dict):
        errors.append("$.decision: expected object")
        decision = {}
    if decision.get("state") not in VALID_DECISION_STATES:
        errors.append("$.decision.state: invalid decision state")
    if decision.get("buy_allowed") is not False:
        errors.append("$.decision.buy_allowed: must be false in V1")
    if decision.get("execution_allowed") is not False:
        errors.append("$.decision.execution_allowed: must be false in V1")
    if payload["data_quality"] in {"RED", "DATA_NOT_READY"} and decision.get("state") not in {"BLOCKED", "DATA_NOT_READY"}:
        errors.append("$.decision.state: RED/DATA_NOT_READY evidence must fail closed")
    if required_evidence_bad and payload["data_quality"] == "GREEN":
        errors.append("$.data_quality: GREEN cannot mask stale/missing required evidence")
    if required_evidence_bad and decision.get("state") not in {"BLOCKED", "DATA_NOT_READY"}:
        errors.append("$.decision.state: stale/missing required evidence must fail closed")

    forecasts = payload["forecasts"]
    if not isinstance(forecasts, list):
        errors.append("$.forecasts: expected array")
        forecasts = []
    for i, forecast in enumerate(forecasts):
        prefix = f"$.forecasts[{i}]"
        if not isinstance(forecast, dict):
            errors.append(f"{prefix}: expected object")
            continue
        horizon = forecast.get("horizon")
        if not isinstance(horizon, dict):
            errors.append(f"{prefix}.horizon: expected object")
        else:
            value = horizon.get("value")
            if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
                errors.append(f"{prefix}.horizon.value: must be a positive integer")
            if horizon.get("unit") not in VALID_HORIZON_UNITS:
                errors.append(f"{prefix}.horizon.unit: invalid unit")
        if forecast.get("permission_state") not in VALID_DECISION_STATES:
            errors.append(f"{prefix}.permission_state: invalid permission state")
        if forecast.get("buy_allowed") is not False:
            errors.append(f"{prefix}.buy_allowed: must be false in V1")
        if forecast.get("execution_allowed") is not False:
            errors.append(f"{prefix}.execution_allowed: must be false in V1")
        for field in ("probability_up", "probability_down", "probability_event", "confidence"):
            value = forecast.get(field)
            if value is not None and (
                not isinstance(value, (int, float)) or isinstance(value, bool) or not 0 <= value <= 1
            ):
                errors.append(f"{prefix}.{field}: expected number from 0 to 1 or null")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("envelope", type=Path, help="Path to one market-run envelope JSON file")
    args = parser.parse_args()

    try:
        payload = json.loads(args.envelope.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: cannot read envelope: {exc}", file=sys.stderr)
        return 2

    errors = validate_envelope(payload)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("PASS: market-run envelope critical invariants are valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
