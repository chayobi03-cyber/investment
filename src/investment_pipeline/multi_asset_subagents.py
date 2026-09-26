from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum
from typing import Any, Mapping, Protocol

from src.investment_pipeline.hallucination_guard_agent import HallucinationGuardAgent

BUY_ALLOWED = False
EXECUTION_ALLOWED = False


class AssetClass(StrEnum):
    EQUITY = "EQUITY"
    GOLD = "GOLD"
    CRYPTO = "CRYPTO"


class Gate(StrEnum):
    GREEN = "GREEN"
    YELLOW = "YELLOW"
    RED = "RED"
    DATA_NOT_READY = "DATA_NOT_READY"


class Status(StrEnum):
    PASS = "PASS"
    BLOCKED = "BLOCKED"
    DATA_NOT_READY = "DATA_NOT_READY"


@dataclass(frozen=True)
class PITObservation:
    series_id: str
    observation_timestamp: datetime
    available_at: datetime
    source_id: str
    value: float | None
    provenance_hash: str | None = None


@dataclass(frozen=True)
class AgentResult:
    agent: str
    asset: AssetClass | None
    status: Status
    payload: Mapping[str, Any]
    blocker_codes: tuple[str, ...] = ()


@dataclass(frozen=True)
class DecisionContract:
    asset: AssetClass
    signal_state: str
    permission_status: Status
    market_gate: Gate
    risk_gate: Gate
    evidence_status: Status
    hallucination_status: Status
    buy_allowed: bool
    execution_allowed: bool
    blocker_codes: tuple[str, ...] = field(default_factory=tuple)


class SignalAgent(Protocol):
    asset: AssetClass

    def run(self, features: Mapping[str, Any]) -> AgentResult: ...


def _utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


class DataPITAgent:
    name = "data_pit"

    def run(
        self,
        observations: list[PITObservation],
        *,
        decision_timestamp: datetime,
        required_series: set[str],
    ) -> AgentResult:
        decision_timestamp = _utc(decision_timestamp)
        blockers: list[str] = []

        seen = {o.series_id for o in observations}
        missing = sorted(required_series - seen)
        if missing:
            blockers.append("MISSING_REQUIRED_SERIES:" + ",".join(missing))

        invalid = [
            o.series_id
            for o in observations
            if _utc(o.available_at) > decision_timestamp
        ]
        if invalid:
            blockers.append("LOOKAHEAD_AVAILABLE_AT")

        provenance_missing = [
            o.series_id
            for o in observations
            if not o.provenance_hash
        ]
        if provenance_missing:
            blockers.append("PROVENANCE_MISSING")

        status = Status.PASS if not blockers else Status.DATA_NOT_READY
        return AgentResult(
            self.name,
            None,
            status,
            {
                "decision_timestamp": decision_timestamp.isoformat(),
                "observation_count": len(observations),
                "eligible_rows": sum(
                    1 for o in observations
                    if _utc(o.available_at) <= decision_timestamp
                ),
            },
            tuple(blockers),
        )


class RegimeAgent:
    name = "regime"

    def run(
        self,
        axis_scores: Mapping[str, float],
        *,
        weights: Mapping[str, float],
    ) -> AgentResult:
        keys = set(weights)
        if keys != set(axis_scores):
            missing = sorted(keys - set(axis_scores))
            return AgentResult(
                self.name, None, Status.DATA_NOT_READY, {},
                (f"MISSING_REGIME_AXES:{','.join(missing)}",),
            )
        if abs(sum(weights.values()) - 1.0) > 1e-9:
            return AgentResult(
                self.name, None, Status.DATA_NOT_READY, {},
                ("REGIME_WEIGHTS_NOT_1",),
            )
        if any(not 0 <= float(axis_scores[k]) <= 100 for k in keys):
            return AgentResult(
                self.name, None, Status.DATA_NOT_READY, {},
                ("REGIME_AXIS_OUT_OF_RANGE",),
            )

        score = round(
            sum(float(axis_scores[k]) * float(weights[k]) for k in keys), 4
        )
        gate = (
            Gate.GREEN if score >= 70
            else Gate.YELLOW if score >= 55
            else Gate.RED
        )
        raw_regime = (
            "R1" if score >= 75
            else "R2" if score >= 60
            else "R3" if score >= 50
            else "R4" if score >= 40
            else "R5" if score >= 25
            else "R6"
        )
        return AgentResult(
            self.name,
            None,
            Status.PASS,
            {
                "market_score": score,
                "market_gate": gate.value,
                "raw_regime": raw_regime,
            },
        )


class PermissionAgent:
    name = "permission"

    def run(
        self,
        *,
        market_gate: Gate,
        macro_block: bool = False,
        derivatives_block: bool = False,
        regulation_block: bool = False,
        geopolitical_block: bool = False,
    ) -> AgentResult:
        blockers = []
        if market_gate in {Gate.RED, Gate.DATA_NOT_READY}:
            blockers.append("MARKET_GATE_BLOCK")
        if macro_block:
            blockers.append("MACRO_BLOCK")
        if derivatives_block:
            blockers.append("DERIVATIVES_BLOCK")
        if regulation_block:
            blockers.append("REGULATION_BLOCK")
        if geopolitical_block:
            blockers.append("GEOPOLITICAL_BLOCK")

        status = Status.PASS if not blockers else Status.BLOCKED
        return AgentResult(
            self.name,
            None,
            status,
            {
                "buy_allowed": BUY_ALLOWED,
                "overlay_only": True,
            },
            tuple(blockers),
        )


