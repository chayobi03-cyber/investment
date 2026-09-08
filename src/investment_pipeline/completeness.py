from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import pandas as pd


@dataclass(frozen=True)
class CompletenessReport:
    rows_expected: int
    rows_present: int
    required_columns_missing: tuple[str, ...]
    critical_missing_rows: int
    completeness_pct: float
    status: str


def validate_required_columns(df: pd.DataFrame, required: Iterable[str]) -> tuple[str, ...]:
    return tuple(c for c in required if c not in df.columns)


def check_stock_snapshot(
    df: pd.DataFrame,
    tickers: Iterable[str],
    required_columns: Iterable[str],
) -> CompletenessReport:
    required = tuple(required_columns)
    missing_cols = validate_required_columns(df, required)
    ticker_set = set(tickers)
    rows_expected = len(ticker_set)
    if "ticker" not in df.columns:
        return CompletenessReport(rows_expected, 0, missing_cols + ("ticker",), rows_expected, 0.0, "FAIL")

    present = set(df["ticker"].dropna().astype(str)) & ticker_set
    rows_present = len(present)
    critical = 0
    if rows_present:
        subset = df[df["ticker"].astype(str).isin(ticker_set)]
        critical = int(subset[list(required)].isna().any(axis=1).sum()) if not missing_cols else rows_expected
    pct = 100.0 * rows_present / rows_expected if rows_expected else 0.0
    status = "GREEN" if not missing_cols and rows_present == rows_expected and critical == 0 else "FAIL"
    return CompletenessReport(rows_expected, rows_present, missing_cols, critical, pct, status)
