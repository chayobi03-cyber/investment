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
        midpoint = (open_px + close_px) / 2.0
        if midpoint > 0 and (high_px - low_px) / midpoint > 0.50:
            issues.append(
                DataIssue(
                    "INTRAPERIOD_RANGE_ANOMALY",
                    symbol,
                    timestamp,
                    "high/low range exceeds 50% of the open/close midpoint; requires source verification",
                    severity="REVIEW",
                )
            )
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


def find_duplicate_timestamps(rows: Iterable[Mapping[str, object]]) -> list[DataIssue]:
    seen: set[tuple[str, str]] = set()
    issues: list[DataIssue] = []
    for row in rows:
        key = (str(row["symbol"]), str(row["timestamp"]))
        if key in seen:
            issues.append(DataIssue("DUPLICATE_TIMESTAMP", key[0], key[1], "duplicate symbol/timestamp observation"))
        else:
            seen.add(key)
    return issues


def find_missing_timestamps(
    rows: Iterable[Mapping[str, object]],
    expected_timestamps: Mapping[str, Iterable[str]],
) -> list[DataIssue]:
    observed: dict[str, set[str]] = {}
    for row in rows:
        observed.setdefault(str(row["symbol"]), set()).add(str(row["timestamp"]))
    issues: list[DataIssue] = []
    for symbol, expected in expected_timestamps.items():
        for timestamp in expected:
            if timestamp not in observed.get(symbol, set()):
                issues.append(DataIssue("MISSING_OBSERVATION", symbol, str(timestamp), "expected observation is absent"))
    return issues


def find_timestamp_order_issues(rows: Iterable[Mapping[str, object]]) -> list[DataIssue]:
    issues: list[DataIssue] = []
    last: dict[str, str] = {}
    for row in rows:
        symbol = str(row["symbol"])
        timestamp = str(row["timestamp"])
        if symbol in last and timestamp < last[symbol]:
            issues.append(DataIssue("TIMESTAMP_ORDER", symbol, timestamp, f"timestamp precedes prior observation {last[symbol]}"))
        last[symbol] = timestamp
    return issues


def find_point_in_time_violations(rows: Iterable[Mapping[str, object]]) -> list[DataIssue]:
    issues: list[DataIssue] = []
    for row in rows:
        symbol = str(row["symbol"])
        timestamp = str(row["timestamp"])
        decision_timestamp = str(row["decision_timestamp"])
        if timestamp > decision_timestamp:
            issues.append(
                DataIssue(
                    "POINT_IN_TIME_VIOLATION",
                    symbol,
                    timestamp,
                    f"observation timestamp {timestamp} is later than decision timestamp {decision_timestamp}",
                )
            )
    return issues


def qa_pass(issues: Iterable[DataIssue]) -> bool:
    """Basic data validity: REVIEW findings remain visible but do not fail this local QA predicate."""
    return not any(issue.severity == "ERROR" for issue in issues)


def gate_pass(issues: Iterable[DataIssue]) -> bool:
    """Strict promotion gate: unresolved ERROR or REVIEW findings fail closed."""
    return not any(issue.severity in {"ERROR", "REVIEW"} for issue in issues)
