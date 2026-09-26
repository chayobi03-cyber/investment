from src.investment_pipeline.conflict_detection_agent import ConflictDetectionAgent


def test_unresolved_explicit_conflict_blocks():
    result = ConflictDetectionAgent().run([
        {
            "claim_id": "A",
            "conflict_group": "RATE_IMPACT",
            "stance": "FOR",
        },
        {
            "claim_id": "B",
            "conflict_group": "RATE_IMPACT",
            "stance": "AGAINST",
        },
    ])
    assert result.status == "BLOCKED"
    assert "CONFLICT_UNRESOLVED:RATE_IMPACT" in result.blocker_codes


def test_resolved_conflict_does_not_block():
    result = ConflictDetectionAgent().run([
        {
            "claim_id": "A",
            "conflict_group": "RATE_IMPACT",
            "stance": "FOR",
            "conflict_resolution": "Prefer primary source based on dated release",
        },
        {
            "claim_id": "B",
            "conflict_group": "RATE_IMPACT",
            "stance": "AGAINST",
        },
    ])
    assert result.status == "PASS"
