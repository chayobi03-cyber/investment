from __future__ import annotations

from pathlib import Path

import pandas as pd

from .models import OutcomeLog
from .store import HistoricalStore


def _max_drawdown(prices: pd.Series) -> float | None:
    prices = pd.to_numeric(prices, errors="coerce").dropna()
    if prices.empty:
        return None
    drawdown = prices / prices.cummax() - 1.0
    return float(drawdown.min() * 100.0)


def evaluate_decisions(
    decisions_csv: str | Path,
    price_csv: str | Path,
    store: HistoricalStore,
    *,
    horizons: tuple[int, ...] = (1, 5, 20, 60),
    benchmark_column: str | None = None,
    model_version: str = "outcome-v1",
) -> int:
    decisions = pd.read_csv(decisions_csv)
    prices = pd.read_csv(price_csv)
    for frame, required, label in (
        (decisions, {"decision_id", "decision_at", "ticker", "price"}, "decisions"),
        (prices, {"date", "ticker", "close"}, "prices"),
    ):
        missing = required - set(frame.columns)
        if missing:
            raise ValueError(f"{label} input missing columns: {sorted(missing)}")

    decisions["decision_at"] = pd.to_datetime(decisions["decision_at"], utc=True)
    prices["date"] = pd.to_datetime(prices["date"], utc=True)
    prices = prices.sort_values(["ticker", "date"])
    inserted = 0

    for _, decision in decisions.iterrows():
        ticker = str(decision["ticker"]).zfill(6)
        entry_price = float(decision["price"])
        history = prices[prices["ticker"].astype(str).str.zfill(6) == ticker]
        future = history[history["date"] > decision["decision_at"]].reset_index(drop=True)
        for horizon in horizons:
            if len(future) < horizon:
                continue
            target = future.iloc[horizon - 1]
            current_price = float(target["close"])
            return_pct = (current_price / entry_price - 1.0) * 100.0
            benchmark_return_pct = None
            if benchmark_column and benchmark_column in target.index:
                benchmark_return_pct = target[benchmark_column]
            alpha_pct = None if benchmark_return_pct is None else return_pct - float(benchmark_return_pct)
            path = future.iloc[:horizon]["close"]
            outcome = OutcomeLog(
                outcome_id=f"{decision['decision_id']}_H{horizon}",
                decision_id=str(decision["decision_id"]),
                evaluation_date=str(target["date"]),
                horizon_days=horizon,
                entry_price=entry_price,
                current_price=current_price,
                return_pct=return_pct,
                benchmark_return_pct=benchmark_return_pct,
                alpha_pct=alpha_pct,
                max_drawdown_pct=_max_drawdown(path),
                hit=None,
                thesis_status=None,
                model_version=model_version,
            )
            inserted += int(store.append_outcome(outcome))
    return inserted
