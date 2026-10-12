#!/usr/bin/env python3
"""Validate and append one market-monitor envelope to Historical DB v1.

The monitor's latest-state JSON is an operational cache, not a history ledger.
This adapter freezes horizon-aware metrics, lineage and source observations into
market_runs.csv. It rejects legacy monitor schemas and fails closed when critical
series freshness is missing or invalid. The ledger is append-only and idempotent.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from investment_pipeline.history.models import MarketRunSnapshot  # noqa: E402
from investment_pipeline.history.store import HistoricalStore  # noqa: E402
from scripts.market_learning.validate_envelope import validate_envelope  # noqa: E402

VALID_RUN_KINDS = {
    "INTRADAY_MONITOR",
    "PREOPEN_ANALYSIS",
    "EOD_ANALYSIS",
    "MANUAL_ANALYSIS",
    "BACKFILL",
}
VALID_FRESHNESS = {
    "FRESH_ACTIVE_SESSION",
    "VALID_CLOSED_SESSION",
    "STALE",
    "MISSING",
    "UNKNOWN",
}
VALID_SERIES_FRESHNESS = {"FRESH_ACTIVE_SESSION", "VALID_CLOSED_SESSION"}
INTRADAY_FIELDS = {"change_pct_5m", "change_pct_15m", "session_change_pct"}
HORIZON_FIELDS = (
    ("price", "native_price_units"),
    ("change_pct_5m", "percent"),
    ("change_pct_15m", "percent"),
    ("session_change_pct", "percent"),
    ("last_completed_session_return_pct", "percent"),
)


def canonical_json(value: Any) -> str:
    """Stable serialization used for hashing, idempotency and evidence retention."""
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def parse_timestamp(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if result.tzinfo is None:
        return None
    return result


def _quality_rank(value: str) -> int:
    return {"GREEN": 0, "AMBER": 1, "RED": 2, "DATA_NOT_READY": 3}.get(value, 3)


def _effective_quality(
    state: dict[str, Any],
    raw: dict[str, Any],
    config: dict[str, Any],
) -> tuple[str, list[str]]:
    """Recompute the fail-closed top-level quality from required series, not global recency."""
    metrics = state.get("metrics") or {}
    freshness = metrics.get("freshness_by_series") or {}
    groups = raw.get("groups") or {}
    required = config.get("thresholds", {}).get("required_series") or []
    missing: list[str] = []
    stale: list[str] = []

    for key in required:
        if not isinstance(key, str) or "." not in key:
            missing.append(str(key))
            continue
        group, name = key.split(".", 1)
        item = (groups.get(group) or {}).get(name)
        series_status = freshness.get(key, "MISSING")
        observed_at = parse_timestamp(item.get("timestamp")) if isinstance(item, dict) else None
        if (
            not isinstance(item, dict)
            or item.get("ok") is not True
            or observed_at is None
            or series_status in {"MISSING", "UNKNOWN"}
            or series_status not in VALID_FRESHNESS
        ):
            missing.append(key)
        elif series_status == "STALE":
            stale.append(key)

    reported = state.get("DATA_QUALITY", "RED")
    if reported not in {"GREEN", "AMBER", "RED", "DATA_NOT_READY"}:
        reported = "DATA_NOT_READY"

    if missing:
        effective = "RED"
    elif stale:
        effective = "AMBER" if _quality_rank(reported) < 2 else reported
    else:
        effective = reported

    # A RED state can be preserved even when a provider happened to return values:
    # the upstream monitor may have rejected a separate required dependency.
    reasons = [f"REQUIRED_MISSING_OR_UNKNOWN:{key}" for key in sorted(set(missing))]
    reasons.extend(f"REQUIRED_STALE:{key}" for key in sorted(set(stale)))
    return effective, reasons


def _dimension_payload(state: dict[str, Any], calculation_version: str) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for source_key in (
        "RISK", "TREND", "BREADTH", "LEADERS", "RATES", "FX", "OIL", "GOLD", "GEO"
    ):
        value = state.get(source_key)
        if value == "N/A":
            value = "N_A"
        if value not in {"GREEN", "AMBER", "RED", "N_A", "DATA_NOT_READY", "BLOCKED"}:
            continue
        out[source_key] = {
            "state": value,
            "score": None,
            "confidence": None,
            "sample_count": 0,
            "calculation_version": calculation_version,
            "evidence_ids": [],
        }
    return out


def _metric_quality(value: Any, freshness_status: str, field: str) -> tuple[Any, str]:
    if freshness_status not in VALID_FRESHNESS:
        freshness_status = "UNKNOWN"

    # A last 5m/15m/session move from a closed market is retained only as stale
    # diagnostic evidence. It cannot masquerade as the current session's move.
    if field in INTRADAY_FIELDS and freshness_status != "FRESH_ACTIVE_SESSION":
        if value is None:
            return None, "MISSING"
        return value, "STALE"

    if freshness_status == "STALE":
        return (value, "STALE") if value is not None else (None, "MISSING")
    if freshness_status in {"MISSING", "UNKNOWN"}:
        return None, "MISSING" if freshness_status == "MISSING" else "REJECTED"
    if value is None:
        return None, "MISSING"
    return value, "VALID"


def _as_finite_number(value: Any) -> int | float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return value if math.isfinite(float(value)) else None


def build_envelope(
    snapshot: dict[str, Any],
    *,
    config: dict[str, Any],
    code_sha: str,
    run_kind: str,
) -> dict[str, Any]:
    """Convert monitor v2.1 output into the canonical versioned market-run envelope."""
    if not isinstance(snapshot, dict):
        raise ValueError("snapshot must be a JSON object")
    state = snapshot.get("state")
    raw = snapshot.get("raw")
    event = snapshot.get("event") or {}
    if not isinstance(state, dict) or not isinstance(raw, dict):
        raise ValueError("snapshot must contain state and raw objects")
    if state.get("schema_version") != "2.1":
        raise ValueError(
            "legacy monitor state rejected: require schema_version 2.1 with explicit return horizons"
        )
    if run_kind not in VALID_RUN_KINDS:
        raise ValueError(f"unsupported run_kind: {run_kind}")
    if not isinstance(code_sha, str) or not code_sha.strip():
        raise ValueError("code_sha must be non-empty")

    asof = state.get("asof") or raw.get("collected_at")
    asof_dt = parse_timestamp(asof)
    if asof_dt is None:
        raise ValueError("monitor asof must be an ISO-8601 timestamp with timezone")
    collected_at = raw.get("collected_at")
    collected_dt = parse_timestamp(collected_at)
    if collected_dt is None or collected_dt > asof_dt:
        raise ValueError("collector timestamp missing or later than monitor analysis_asof")

    effective_quality, quality_reasons = _effective_quality(state, raw, config)
    state_metrics = state.get("metrics") or {}
    freshness_by_series = state_metrics.get("freshness_by_series") or {}
    required_series = set(config.get("thresholds", {}).get("required_series") or [])
    calculation_version = "returns-5m-15m-close-close-v1"
    for group in (raw.get("groups") or {}).values():
        for item in (group or {}).values():
            if isinstance(item, dict) and item.get("return_calculation_version"):
                calculation_version = str(item["return_calculation_version"])
                break

    input_sha = sha256_json(snapshot)
    idempotency_material = "|".join((asof, code_sha, input_sha, run_kind, calculation_version))
    idempotency_digest = hashlib.sha256(idempotency_material.encode("utf-8")).hexdigest()
    idempotency_key = f"market-monitor-v1:{idempotency_digest}"
    session = state.get("session")
    if session not in {"KOREA", "US", "OVERLAP", "GLOBAL_TRANSITION"}:
        raise ValueError("monitor session is missing or invalid")
    session_date = asof_dt.astimezone(ZoneInfo("Asia/Seoul")).date().isoformat()

    monitor_metrics: dict[str, Any] = {}
    groups = raw.get("groups") or {}
    for group_name, group_values in groups.items():
        if not isinstance(group_values, dict):
            continue
        for series_name, item in group_values.items():
            if not isinstance(item, dict):
                continue
            series_key = f"{group_name}.{series_name}"
            source_status = freshness_by_series.get(series_key, "UNKNOWN")
            if source_status not in VALID_FRESHNESS:
                source_status = "UNKNOWN"
            observed = parse_timestamp(item.get("timestamp"))
            if observed is None:
                # Missing timestamps are represented by a run-level gap, not a fabricated observation.
                continue
            observed_iso = observed.isoformat().replace("+00:00", "Z")
            market_session_state = item.get("market_session_state")
            if market_session_state == "ACTIVE":
                primary_horizon_field = "change_pct_15m"
            elif market_session_state == "CLOSED":
                primary_horizon_field = "last_completed_session_return_pct"
            else:
                primary_horizon_field = None

            for field, default_unit in HORIZON_FIELDS:
                field_value = _as_finite_number(item.get(field))
                metric_value, field_quality = _metric_quality(field_value, source_status, field)
                required_for_decision = series_key in required_series and (
                    field == "price" or field == primary_horizon_field
                    or (primary_horizon_field is None and field in {"change_pct_15m", "last_completed_session_return_pct"})
                )
                unit = item.get("currency") if field == "price" else default_unit
                monitor_metrics[f"{series_key}.{field}"] = {
                    "value": metric_value,
                    "unit": unit,
                    "observed_at": observed_iso,
                    "published_at": observed_iso,
                    "available_at": asof,
                    "source_id": f"yahoo-chart:{item.get('symbol') or series_key}",
                    "quality_status": field_quality,
                    "required_for_decision": bool(required_for_decision),
                    "freshness_status": source_status,
                }

    # Store derived indicators separately from source observations and preserve their origin.
    derived_freshness = (
        "FRESH_ACTIVE_SESSION" if session in {"KOREA", "US", "OVERLAP"}
        else "VALID_CLOSED_SESSION"
    )
    for key in ("trend_selected_pct", "breadth_proxy", "freshness_max_required_minutes"):
        number = _as_finite_number(state_metrics.get(key))
        if number is None:
            continue
        monitor_metrics[f"derived.{key}"] = {
            "value": number,
            "unit": "minutes" if key == "freshness_max_required_minutes" else "ratio" if key == "breadth_proxy" else "percent",
            "observed_at": asof,
            "published_at": None,
            "available_at": asof,
            "source_id": f"derived:market-monitor:{calculation_version}",
            "quality_status": "VALID" if effective_quality == "GREEN" else "STALE" if effective_quality == "AMBER" else "REJECTED",
            "required_for_decision": False,
            "freshness_status": derived_freshness if effective_quality == "GREEN" else "STALE" if effective_quality == "AMBER" else "UNKNOWN",
        }

    dimensions = _dimension_payload(state, calculation_version)
    dimensions["DATA_QUALITY"] = {
        "state": effective_quality if effective_quality in {"GREEN", "AMBER", "RED"} else "DATA_NOT_READY",
        "score": None,
        "confidence": None,
        "sample_count": 0,
        "calculation_version": calculation_version,
        "evidence_ids": [],
    }
    regime = state.get("REGIME")
    if regime not in {"R1", "R2", "R3", "R4", "R5", "R6", "UNCONFIRMED", "DATA_NOT_READY"}:
        regime = "UNCONFIRMED"

    decision_state = "RESEARCH_ONLY" if effective_quality == "GREEN" else "BLOCKED"
    reason_codes = ["OBSERVATIONAL_MONITOR_ONLY"]
    if effective_quality != "GREEN":
        reason_codes.append(f"DATA_QUALITY_{effective_quality}")
    reason_codes.extend(quality_reasons)

    envelope = {
        "schema_version": "1.0",
        "idempotency_key": idempotency_key,
        "analysis_asof": asof,
        "session_date": session_date,
        "run_kind": run_kind,
        "session": session,
        "data_quality": effective_quality,
        "provenance": {
            "code_sha": code_sha,
            "config_version": str(config.get("version", "unknown")),
            "rule_version": f"market-monitor-v{state.get('schema_version')}",
            "prompt_version": "not-applicable-deterministic-monitor-v1",
            "calculation_version": calculation_version,
            "input_sha256": input_sha,
            "artifact_uri": None,
        },
        "market_state": {
            "regime": regime,
            "dimensions": dimensions,
            "metrics": monitor_metrics,
        },
        "forecasts": [],
        "decision": {
            "state": decision_state,
            "buy_allowed": False,
            "execution_allowed": False,
            "reason_codes": sorted(set(reason_codes)),
        },
        "summary": {
            "headline": f"Market monitor snapshot; quality={effective_quality}; session={session}",
            "state_delta": [str(x)[:300] for x in (event.get("delta") or []) if isinstance(x, str)][:100],
            "unresolved_gaps": sorted(set(quality_reasons))[:100],
            "evidence_ids": [],
        },
    }

    errors = validate_envelope(envelope)
    if errors:
        raise ValueError("market envelope validation failed: " + "; ".join(errors[:20]))
    return envelope


def append_run(envelope: dict[str, Any], *, root: str | Path, source_snapshot: dict[str, Any]) -> tuple[bool, str]:
    """Persist an immutable ledger row; a repeat is a no-op and a key collision is an error."""
    key = envelope["idempotency_key"]
    run_id = "run-" + hashlib.sha256(key.encode("utf-8")).hexdigest()[:24]
    provenance = envelope["provenance"]
    state = source_snapshot.get("state") or {}
    summary = envelope.get("summary") or {}
    row = MarketRunSnapshot(
        run_id=run_id,
        analysis_asof=envelope["analysis_asof"],
        session_date=envelope["session_date"],
        run_kind=envelope["run_kind"],
        session=envelope["session"],
        data_quality=envelope["data_quality"],
        decision_state=envelope["decision"]["state"],
        regime=envelope["market_state"]["regime"],
        risk_state=state.get("RISK"),
        trend_state=state.get("TREND"),
        breadth_state=state.get("BREADTH"),
        leaders_state=state.get("LEADERS"),
        rates_state=state.get("RATES"),
        fx_state=state.get("FX"),
        oil_state=state.get("OIL"),
        gold_state=state.get("GOLD"),
        input_sha256=provenance["input_sha256"],
        code_sha=provenance["code_sha"],
        config_version=provenance["config_version"],
        rule_version=str(provenance.get("rule_version") or ""),
        calculation_version=provenance["calculation_version"],
        summary_json=canonical_json(summary),
        envelope_json=canonical_json(envelope),
        source_snapshot_json=canonical_json(source_snapshot),
        record_origin="market_monitor",
    )
    stored = HistoricalStore(root).append_run(row)
    return stored, run_id


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="runtime/market_state.json")
    parser.add_argument("--root", type=Path, default=Path("data/history"), help="Historical DB v1 root")
    parser.add_argument("--code-sha", default=os.environ.get("GITHUB_SHA", "local-unversioned"))
    parser.add_argument(
        "--run-kind",
        choices=sorted(VALID_RUN_KINDS),
        default="MANUAL_ANALYSIS",
    )
    parser.add_argument("--config", type=Path, default=ROOT / "config" / "market_monitor.json")
    parser.add_argument("--envelope-output", type=Path, help="Optional envelope JSON output path")
    args = parser.parse_args()

    try:
        snapshot = json.loads(args.input.read_text(encoding="utf-8"))
        config = json.loads(args.config.read_text(encoding="utf-8"))
        envelope = build_envelope(
            snapshot,
            config=config,
            code_sha=args.code_sha,
            run_kind=args.run_kind,
        )
        stored, run_id = append_run(envelope, root=args.root, source_snapshot=snapshot)
        if args.envelope_output:
            args.envelope_output.parent.mkdir(parents=True, exist_ok=True)
            args.envelope_output.write_text(json.dumps(envelope, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(json.dumps({"status": "BLOCKED", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1

    print(json.dumps({
        "status": "RECORDED" if stored else "ALREADY_RECORDED",
        "run_id": run_id,
        "analysis_asof": envelope["analysis_asof"],
        "session_date": envelope["session_date"],
        "run_kind": envelope["run_kind"],
        "data_quality": envelope["data_quality"],
        "decision_state": envelope["decision"]["state"],
        "input_sha256": envelope["provenance"]["input_sha256"],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
