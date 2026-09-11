"""Generate a deterministic, fail-closed R01 gate report."""

from __future__ import annotations

import argparse
import hashlib
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import yaml

VERIFIED_REVISION_STATES = {
    "ORIGINAL_VERIFIED",
    "REVISED_VERIFIED",
    "NO_REVISION_VERIFIED",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def pit_decision(availability: dict[str, Any], decision_timestamp: str | None) -> str:
    if not decision_timestamp:
        return "FAIL"
    available_raw = availability.get("available_at")
    precision = availability.get("precision", "unknown")
    if not available_raw:
        return "FAIL"
    try:
        decision = datetime.fromisoformat(decision_timestamp.replace("Z", "+00:00"))
    except ValueError:
        try:
            decision = datetime.combine(date.fromisoformat(decision_timestamp), datetime.min.time())
        except ValueError:
            return "FAIL"
    try:
        available = datetime.fromisoformat(str(available_raw).replace("Z", "+00:00"))
    except ValueError:
        try:
            available = datetime.combine(date.fromisoformat(str(available_raw)), datetime.min.time())
        except ValueError:
            return "FAIL"

    if precision == "date":
        if decision.date() < available.date():
            return "FAIL"
        if decision.date() == available.date():
            return "HUMAN_REVIEW"
        return "PASS"
    return "PASS" if decision >= available else "FAIL"


def build_report(manifest: dict[str, Any], base_dir: Path, decision_timestamp: str | None) -> dict[str, Any]:
    publication = manifest.get("publication", {}) or {}
    availability = manifest.get("availability", {}) or {}
    raw = manifest.get("raw_capture", {}) or {}
    revision = manifest.get("revision", {}) or {}
    methodology = manifest.get("methodology", {}) or {}
    observation = manifest.get("observation_period", {}) or {}

    release_gate = "PASS" if all([
        manifest.get("source_id"),
        manifest.get("observation_period"),
        publication.get("official_release_page"),
        publication.get("actual_publication_date"),
        availability.get("available_at"),
    ]) else "FAIL"

    methodology_gate = "PASS" if all([
        methodology.get("methodology_version"),
        methodology.get("sample_design_version"),
        methodology.get("extraction_frame"),
        methodology.get("index_base_period"),
    ]) else "FAIL"

    raw_capture_gate = "PASS" if raw.get("raw_capture_verified") and raw.get("raw_sha256") else "FAIL"

    artifact_gate = "UNKNOWN"
    storage_path = raw.get("storage_path")
    observed_hash = None
    if storage_path:
        target = (base_dir / storage_path).resolve()
        if target.exists() and target.is_file():
            observed_hash = sha256_file(target)
            artifact_gate = "PASS" if observed_hash == raw.get("raw_sha256") else "FAIL"

    revision_gate = "PASS" if revision.get("status") in VERIFIED_REVISION_STATES else "FAIL"
    pit_gate = pit_decision(availability, decision_timestamp)
    data_quality_gate = "PASS" if observation.get("start") and observation.get("end") else "FAIL"

    blockers: list[str] = []
    if release_gate != "PASS":
        blockers.append("release_provenance_incomplete")
    if methodology_gate != "PASS":
        blockers.append("methodology_provenance_incomplete")
    if raw_capture_gate != "PASS":
        blockers.append("raw_capture_not_verified")
    if artifact_gate != "PASS":
        blockers.append("raw_artifact_runtime_integrity_not_verified")
    if revision_gate != "PASS":
        blockers.append("revision_vintage_not_verified")
    if pit_gate != "PASS":
        blockers.append("pit_not_passed")
    if data_quality_gate != "PASS":
        blockers.append("data_quality_incomplete")

    return {
        "gate_report_version": "0.1",
        "research_id": "R01",
        "source_id": manifest.get("source_id"),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "gates": {
            "release_provenance": release_gate,
            "methodology_provenance": methodology_gate,
            "raw_capture_evidence": raw_capture_gate,
            "raw_artifact_runtime_integrity": artifact_gate,
            "revision_vintage": revision_gate,
            "pit": pit_gate,
            "data_quality": data_quality_gate,
        },
        "runtime": {
            "decision_timestamp": decision_timestamp,
            "observed_sha256": observed_hash,
            "stored_artifact_checked": artifact_gate == "PASS",
        },
        "promotion": {
            "eligible": not blockers,
            "status": "PRIMARY_VERIFIED" if not blockers else "PROVISIONAL",
            "blocking_reasons": blockers,
        },
        "downstream": {
            "historical_panel": "ALLOWED" if not blockers else "BLOCKED",
            "hypothesis_freeze": "ALLOWED" if not blockers else "BLOCKED",
            "threshold_preregistration": "ALLOWED" if not blockers else "BLOCKED",
            "backtest": "ALLOWED" if not blockers else "BLOCKED",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--decision-timestamp")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    manifest_path = args.manifest.resolve()
    with manifest_path.open("r", encoding="utf-8") as handle:
        manifest = yaml.safe_load(handle) or {}

    report = build_report(manifest, Path.cwd(), args.decision_timestamp)
    rendered = yaml.safe_dump(report, allow_unicode=True, sort_keys=False)

    if args.output:
        args.output.resolve().write_text(rendered, encoding="utf-8")
    else:
        print(rendered.rstrip())

    return 0 if report["promotion"]["eligible"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
