from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Mapping


BUY_ALLOWED = False
EXECUTION_ALLOWED = False


class DecisionState(StrEnum):
    DATA_NOT_READY = "DATA_NOT_READY"
    BLOCKED = "BLOCKED"
    RESEARCH_ONLY = "RESEARCH_ONLY"


@dataclass(frozen=True)
class DecisionGateResult:
    decision_status: DecisionState
    promotion_status: str
    buy_allowed: bool
    execution_allowed: bool
    blocker_codes: tuple[str, ...]


class DecisionGateAgent:
    """Final deterministic gate for the investment decision plane."""

    name = "decision_gate"

    def run(
        self,
        agent_statuses: Mapping[str, str],
        *,
        blocker_codes: tuple[str, ...] = (),
    ) -> DecisionGateResult:
        normalized = {str(k): str(v) for k, v in agent_statuses.items()}

        if not normalized:
            state = DecisionState.DATA_NOT_READY
            blockers = ("NO_UPSTREAM_AGENT_STATUS", *blocker_codes)
        elif any(status == "DATA_NOT_READY" for status in normalized.values()):
            state = DecisionState.DATA_NOT_READY
            blockers = tuple(blocker_codes)
        elif any(status == "BLOCKED" for status in normalized.values()):
            state = DecisionState.BLOCKED
            blockers = tuple(blocker_codes)
        elif all(status == "PASS" for status in normalized.values()):
            # Research controls may be green, but live promotion remains disabled.
            state = DecisionState.RESEARCH_ONLY
            blockers = tuple(blocker_codes)
        else:
            state = DecisionState.BLOCKED
            blockers = tuple(sorted(set((*blocker_codes, "UNKNOWN_UPSTREAM_STATUS"))))

        return DecisionGateResult(
            decision_status=state,
            promotion_status="DISABLED",
            buy_allowed=BUY_ALLOWED,
            execution_allowed=EXECUTION_ALLOWED,
            blocker_codes=tuple(sorted(set(blockers))),
        )
