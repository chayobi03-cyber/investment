from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pandas as pd

from .models import DecisionLog, MarketSnapshot, StockSnapshot
from .store import HistoricalStore


def _stable_id(prefix: str, *parts: object) -> str:
    payload = "|".join("" if p is None else str(p) for p in parts)
    digest = hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
    return f"{prefix}_{digest}"


def _value(row: pd.Series, name: str) -> Any:
    value = row.get(name)
    return None if pd.isna(value) else value


def ingest_market_csv(path: str | Path, store: HistoricalStore, *, model_version: str, data_version: str, record_origin: str = "live") -> int:
    df = pd.read_csv(path)
    required = {"as_of"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"market input missing columns: {sorted(missing)}")

    inserted = 0
    for _, row in df.iterrows():
        as_of = str(row["as_of"])
        snapshot = MarketSnapshot(
            snapshot_id=_stable_id("mkt", as_of, data_version, model_version),
            as_of=as_of,
            source_timestamp=_value(row, "source_timestamp"),
            kospi=_value(row, "kospi"),
            kosdaq=_value(row, "kosdaq"),
            usdkrw=_value(row, "usdkrw"),
            jpykrw=_value(row, "jpykrw"),
            sp500=_value(row, "sp500"),
            nasdaq=_value(row, "nasdaq"),
            vix=_value(row, "vix"),
            us10y=_value(row, "us10y"),
            axis_1=_value(row, "axis_1"),
            axis_2=_value(row, "axis_2"),
            axis_3=_value(row, "axis_3"),
            axis_4=_value(row, "axis_4"),
            axis_5=_value(row, "axis_5"),
            regime=_value(row, "regime"),
            model_version=model_version,
            data_version=data_version,
            record_origin=record_origin,
        )
        inserted += int(store.append_market(snapshot))
    return inserted


def ingest_stock_csv(path: str | Path, store: HistoricalStore, *, model_version: str, data_version: str, record_origin: str = "live") -> int:
    df = pd.read_csv(path)
    required = {"as_of", "ticker"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"stock input missing columns: {sorted(missing)}")

    inserted = 0
    for _, row in df.iterrows():
        as_of = str(row["as_of"])
        ticker = str(row["ticker"]).zfill(6)
        snapshot = StockSnapshot(
            snapshot_id=_stable_id("stk", as_of, ticker, model_version, data_version),
            as_of=as_of,
            ticker=ticker,
            name=_value(row, "name"),
            close=_value(row, "close"),
            volume=_value(row, "volume"),
            foreign_net=_value(row, "foreign_net"),
            institution_net=_value(row, "institution_net"),
            sector_code=_value(row, "sector_code"),
            long_score=_value(row, "long_score"),
            medium_score=_value(row, "medium_score"),
            short_score=_value(row, "short_score"),
            composite_score=_value(row, "composite_score"),
            rank=None if pd.isna(row.get("rank")) else int(row["rank"]),
            action=_value(row, "action"),
            data_completeness=_value(row, "data_completeness"),
            model_version=model_version,
            data_version=data_version,
            record_origin=record_origin,
        )
        inserted += int(store.append_stock(snapshot))
    return inserted


def ingest_decisions_json(path: str | Path, store: HistoricalStore) -> int:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    records = raw if isinstance(raw, list) else raw.get("decisions", [])
    inserted = 0
    for item in records:
        decision = DecisionLog(**item)
        inserted += int(store.append_decision(decision))
    return inserted
