from datetime import datetime, timezone

from src.investment_pipeline.source_retrieval_agent import (
    SourceRecord,
    SourceRetrievalAgent,
)


NOW = datetime(2026, 9, 26, tzinfo=timezone.utc)


def source():
    return SourceRecord(
        source_id="SRC1",
        title="Test source",
        source_url="https://example.test/source",
        source_type="test",
        available_at=NOW,
        retrieved_at=NOW,
        content_hash="abc123",
    )


def test_missing_cited_source_is_blocked():
    result = SourceRetrievalAgent().run(
        [{
            "claim_id": "C1",
            "claim_type": "FACT",
            "source_id": "MISSING",
        }],
        [source()],
        decision_timestamp=NOW,
    )
    assert result.status == "DATA_NOT_READY"
    assert any("SOURCE_NOT_RETRIEVED" in b for b in result.blocker_codes)


def test_source_available_after_decision_is_blocked():
    late = SourceRecord(
        source_id="SRC1",
        title="Test",
        source_url="https://example.test/source",
        source_type="test",
        available_at=datetime(2026, 9, 27, tzinfo=timezone.utc),
        retrieved_at=datetime(2026, 9, 27, tzinfo=timezone.utc),
        content_hash="abc",
    )
    result = SourceRetrievalAgent().run([], [late], decision_timestamp=NOW)
    assert result.status == "DATA_NOT_READY"
    assert "SOURCE_LOOKAHEAD:SRC1" in result.blocker_codes
