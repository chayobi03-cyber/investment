from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


STANCE_VALUES = {"FOR", "AGAINST", "NEUTRAL"}


@dataclass(frozen=True)
class ConflictDetectionResult:
    status: str
    conflict_groups: tuple[str, ...]
    blocker_codes: tuple[str, ...]


class ConflictDetectionAgent:
    """
    Detect explicit structured conflicts. It never chooses which side is correct.
    """

    name = "conflict_detection"

    def run(self, claims: list[Mapping[str, Any]]) -> ConflictDetectionResult:
        groups: dict[str, dict[str, list[str]]] = {}
        blockers: list[str] = []

        for claim in claims:
            group = str(claim.get("conflict_group", "")).strip()
            stance = str(claim.get("stance", "NEUTRAL")).upper()
            claim_id = str(claim.get("claim_id", "UNKNOWN"))

            if not group:
                continue

            if stance not in STANCE_VALUES:
                blockers.append(f"INVALID_STANCE:{claim_id}")
                continue

            groups.setdefault(group, {}).setdefault(stance, []).append(claim_id)

        conflicts: list[str] = []
        for group, stances in groups.items():
            if stances.get("FOR") and stances.get("AGAINST"):
                conflicts.append(group)
                resolution = any(
                    bool(claim.get("conflict_resolution"))
                    for claim in claims
                    if str(claim.get("conflict_group", "")).strip() == group
                )
                if not resolution:
                    blockers.append(f"CONFLICT_UNRESOLVED:{group}")

        return ConflictDetectionResult(
            status="PASS" if not blockers else "BLOCKED",
            conflict_groups=tuple(sorted(conflicts)),
            blocker_codes=tuple(sorted(set(blockers))),
        )
