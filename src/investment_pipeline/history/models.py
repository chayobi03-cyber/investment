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


@dataclass(frozen=True)
class MarketRunSnapshot:
    """Immutable point-in-time monitor run stored in the Historical DB v1 ledger."""

    run_id: str
    analysis_asof: str
    session_date: str
    run_kind: str
    session: str
    data_quality: str
    decision_state: str
    regime: str | None = None
    risk_state: str | None = None
    trend_state: str | None = None
    breadth_state: str | None = None
    leaders_state: str | None = None
    rates_state: str | None = None
    fx_state: str | None = None
    oil_state: str | None = None
    gold_state: str | None = None
    input_sha256: str = ""
    code_sha: str = ""
    config_version: str = ""
    rule_version: str = ""
    calculation_version: str = ""
    summary_json: str = "{}"
    envelope_json: str = "{}"
    source_snapshot_json: str = "{}"
    record_origin: str = "market_monitor"

    def to_record(self) -> dict[str, Any]:
        return asdict(self)
