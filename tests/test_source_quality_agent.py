from src.investment_pipeline.source_quality_agent import SourceQualityAgent


def test_unknown_source_cannot_meet_primary_requirement():
    result = SourceQualityAgent().run(
        [{
            "claim_id": "C1",
            "claim_type": "FACT",
            "source_id": "SRC1",
            "minimum_source_class": "PRIMARY_OFFICIAL",
        }],
        [{"source_id": "SRC1", "source_class": "UNKNOWN"}],
    )
    assert result.status == "BLOCKED"
    assert any("SOURCE_QUALITY_BELOW_MINIMUM" in b for b in result.blocker_codes)


def test_primary_source_passes_primary_requirement():
    result = SourceQualityAgent().run(
        [{
            "claim_id": "C1",
            "claim_type": "FACT",
            "source_id": "SRC1",
            "minimum_source_class": "PRIMARY_OFFICIAL",
        }],
        [{"source_id": "SRC1", "source_class": "PRIMARY_OFFICIAL"}],
    )
    assert result.status == "PASS"
