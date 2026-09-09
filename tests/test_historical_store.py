import pytest

from investment_pipeline.history import DecisionLog, HistoricalStore, MarketSnapshot


def test_market_snapshot_is_idempotent_and_immutable(tmp_path):
    store = HistoricalStore(tmp_path)
    row = MarketSnapshot(
        snapshot_id="2026-09-09",
        as_of="2026-09-09T09:00:00+09:00",
        kospi=3520.0,
        model_version="market-v1",
        data_version="d1",
    )
    assert store.append_market(row) is True
    assert store.append_market(row) is False
    with pytest.raises(ValueError, match="immutable record conflict"):
        store.append_market(
            MarketSnapshot(
                snapshot_id="2026-09-09",
                as_of="2026-09-09T09:00:00+09:00",
                kospi=3600.0,
                model_version="market-v1",
                data_version="d1",
            )
        )


def test_decision_and_market_use_separate_records(tmp_path):
    store = HistoricalStore(tmp_path)
    assert store.append_market(
        MarketSnapshot(snapshot_id="m1", as_of="2026-09-09T09:00:00+09:00", regime="risk-on")
    )
    assert store.append_decision(
        DecisionLog(
            decision_id="d1",
            decision_at="2026-09-09T15:31:00+09:00",
            ticker="TSM",
            decision="BUY",
            price=432.70,
            score=78.0,
        )
    )
    assert (tmp_path / "market_snapshots.csv").exists()
    assert (tmp_path / "decisions.csv").exists()
    assert not (tmp_path / "outcomes.csv").exists()
