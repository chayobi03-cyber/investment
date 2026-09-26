from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping


def _utc(value: datetime | str) -> datetime:
    parsed = value if isinstance(value, datetime) else datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


@dataclass(frozen=True)
class SourceRecord:
    source_id: str
    title: str
    source_url: str
    source_type: str
    available_at: datetime
    retrieved_at: datetime
    content_hash: str

    @property
    def source_class(self) -> str:
        """Semantic alias: source_type stores the declared source class."""
        return self.source_type


@dataclass(frozen=True)
class SourceRetrievalResult:
    status: str
    records: int
    referenced_sources: int
    blocker_codes: tuple[str, ...]


class SourceRetrievalAgent:
    """Validate that cited source artifacts were actually retrieved and PIT-eligible."""

    name = "source_retrieval"

    def run(
        self,
        claims: list[Mapping[str, Any]],
        sources: list[SourceRecord],
        *,
        decision_timestamp: datetime,
    ) -> SourceRetrievalResult:
        decision_timestamp = _utc(decision_timestamp)
        blockers: list[str] = []

        ids = [source.source_id for source in sources]
        if len(ids) != len(set(ids)):
            blockers.append("DUPLICATE_SOURCE_ID")

        registry = {source.source_id: source for source in sources}

        referenced = {
            str(claim.get("source_id"))
            for claim in claims
            if claim.get("claim_type") in {"FACT", "CALCULATION"} and claim.get("source_id")
        }

        missing = sorted(referenced - set(registry))
        if missing:
            blockers.append("SOURCE_NOT_RETRIEVED:" + ",".join(missing))

        for source in sources:
            if not source.title:
                blockers.append(f"SOURCE_TITLE_MISSING:{source.source_id}")
            if not source.source_url:
                blockers.append(f"SOURCE_URL_MISSING:{source.source_id}")
            if not source.content_hash:
                blockers.append(f"SOURCE_CONTENT_HASH_MISSING:{source.source_id}")

            try:
                available_at = _utc(source.available_at)
                retrieved_at = _utc(source.retrieved_at)
            except (TypeError, ValueError):
                blockers.append(f"SOURCE_TIMESTAMP_INVALID:{source.source_id}")
                continue

            if available_at > decision_timestamp:
                blockers.append(f"SOURCE_LOOKAHEAD:{source.source_id}")
            if retrieved_at < available_at:
                blockers.append(f"SOURCE_RETRIEVAL_BEFORE_AVAILABILITY:{source.source_id}")

        status = "PASS" if not blockers else "DATA_NOT_READY"
        return SourceRetrievalResult(
            status=status,
            records=len(sources),
            referenced_sources=len(referenced & set(registry)),
            blocker_codes=tuple(sorted(set(blockers))),
        )
