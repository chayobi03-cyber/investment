from src.investment_pipeline.claim_contract import validate_claim_structure


def test_fact_contract_requires_source_and_scope():
    blockers = validate_claim_structure({
        "claim_id": "C1",
        "claim_type": "FACT",
        "statement": "fact",
        "scope": "decision",
    })
    assert any("source_id" in b for b in blockers)
    assert any("source_timestamp" in b for b in blockers)
    assert any("available_at" in b for b in blockers)


def test_inference_contract_requires_support_and_reasoning():
    blockers = validate_claim_structure({
        "claim_id": "I1",
        "claim_type": "INFERENCE",
        "statement": "inference",
        "scope": "decision",
    })
    assert any("supporting_claim_ids" in b for b in blockers)
    assert any("reasoning" in b for b in blockers)


def test_valid_calculation_contract_passes_structure():
    blockers = validate_claim_structure({
        "claim_id": "C2",
        "claim_type": "CALCULATION",
        "statement": "return",
        "scope": "asset",
        "source_id": "SRC",
        "source_timestamp": "2026-09-26T00:00:00+00:00",
        "available_at": "2026-09-26T00:00:00+00:00",
        "calculation": "110/100-1",
    })
    assert blockers == ()