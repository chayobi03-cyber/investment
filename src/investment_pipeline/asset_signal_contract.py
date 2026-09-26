from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Mapping, Protocol


@dataclass(frozen=True)
class AssetSignalSnapshot:
    """Immutable handoff from an asset-specific engine to the decision plane."""

    asset: str
    signal_state: str
    as_of: datetime
    rule_version: str
    evidence_refs: tuple[str, ...] = ()
    metrics: Mapping[str, float] | None = None

    def __post_init__(self) -> None:
        if not self.asset:
            raise ValueError("asset_required")
        if not self.signal_state:
            raise ValueError("signal_state_required")
        if not self.rule_version:
            raise ValueError("rule_version_required")
        if self.as_of.tzinfo is None:
            raise ValueError("as_of_must_be_timezone_aware")
        if self.as_of != self.as_of.astimezone(timezone.utc):
            object.__setattr__(self, "as_of", self.as_of.astimezone(timezone.utc))


class AssetSignalAdapter(Protocol):
    asset: str
    name: str

    def adapt(self, snapshot: AssetSignalSnapshot) -> Mapping[str, object]:
        """Convert an immutable asset signal into the common control-plane shape."""
        ...


def require_pit_eligible(snapshot: AssetSignalSnapshot, decision_timestamp: datetime) -> None:
    if decision_timestamp.tzinfo is None:
        raise ValueError("decision_timestamp_must_be_timezone_aware")
    decision_timestamp = decision_timestamp.astimezone(timezone.utc)
    if snapshot.as_of > decision_timestamp:
        raise ValueError("SIGNAL_LOOKAHEAD")
