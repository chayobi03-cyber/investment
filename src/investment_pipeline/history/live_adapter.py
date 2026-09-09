from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from .models import DecisionLog, MarketSnapshot, StockSnapshot
from .store import HistoricalStore


class LiveReviewValidationError(ValueError):
    """Raised when a live market-review payload is incomplete or invalid."""


def _require_text(payload: Mapping[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise LiveReviewValidationError(f"{key} must be a non-empty string")
    return value.strip()


def _stable_id(prefix: str, *parts: object) -> str:
    raw = "|".join(str(part) for part in parts)
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
    return f"{prefix}-{digest}"


def _market_snapshot(payload: Mapping[str, Any], *, model_version: str, data_version: str, origin: str) -> MarketSnapshot:
    market = payload.get("market")
    if not isinstance(market, Mapping):
        raise LiveReviewValidationError("market must be an object")
    as_of = _require_text(payload, "as_of")
    return MarketSnapshot(
        snapshot_id=str(market.get("snapshot_id") or _stable_id("market", as_of, model_version, data_version)),
        as_of=as_of,
        source_timestamp=market.get("source_timestamp"),
        kospi=market.get("kospi"),
        kosdaq=market.get("kosdaq"),
        usdkrw=market.get("usdkrw"),
        jpykrw=market.get("jpykrw"),
        sp500=market.get("sp500"),
        nasdaq=market.get("nasdaq"),
        vix=market.get("vix"),
        us10y=market.get("us10y"),
        axis_1=market.get("axis_1"),
        axis_2=market.get("axis_2"),
        axis_3=market.get("axis_3"),
        axis_4=market.get("axis_4"),
        axis_5=market.get("axis_5"),
        regime=market.get("regime"),
        model_version=model_version,
        data_version=data_version,
        record_origin=origin,
    )


def _stock_snapshots(payload: Mapping[str, Any], *, model_version: str, data_version: str, origin: str) -> list[StockSnapshot]:
    stocks = payload.get("stocks", [])
    if not isinstance(stocks, list):
        raise LiveReviewValidationError("stocks must be an array")
    as_of = _require_text(payload, "as_of")
    records: list[StockSnapshot] = []
    for item in stocks:
        if not isinstance(item, Mapping):
            raise LiveReviewValidationError("each stock must be an object")
        ticker = item.get("ticker")
        if not isinstance(ticker, str) or not ticker.strip():
            raise LiveReviewValidationError("stock.ticker must be a non-empty string")
        ticker = ticker.strip()
        records.append(
            StockSnapshot(
                snapshot_id=str(item.get("snapshot_id") or _stable_id("stock", as_of, ticker, model_version, data_version)),
                as_of=as_of,
                ticker=ticker,
                name=item.get("name"),
                close=item.get("close"),
                volume=item.get("volume"),
                foreign_net=item.get("foreign_net"),
                institution_net=item.get("institution_net"),
                sector_code=item.get("sector_code"),
                long_score=item.get("long_score"),
                medium_score=item.get("medium_score"),
                short_score=item.get("short_score"),
                composite_score=item.get("composite_score"),
                rank=item.get("rank"),
                action=item.get("action"),
                data_completeness=item.get("data_completeness"),
                model_version=model_version,
                data_version=data_version,
                record_origin=origin,
            )
        )
    return records


def _decision_logs(payload: Mapping[str, Any], *, model_version: str, data_version: str, origin: str) -> list[DecisionLog]:
    decisions = payload.get("decisions", [])
    if not isinstance(decisions, list):
        raise LiveReviewValidationError("decisions must be an array")
    records: list[DecisionLog] = []
    for item in decisions:
        if not isinstance(item, Mapping):
            raise LiveReviewValidationError("each decision must be an object")
        decision_at = item.get("decision_at")
        ticker = item.get("ticker")
        decision = item.get("decision")
        if not all(isinstance(v, str) and v.strip() for v in (decision_at, ticker, decision)):
            raise LiveReviewValidationError("decision_at, ticker and decision are required text fields")
        decision_id = str(item.get("decision_id") or _stable_id("decision", decision_at, ticker, decision, model_version, data_version))
        records.append(
            DecisionLog(
                decision_id=decision_id,
                decision_at=decision_at.strip(),
                ticker=ticker.strip(),
                decision=decision.strip(),
                price=item.get("price"),
                position_size=item.get("position_size"),
                regime=item.get("regime"),
                score=item.get("score"),
                rank=item.get("rank"),
                reason_code=item.get("reason_code"),
                reason_text=item.get("reason_text"),
                confidence=item.get("confidence"),
                review_horizon_days=item.get("review_horizon_days"),
                model_version=model_version,
                data_version=data_version,
                record_origin=origin,
                source_ref=item.get("source_ref"),
            )
        )
    return records


def record_live_review(payload: Mapping[str, Any], *, root: str | Path = "data/history", origin: str = "live") -> dict[str, Any]:
    """Validate and persist one structured live market-review result.

    The adapter does not infer missing market/stock values. Optional values stay null.
    """
    model_version = _require_text(payload, "model_version")
    data_version = _require_text(payload, "data_version")
    market = _market_snapshot(payload, model_version=model_version, data_version=data_version, origin=origin)
    stocks = _stock_snapshots(payload, model_version=model_version, data_version=data_version, origin=origin)
    decisions = _decision_logs(payload, model_version=model_version, data_version=data_version, origin=origin)

    store = HistoricalStore(root)
    market_written = int(store.append_market(market))
    stock_written = store.stock.append_many(stock.to_record() for stock in stocks)
    decision_written = store.decisions.append_many(decision.to_record() for decision in decisions)

    manifest = {
        "as_of": market.as_of,
        "model_version": model_version,
        "data_version": data_version,
        "record_origin": origin,
        "market_records_written": market_written,
        "stock_records_written": stock_written,
        "decision_records_written": decision_written,
    }
    manifest_path = Path(root) / "live_review_manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def record_live_review_file(path: str | Path, *, root: str | Path = "data/history", origin: str = "live") -> dict[str, Any]:
    source = Path(path)
    payload = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(payload, Mapping):
        raise LiveReviewValidationError("live review JSON root must be an object")
    return record_live_review(payload, root=root, origin=origin)
