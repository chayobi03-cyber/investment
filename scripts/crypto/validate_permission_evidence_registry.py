#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

ALLOWED_POLICIES = {
    "SOURCE_RELEASE_TIMESTAMP",
    "EXCHANGE_OBSERVATION_TIMESTAMP",
    "EXPLICIT_AVAILABLE_AT",
}
REQUIRED_FAMILIES = {
    "cross_asset_spot",
    "macro_liquidity",
    "derivatives",
    "regulation_market_structure",
    "geopolitical_transmission",
}


def validate(path: Path) -> dict:
    cfg = json.loads(path.read_text(encoding="utf-8"))
    errors: list[str] = []

    if cfg.get("schema_version") != "permission-evidence-registry-v0.1":
        errors.append("INVALID_SCHEMA_VERSION")
    if cfg.get("status") != "SCHEMA_DEFINED_NOT_VALIDATED":
        errors.append("REGISTRY_STATUS_MUST_REMAIN_UNVALIDATED")

    controls = cfg.get("global_controls", {})
    for key in (
        "lookahead_forbidden",
        "provenance_hash_required",
        "explicit_available_at_required",
        "silent_provider_splice_forbidden",
    ):
        if controls.get(key) is not True:
            errors.append("GLOBAL_CONTROL_NOT_TRUE:" + key)

    families = cfg.get("families", [])
    family_ids = [str(x.get("family_id")) for x in families]
    if len(family_ids) != len(set(family_ids)):
        errors.append("DUPLICATE_FAMILY_ID")
    if not REQUIRED_FAMILIES.issubset(set(family_ids)):
        errors.append("REQUIRED_FAMILY_MISSING")

    for family in families:
        family_id = str(family.get("family_id"))
        if family.get("required") is not True:
            errors.append("FAMILY_NOT_REQUIRED:" + family_id)

        policy = family.get("availability_policy")
        if policy not in ALLOWED_POLICIES:
            errors.append("INVALID_AVAILABILITY_POLICY:" + family_id)

        for dataset in family.get("datasets", []):
            source_ids = []
            for series in dataset.get("series", []):
                if series.get("available_at_required") is not True:
                    errors.append(
                        "AVAILABLE_AT_NOT_REQUIRED:" + str(series.get("series_id"))
                    )
            for source in dataset.get("primary_sources", []):
                source_id = str(source.get("source_id"))
                source_ids.append(source_id)
                if source.get("role") not in {"PRIMARY", "FALLBACK", "ARCHIVE"}:
                    errors.append("INVALID_SOURCE_ROLE:" + source_id)
                if not source.get("source_class"):
                    errors.append("SOURCE_CLASS_MISSING:" + source_id)
            if len(source_ids) != len(set(source_ids)):
                errors.append("DUPLICATE_SOURCE_ID:" + str(dataset.get("dataset_id")))

    if errors:
        raise SystemExit(
            "PERMISSION_EVIDENCE_REGISTRY_FAIL:"
            + "|".join(sorted(set(errors)))
        )

    return {
        "status": "PASS",
        "families": len(families),
        "required_families": sorted(REQUIRED_FAMILIES),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("registry", type=Path)
    args = ap.parse_args()
    print(validate(args.registry))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