class RiskAgent:
    name = "risk"

    def run(
        self,
        *,
        max_drawdown: float | None,
        mae: float | None,
        stress_loss: float | None,
        concentration_ok: bool = True,
    ) -> AgentResult:
        blockers: list[str] = []
        if not concentration_ok:
            blockers.append("CONCENTRATION_LIMIT")
        if max_drawdown is None or mae is None or stress_loss is None:
            blockers.append("RISK_INPUT_MISSING")

        status = Status.PASS if not blockers else Status.DATA_NOT_READY
        return AgentResult(
            self.name,
            None,
            status,
            {
                "risk_gate": Gate.GREEN.value if status == Status.PASS else Gate.DATA_NOT_READY.value,
                "max_drawdown": max_drawdown,
                "mae": mae,
                "stress_loss": stress_loss,
            },
            tuple(blockers),
        )


class EvidenceAgent:
    name = "evidence"

    def run(self, claims: list[Mapping[str, Any]]) -> AgentResult:
        blockers: list[str] = []
        for claim in claims:
            claim_id = str(claim.get("claim_id", "UNKNOWN"))
            claim_type = str(claim.get("claim_type", ""))

            for required in ("claim_id", "claim_type", "statement", "scope"):
                if not claim.get(required):
                    blockers.append(f"{claim_id}:EVIDENCE_MISSING:{required}")

            if claim_type in {"FACT", "CALCULATION"}:
                for required in ("source_id", "source_timestamp", "available_at"):
                    if not claim.get(required):
                        blockers.append(f"{claim_id}:EVIDENCE_MISSING:{required}")

            if claim_type == "CALCULATION" and not claim.get("calculation"):
                blockers.append(f"{claim_id}:EVIDENCE_MISSING:calculation")

            if claim_type == "INFERENCE":
                if not claim.get("supporting_claim_ids"):
                    blockers.append(f"{claim_id}:EVIDENCE_MISSING:supporting_claim_ids")
                if not claim.get("reasoning"):
                    blockers.append(f"{claim_id}:EVIDENCE_MISSING:reasoning")

        status = Status.PASS if not blockers else Status.DATA_NOT_READY
        return AgentResult(
            self.name,
            None,
            status,
            {"claim_count": len(claims)},
            tuple(sorted(set(blockers))),
        )

class EquitySignalAgent:
    asset = AssetClass.EQUITY
    name = "equity_signal"

    def run(self, features: Mapping[str, Any]) -> AgentResult:
        # Adapter only. Existing Stock Score / BuyStrength remains source of truth.
        state = str(features.get("signal_state", "DATA_NOT_READY"))
        if state == "DATA_NOT_READY":
            return AgentResult(self.name, self.asset, Status.DATA_NOT_READY, {},
                               ("EQUITY_SIGNAL_DATA_NOT_READY",))
        return AgentResult(
            self.name, self.asset, Status.PASS,
            {"signal_state": state, "source": "EXISTING_STOCK_SCORE_BUYSTRENGTH"},
        )


class GoldSignalAgent:
    asset = AssetClass.GOLD
    name = "gold_signal"

    def run(self, features: Mapping[str, Any]) -> AgentResult:
        state = str(features.get("signal_state", "DATA_NOT_READY"))
        if state == "DATA_NOT_READY":
            return AgentResult(self.name, self.asset, Status.DATA_NOT_READY, {},
                               ("GOLD_SIGNAL_DATA_NOT_READY",))
        return AgentResult(
            self.name, self.asset, Status.PASS,
            {"signal_state": state, "source": "GOLD_RULE_VERSION_PENDING"},
        )


class CryptoSignalAgent:
    asset = AssetClass.CRYPTO
    name = "crypto_signal"

    def run(self, features: Mapping[str, Any]) -> AgentResult:
        state = str(features.get("signal_state", "DATA_NOT_READY"))
        if state == "DATA_NOT_READY":
            return AgentResult(self.name, self.asset, Status.DATA_NOT_READY, {},
                               ("CRYPTO_SIGNAL_DATA_NOT_READY",))
        return AgentResult(
            self.name, self.asset, Status.PASS,
            {
                "signal_state": state,
                "threshold_source": "crypto-market-regime-entry-v0.2",
                "permission_independent": True,
            },
        )


