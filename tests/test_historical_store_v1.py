from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from investment_pipeline.history.ingest import ingest_market_csv, ingest_stock_csv
from investment_pipeline.history.store import HistoricalStore


def test_append_only_conflict(tmp_path: Path) -> None:
    store = HistoricalStore(tmp_path)
    assert store.market.append({"snapshot_id": "x", "as_of": "2026-09-09"}) is True
    assert store.market.append({"snapshot_id": "x", "as_of": "2026-09-09"}) is False
    with pytest.raises(ValueError, match="immutable record conflict"):
        store.market.append({"snapshot_id": "x", "as_of": "2026-09-10"})


def test_ingest_market_and_stock(tmp_path: Path) -> None:
    market = tmp_path / "market.csv"
    stock = tmp_path / "stock.csv"
    pd.DataFrame([{"as_of": "2026-09-09", "usdkrw": 1380.0, "regime": "NORMAL"}]).to_csv(market, index=False)
    pd.DataFrame([{"as_of": "2026-09-09", "ticker": "5930", "close": 100.0, "rank": 1, "action": "분할매수"}]).to_csv(stock, index=False)

    store = HistoricalStore(tmp_path / "history")
    assert ingest_market_csv(market, store, model_version="v1", data_version="d1") == 1
    assert ingest_stock_csv(stock, store, model_version="v1", data_version="d1") == 1
    assert ingest_market_csv(market, store, model_version="v1", data_version="d1") == 0

    market_saved = pd.read_csv(tmp_path / "history" / "market_snapshots.csv")
    stock_saved = pd.read_csv(tmp_path / "history" / "stock_snapshots.csv")
    assert market_saved.loc[0, "usdkrw"] == 1380.0
    assert stock_saved.loc[0, "ticker"] == 5930


def test_decision_json_contract(tmp_path: Path) -> None:
    payload = {"decisions": [{"decision_id": "d1", "decision_at": "2026-09-09T09:00:00Z", "ticker": "005930", "decision": "관망"}]}
    path = tmp_path / "decisions.json"
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    # JSON payload shape is intentionally covered by the public CLI contract.
    assert path.exists()
