"""Deterministic market-data integrity checks."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping


@dataclass(frozen=True)
class DataIssue:
    code: str
    symbol: str
    timestamp: str
    message: str
    severity: str = "ERROR"


def validate_ohlc(rows: Iterable[Mapping[str, object]]) -> list[DataIssue]:
    issues: list[DataIssue] = []
    for row in rows:
        symbol = str(row["symbol"])
        timestamp = str(row["timestamp"])
        open_px = float(row["open"])
        high_px = float(row["high"])
        low_px = float(row["low"])
        close_px = float(row["close"])
        if not (low_px <= open_px <= high_px):
            issues.append(DataIssue("OHLC_RANGE", symbol, timestamp, "open is outside low/high"))
        if not (low_px <= close_px <= high_px):
            issues.append(DataIssue("OHLC_RANGE", symbol, timestamp, "close is outside low/high"))
        if min(open_px, high_px, low_px, close_px) <= 0:
            issues.append(DataIssue("NON_POSITIVE_PRICE", symbol, timestamp, "price must be positive"))
    return issues


def flag_return_outliers(
    rows: Iterable[Mapping[str, object]],
    threshold: float = 0.25,
) -> list[DataIssue]:
    """Flag large close-to-close moves; never delete them."""
    ordered = sorted(rows, key=lambda row: (str(row["symbol"]), str(row["timestamp"])))
    issues: list[DataIssue] = []
    previous: dict[str, float] = {}
    for row in ordered:
        symbol = str(row["symbol"])
        timestamp = str(row["timestamp"])
        close_px = float(row["close"])
        if symbol in previous:
            ret = close_px / previous[symbol] - 1.0
            if abs(ret) > threshold:
                issues.append(
                    DataIssue(
                        "RETURN_OUTLIER",
                        symbol,
                        timestamp,
                        f"close-to-close return {ret:.4f} exceeds threshold {threshold:.4f}",
                        severity="REVIEW",
                    )
                )
        previous[symbol] = close_px
    return issues


def qa_pass(issues: Iterable[DataIssue]) -> bool:
    return not any(issue.severity == "ERROR" for issue in issues)
