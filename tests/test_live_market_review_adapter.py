from __future__ import annotations

import json
from pathlib import Path

import pytest

from investment_pipeline.history.live_adapter import LiveReviewValidationError, record_live_review


def test_record_live_review_is_idempotent(tmp_path: Path) -> None:
    payload = {
        "as_of": "2026-09-09",
        "model_version": "market-review-v1",
        "data_version": "2026-09-09",
        "market": {"usdkrw": 1380.0, "regime": "NORMAL"},
        "stocks": [
            {"ticker": "005930", "name": "Samsung Electronics", "rank": 1, "action": "분할매수"}
        ],
        "decisions": [
            {"decision_at": "2026-09-09T20:00:00+09:00", "ticker": "005930", "decision": "관망"}
        ],
    }
    first = record_live_review(payload, root=tmp_path / "history")
    second = record_live_review(payload, root=tmp_path / "history")

    assert first["market_records_written"] == 1
    assert first["stock_records_written"] == 1
    assert first["decision_records_written"] == 1
    assert second["market_records_written"] == 0
    assert second["stock_records_written"] == 0
    assert second["decision_records_written"] == 0


def test_missing_versions_are_rejected(tmp_path: Path) -> None:
    with pytest.raises(LiveReviewValidationError, match="model_version"):
        record_live_review({"as_of": "2026-09-09", "data_version": "d1", "market": {}}, root=tmp_path)


def test_missing_market_object_is_rejected(tmp_path: Path) -> None:
    with pytest.raises(LiveReviewValidationError, match="market"):
        record_live_review(
            {"as_of": "2026-09-09", "model_version": "m1", "data_version": "d1"},
            root=tmp_path,
        )


def test_unknown_market_values_stay_empty(tmp_path: Path) -> None:
    payload = {
        "as_of": "2026-09-09",
        "model_version": "m1",
        "data_version": "d1",
        "market": {"usdkrw": None, "regime": "UNKNOWN"},
    }
    record_live_review(payload, root=tmp_path)
    text = (tmp_path / "market_snapshots.csv").read_text(encoding="utf-8")
    assert '""' in text
