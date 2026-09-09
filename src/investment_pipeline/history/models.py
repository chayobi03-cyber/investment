from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class MarketSnapshot:
    snapshot_id: str
    as_of: str
    source_timestamp: str | None = None
    kospi: float | None = None
    kosdaq: float | None = None
    usdkrw: float | None = None
    jpykrw: float | None = None
    sp500: float | None = None
    nasdaq: float | None = None
    vix: float | None = None
    us10y: float | None = None
    axis_1: float | None = None
    axis_2: float | None = None
    axis_3: float | None = None
    axis_4: float | None = None
    axis_5: float | None = None
    regime: str | None = None
    model_version: str = "unknown"
    data_version: str = "unknown"
    record_origin: str = "live"

    def to_record(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class StockSnapshot:
    snapshot_id: str
    as_of: str
    ticker: str
    name: str | None = None
    close: float | None = None
    volume: float | None = None
    foreign_net: float | None = None
    institution_net: float | None = None
    sector_code: str | None = None
    long_score: float | None = None
    medium_score: float | None = None
    short_score: float | None = None
    composite_score: float | None = None
    rank: int | None = None
    action: str | None = None
    data_completeness: str | None = None
    model_version: str = "unknown"
    data_version: str = "unknown"
    record_origin: str = "live"

    def to_record(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DecisionLog:
    decision_id: str
    decision_at: str
    ticker: str
    decision: str
    price: float | None = None
    position_size: float | None = None
    regime: str | None = None
    score: float | None = None
    rank: int | None = None
    reason_code: str | None = None
    reason_text: str | None = None
    confidence: float | None = None
    review_horizon_days: int | None = None
    model_version: str = "unknown"
    data_version: str = "unknown"
    record_origin: str = "live"
    source_ref: str | None = None

    def to_record(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class OutcomeLog:
    outcome_id: str
    decision_id: str
    evaluation_date: str
    horizon_days: int
    entry_price: float | None = None
    current_price: float | None = None
    return_pct: float | None = None
    benchmark_return_pct: float | None = None
    alpha_pct: float | None = None
    max_drawdown_pct: float | None = None
    hit: bool | None = None
    thesis_status: str | None = None
    model_version: str = "unknown"

    def to_record(self) -> dict[str, Any]:
        return asdict(self)
