from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


SOURCE_CLASSES = (
    "PRIMARY_OFFICIAL",
    "PRIMARY_FILING",
    "PRIMARY_EXCHANGE",
    "LICENSED_MARKET_DATA",
    "REPUTABLE_SECONDARY",
    "SECONDARY",
    "UNKNOWN",
)

SOURCE_CLASS_RANK = {
    "UNKNOWN": 0,
    "SECONDARY": 1,
    "REPUTABLE_SECONDARY": 2,
    "LICENSED_MARKET_DATA": 3,
    "PRIMARY_EXCHANGE": 4,
    "PRIMARY_FILING": 4,
    "PRIMARY_OFFICIAL": 5,
}


@dataclass(frozen=True)
class SourceQualityResult:
    status: str
    classifications: Mapping[str, str]
    blocker_codes: tuple[str, ...]


class SourceQualityAgent:
    """
    Deterministic source classification.

    The agent does not assign a subjective truth score. It only checks
    whether the supplied source metadata meets a declared minimum class.
    """

    name = "source_quality"

    def run(
        self,
        claims: list[Mapping[str, Any]],
        sources: list[Mapping[str, Any]],
    ) -> SourceQualityResult:
        registry = {str(source.get("source_id")): source for source in sources}
        classifications: dict[str, str] = {}
        blockers: list[str] = []

        for source_id, source in registry.items():
            source_class = str(source.get("source_class", "UNKNOWN"))
            if source_class not in SOURCE_CLASSES:
                source_class = "UNKNOWN"
                blockers.append(f"INVALID_SOURCE_CLASS:{source_id}")
            classifications[source_id] = source_class

        for claim in claims:
            if claim.get("claim_type") not in {"FACT", "CALCULATION"}:
                continue

            source_id = str(claim.get("source_id", ""))
            if not source_id:
                continue
            if source_id not in registry:
                blockers.append(f"SOURCE_QUALITY_SOURCE_MISSING:{source_id}")
                continue

            source_class = classifications.get(source_id, "UNKNOWN")
            minimum = str(claim.get("minimum_source_class", "REPUTABLE_SECONDARY"))

            if minimum not in SOURCE_CLASS_RANK:
                blockers.append(f"INVALID_MINIMUM_SOURCE_CLASS:{claim.get('claim_id', 'UNKNOWN')}")
                continue

            if SOURCE_CLASS_RANK[source_class] < SOURCE_CLASS_RANK[minimum]:
                blockers.append(
                    f"SOURCE_QUALITY_BELOW_MINIMUM:{claim.get('claim_id', 'UNKNOWN')}:"
                    f"{source_class}<{minimum}"
                )

        return SourceQualityResult(
            status="PASS" if not blockers else "BLOCKED",
            classifications=classifications,
            blocker_codes=tuple(sorted(set(blockers))),
        )
