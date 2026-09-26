from datetime import datetime, timezone

from src.investment_pipeline.hallucination_guard_agent import (
    HallucinationGuardAgent,
    VerificationStatus,
)


NOW = datetime(2026, 9, 26, tzinfo=timezone.utc)


def test_fact_requires_pit_provenance():
    result = HallucinationGuardAgent().verify(
        [{
            "claim_id": "C1",
            "claim_type": "FACT",
            "statement": "DXY was 100",
            "scope": "2026-09-26 decision",
        }],
        decision_timestamp=NOW,
    )
    assert result.status == "BLOCKED"
    assert result.findings[0].status == VerificationStatus.UNSUPPORTED


def test_lookahead_is_blocked():
    result = HallucinationGuardAgent().verify(
        [{
            "claim_id": "C1",
            "claim_type": "FACT",
            "statement": "DXY was 100",
            "scope": "2026-09-26 decision",
            "source_id": "TEST",
            "source_timestamp": NOW,
            "available_at": datetime(2026, 9, 27, tzinfo=timezone.utc),
        }],
        decision_timestamp=NOW,
    )
    assert result.status == "BLOCKED"
    assert result.findings[0].status == VerificationStatus.LOOKAHEAD


def test_calculation_mismatch_is_blocked():
    result = HallucinationGuardAgent().verify(
        [{
            "claim_id": "C1",
            "claim_type": "CALCULATION",
            "statement": "20D return is 10%",
            "scope": "BTC",
            "source_id": "TEST",
            "source_timestamp": NOW,
            "available_at": NOW,
            "calculation": "110/100-1",
            "expected_value": 0.10,
            "actual_value": 0.25,
        }],
        decision_timestamp=NOW,
    )
    assert result.status == "BLOCKED"
    assert result.findings[0].status == VerificationStatus.CALCULATION_UNVERIFIED


def test_inference_requires_verified_support():
    result = HallucinationGuardAgent().verify(
        [{
            "claim_id": "I1",
            "claim_type": "INFERENCE",
            "statement": "Rates may pressure risk assets",
            "scope": "2026-09-26",
            "supporting_claim_ids": ["C1"],
            "reasoning": "Higher real yields can tighten financial conditions",
            "explicitly_labeled_inference": True,
        }],
        decision_timestamp=NOW,
    )
    assert result.status == "BLOCKED"
    assert any("INFERENCE_SUPPORT_UNKNOWN" in b for b in result.blocker_codes)


def test_verified_fact_and_calculation_pass():
    result = HallucinationGuardAgent().verify(
        [
            {
                "claim_id": "C1",
                "claim_type": "FACT",
                "statement": "DXY was 100",
                "scope": "decision date",
                "source_id": "TEST",
                "source_timestamp": NOW,
                "available_at": NOW,
            },
            {
                "claim_id": "C2",
                "claim_type": "CALCULATION",
                "statement": "Return is 10%",
                "scope": "asset A",
                "source_id": "TEST",
                "source_timestamp": NOW,
                "available_at": NOW,
                "calculation": "110/100-1",
                "expected_value": 0.10,
                "actual_value": 0.10,
            },
        ],
        decision_timestamp=NOW,
    )
    assert result.status == "PASS"
    assert result.verified_claims == 2