class DecisionAgent:
    name = "decision"

    def run(
        self,
        *,
        asset: AssetClass,
        signal: AgentResult,
        permission: AgentResult,
        regime: AgentResult,
        risk: AgentResult,
        evidence: AgentResult,
        hallucination: AgentResult,
    ) -> DecisionContract:
        blockers: list[str] = [
            *signal.blocker_codes,
            *permission.blocker_codes,
            *regime.blocker_codes,
            *risk.blocker_codes,
            *evidence.blocker_codes,
            *hallucination.blocker_codes,
        ]

        if signal.status != Status.PASS:
            blockers.append("SIGNAL_NOT_READY")
        if permission.status != Status.PASS:
            blockers.append("PERMISSION_BLOCK")
        if regime.status != Status.PASS:
            blockers.append("REGIME_NOT_READY")
        if risk.status != Status.PASS:
            blockers.append("RISK_NOT_READY")
        if evidence.status != Status.PASS:
            blockers.append("EVIDENCE_NOT_READY")
        if hallucination.status != Status.PASS:
            blockers.append("HALLUCINATION_GUARD_BLOCK")

        # Hard kill switch. Never derived from score or exposure.
        return DecisionContract(
            asset=asset,
            signal_state=str(signal.payload.get("signal_state", "DATA_NOT_READY")),
            permission_status=permission.status,
            market_gate=Gate(
                regime.payload.get("market_gate", Gate.DATA_NOT_READY.value)
            ),
            risk_gate=Gate(
                risk.payload.get("risk_gate", Gate.DATA_NOT_READY.value)
            ),
            evidence_status=evidence.status,
            hallucination_status=hallucination.status,
            buy_allowed=BUY_ALLOWED,
            execution_allowed=EXECUTION_ALLOWED,
            blocker_codes=tuple(sorted(set(blockers))),
        )


class MultiAssetOrchestrator:
    """Deterministic coordinator; agents communicate through immutable results."""

    def __init__(self) -> None:
        self.data_pit = DataPITAgent()
        self.regime = RegimeAgent()
        self.permission = PermissionAgent()
        self.risk = RiskAgent()
        self.evidence = EvidenceAgent()
        self.hallucination_guard = HallucinationGuardAgent()
        self.signals: dict[AssetClass, SignalAgent] = {
            AssetClass.EQUITY: EquitySignalAgent(),
            AssetClass.GOLD: GoldSignalAgent(),
            AssetClass.CRYPTO: CryptoSignalAgent(),
        }
        self.decision = DecisionAgent()

    def run(
        self,
        *,
        asset: AssetClass,
        decision_timestamp: datetime,
        observations: list[PITObservation],
        required_series: set[str],
        axis_scores: Mapping[str, float],
        regime_weights: Mapping[str, float],
        signal_features: Mapping[str, Any],
        evidence_claims: list[Mapping[str, Any]],
        risk_inputs: Mapping[str, Any],
        permission_inputs: Mapping[str, bool],
    ) -> DecisionContract:
        pit = self.data_pit.run(
            observations,
            decision_timestamp=decision_timestamp,
            required_series=required_series,
        )
        if pit.status != Status.PASS:
            # Fail-closed before any downstream promotion.
            blocked_signal = AgentResult(
                self.signals[asset].name, asset, Status.DATA_NOT_READY, {},
                ("PIT_GATE_NOT_GREEN",),
            )
            return self.decision.run(
                asset=asset,
                signal=blocked_signal,
                permission=AgentResult(
                    self.permission.name, None, Status.DATA_NOT_READY, {},
                    ("PIT_GATE_NOT_GREEN",),
                ),
                regime=AgentResult(
                    self.regime.name, None, Status.DATA_NOT_READY, {},
                    ("PIT_GATE_NOT_GREEN",),
                ),
                risk=AgentResult(
                    self.risk.name, None, Status.DATA_NOT_READY, {},
                    ("PIT_GATE_NOT_GREEN",),
                ),
                evidence=AgentResult(
                    self.evidence.name, None, Status.DATA_NOT_READY, {},
                    ("PIT_GATE_NOT_GREEN",),
                ),
                hallucination=AgentResult(
                    self.hallucination_guard.name, None, Status.DATA_NOT_READY, {},
                    ("PIT_GATE_NOT_GREEN",),
                ),
            )

        regime = self.regime.run(axis_scores, weights=regime_weights)
        signal = self.signals[asset].run(signal_features)
        permission = self.permission.run(
            market_gate=Gate(regime.payload["market_gate"]),
            **permission_inputs,
        )
        risk = self.risk.run(**risk_inputs)
        evidence = self.evidence.run(evidence_claims)

        guard_result = self.hallucination_guard.verify(
            evidence_claims,
            decision_timestamp=decision_timestamp,
        )
        hallucination = AgentResult(
            self.hallucination_guard.name,
            None,
            Status.PASS if guard_result.status == "PASS" else (
                Status.DATA_NOT_READY
                if guard_result.status == "DATA_NOT_READY"
                else Status.BLOCKED
            ),
            {
                "verified_claims": guard_result.verified_claims,
                "total_claims": guard_result.total_claims,
                "findings": [
                    {
                        "claim_id": finding.claim_id,
                        "status": finding.status.value,
                        "reason_codes": list(finding.reason_codes),
                    }
                    for finding in guard_result.findings
                ],
            },
            guard_result.blocker_codes,
        )

        return self.decision.run(
            asset=asset,
            signal=signal,
            permission=permission,
            regime=regime,
            risk=risk,
            evidence=evidence,
            hallucination=hallucination,
        )
