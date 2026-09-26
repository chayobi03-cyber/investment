from __future__ import annotations

from typing import Any, Mapping

CLAIM_TYPES = {"FACT", "CALCULATION", "INFERENCE"}
BASE_REQUIRED = ("claim_id", "claim_type", "statement", "scope")
SOURCED_TYPES = {"FACT", "CALCULATION"}


def validate_claim_structure(claim: Mapping[str, Any]) -> tuple[str, ...]:
    blockers: list[str] = []
    claim_id = str(claim.get("claim_id", "UNKNOWN"))
    claim_type = str(claim.get("claim_type", ""))

    for required in BASE_REQUIRED:
        if not claim.get(required):
            blockers.append(f"{claim_id}:CLAIM_FIELD_MISSING:{required}")

    if claim_type not in CLAIM_TYPES:
        blockers.append(f"{claim_id}:INVALID_CLAIM_TYPE")
        return tuple(sorted(set(blockers)))

    if claim_type in SOURCED_TYPES:
        for required in ("source_id", "source_timestamp", "available_at"):
            if not claim.get(required):
                blockers.append(f"{claim_id}:CLAIM_FIELD_MISSING:{required}")

    if claim_type == "CALCULATION" and not claim.get("calculation"):
        blockers.append(f"{claim_id}:CLAIM_FIELD_MISSING:calculation")

    if claim_type == "INFERENCE":
        if not claim.get("supporting_claim_ids"):
            blockers.append(f"{claim_id}:CLAIM_FIELD_MISSING:supporting_claim_ids")
        if not claim.get("reasoning"):
            blockers.append(f"{claim_id}:CLAIM_FIELD_MISSING:reasoning")

    return tuple(sorted(set(blockers)))
