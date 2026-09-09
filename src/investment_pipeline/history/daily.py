from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .ingest import ingest_market_csv, ingest_stock_csv, ingest_decisions_json
from .store import HistoricalStore


def ingest_daily_bundle(
    *,
    market_csv: str | Path,
    stock_csv: str | Path,
    decisions_json: str | Path | None = None,
    root: str | Path = "data/history",
    model_version: str,
    data_version: str,
    record_origin: str = "live",
) -> dict[str, Any]:
    """Persist one daily market-review bundle into the historical store.

    The bundle is intentionally explicit: no values are inferred or fabricated.
    """
    store = HistoricalStore(root)
    market_written = ingest_market_csv(
        market_csv,
        store,
        model_version=model_version,
        data_version=data_version,
        record_origin=record_origin,
    )
    stock_written = ingest_stock_csv(
        stock_csv,
        store,
        model_version=model_version,
        data_version=data_version,
        record_origin=record_origin,
    )
    decision_written = 0
    if decisions_json is not None:
        decision_written = ingest_decisions_json(decisions_json, store)

    manifest = {
        "data_version": data_version,
        "model_version": model_version,
        "record_origin": record_origin,
        "market_records_written": market_written,
        "stock_records_written": stock_written,
        "decision_records_written": decision_written,
    }
    manifest_path = Path(root) / "daily_ingest_manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest
