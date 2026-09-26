from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from math import isclose
from typing import Any, Mapping


class ClaimType(StrEnum):
    FACT = "FACT"
    CALCULATION = "CALCULATION"
    INFERENCE = "INFERENCE"


class VerificationStatus(StrEnum):
    VERIFIED = "VERIFIED"
    UNSUPPORTED = "UNSUPPORTED"
    LOOKAHEAD = "LOOKAHEAD"
    CALCULATION_UNVERIFIED = "CALCULATION_UNVERIFIED"
    SCOPE_UNSPECIFIED = "SCOPE_UNSPECIFIED"
    CONFLICT_UNRESOLVED = "CONFLICT_UNRESOLVED"
    DATA_NOT_READY = "DATA_NOT_READY"


@dataclass(frozen=True)
class VerificationFinding:
    claim_id: str
    status: VerificationStatus
    reason_codes: tuple[str, ...]


@dataclass(frozen=True)
class HallucinationGuardResult:
    status: str
    verified_claims: int
    total_claims: int
    findings: tuple[VerificationFinding, ...]
    blocker_codes: tuple[str, ...]


def _utc(value: datetime | str) -> datetime:
    parsed = value if isinstance(value, datetime) else datetime.fromisoformat(value)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


class HallucinationGuardAgent:
    """
    Deterministic claim verifier.

    This agent does not decide whether an investment is attractive.
    It only checks whether a supplied claim has sufficient evidence,
    is point-in-time eligible, and is internally supported.
    """

    name = "hallucination_guard"
    REQUIRED_BASE = ("claim_id", "claim_type", "statement", "scope")

    def verify(
        self,
        claims: list[Mapping[str, Any]],
        *,
        decision_timestamp: datetime,
    ) -> HallucinationGuardResult:
        decision_timestamp = _utc(decision_timestamp)

        if not claims:
            return HallucinationGuardResult(
                status="DATA_NOT_READY",
                verified_claims=0,
                total_claims=0,
                findings=(),
                blocker_codes=("NO_CLAIMS",),
            )

        blockers: list[str] = []
        findings: list[VerificationFinding] = []
        by_id: dict[str, Mapping[str, Any]] = {}

        for claim in claims:
            claim_id = str(claim.get("claim_id", ""))
            reasons: list[str] = []

            if not all(claim.get(key) for key in self.REQUIRED_BASE):
                reasons.append("CLAIM_FIELDS_MISSING")

            if not claim_id:
                reasons.append("CLAIM_ID_MISSING")
            elif claim_id in by_id:
                reasons.append("DUPLICATE_CLAIM_ID")
            else:
                by_id[claim_id] = claim

            claim_type = str(claim.get("claim_type", ""))
            if claim_type not in {x.value for x in ClaimType}:
                reasons.append("INVALID_CLAIM_TYPE")

            if claim_type in {ClaimType.FACT.value, ClaimType.CALCULATION.value}:
                if not claim.get("source_id") or not claim.get("source_timestamp"):
                    reasons.append("SOURCE_PROVENANCE_MISSING")
                if claim.get("available_at") is None:
                    reasons.append("AVAILABLE_AT_MISSING")
                else:
                    try:
                        available_at = _utc(claim["available_at"])
                        if available_at > decision_timestamp:
                            reasons.append("LOOKAHEAD_AVAILABLE_AT")
                    except (TypeError, ValueError):
                        reasons.append("INVALID_AVAILABLE_AT")

            if claim.get("source_timestamp"):
                try:
                    source_timestamp = _utc(claim["source_timestamp"])
                    if source_timestamp > decision_timestamp:
                        reasons.append("LOOKAHEAD_SOURCE_TIMESTAMP")
                except (TypeError, ValueError):
                    reasons.append("INVALID_SOURCE_TIMESTAMP")

            if not claim.get("scope"):
                reasons.append("SCOPE_UNSPECIFIED")

            if claim_type == ClaimType.CALCULATION.value:
                if not claim.get("calculation"):
                    reasons.append("CALCULATION_MISSING")
                if "expected_value" in claim and "actual_value" in claim:
                    expected = claim["expected_value"]
                    actual = claim["actual_value"]
                    tolerance = float(claim.get("tolerance", 1e-9))
                    if not (
                        isinstance(expected, (int, float))
                        and isinstance(actual, (int, float))
                        and isclose(
                            float(expected),
                            float(actual),
                            rel_tol=tolerance,
                            abs_tol=tolerance,
                        )
                    ):
                        reasons.append("CALCULATION_MISMATCH")

            if claim_type == ClaimType.INFERENCE.value:
                support_ids = [str(x) for x in claim.get("supporting_claim_ids", [])]
                if not support_ids:
                    reasons.append("INFERENCE_SUPPORT_MISSING")
                else:
                    unresolved = [
                        support_id
                        for support_id in support_ids
                        if support_id not in by_id
                    ]
                    if unresolved:
                        reasons.append(
                            "INFERENCE_SUPPORT_UNKNOWN:" + ",".join(sorted(unresolved))
                        )
                if not claim.get("reasoning"):
                    reasons.append("INFERENCE_REASONING_MISSING")
                if claim.get("source_id") and not claim.get("explicitly_labeled_inference"):
                    reasons.append("INFERENCE_MISLABELED_AS_FACT")

            if claim.get("conflicts_with") and not claim.get("conflict_resolution"):
                reasons.append("CONFLICT_UNRESOLVED")

            if reasons:
                if any(r.startswith("LOOKAHEAD") for r in reasons):
                    status = VerificationStatus.LOOKAHEAD
                elif "CALCULATION_MISMATCH" in reasons or "CALCULATION_MISSING" in reasons:
                    status = VerificationStatus.CALCULATION_UNVERIFIED
                elif "CONFLICT_UNRESOLVED" in reasons:
                    status = VerificationStatus.CONFLICT_UNRESOLVED
                elif "SCOPE_UNSPECIFIED" in reasons:
                    status = VerificationStatus.SCOPE_UNSPECIFIED
                else:
                    status = VerificationStatus.UNSUPPORTED
                blockers.extend(f"{claim_id}:{reason}" for reason in reasons)
            else:
                status = VerificationStatus.VERIFIED

            findings.append(
                VerificationFinding(
                    claim_id=claim_id or "UNKNOWN",
                    status=status,
                    reason_codes=tuple(sorted(set(reasons))),
                )
            )

        verified_ids = {
            finding.claim_id
            for finding in findings
            if finding.status == VerificationStatus.VERIFIED
        }
        revised: list[VerificationFinding] = []
        for claim, finding in zip(claims, findings):
            if (
                finding.status == VerificationStatus.VERIFIED
                and claim.get("claim_type") == ClaimType.INFERENCE.value
            ):
                support_ids = {str(x) for x in claim.get("supporting_claim_ids", [])}
                missing = sorted(support_ids - verified_ids)
                if missing:
                    revised.append(
                        VerificationFinding(
                            claim_id=finding.claim_id,
                            status=VerificationStatus.UNSUPPORTED,
                            reason_codes=("INFERENCE_SUPPORT_NOT_VERIFIED",),
                        )
                    )
                    blockers.append(
                        f"{finding.claim_id}:INFERENCE_SUPPORT_NOT_VERIFIED:"
                        + ",".join(missing)
                    )
                    continue
            revised.append(finding)

        findings = revised
        verified_count = sum(
            1 for finding in findings if finding.status == VerificationStatus.VERIFIED
        )
        status = "PASS" if verified_count == len(claims) and not blockers else "BLOCKED"

        return HallucinationGuardResult(
            status=status,
            verified_claims=verified_count,
            total_claims=len(claims),
            findings=tuple(findings),
            blocker_codes=tuple(sorted(set(blockers))),
        )
