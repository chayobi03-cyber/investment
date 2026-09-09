from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable, Mapping

from .models import DecisionLog, MarketSnapshot, OutcomeLog, StockSnapshot


class AppendOnlyCsvStore:
    """V1 persistence for immutable historical records."""

    def __init__(self, path: str | Path, key: str, columns: Iterable[str]):
        self.path = Path(path)
        self.key = key
        self.columns = tuple(columns)
        if key not in self.columns:
            raise ValueError(f"key {key!r} must be included in columns")

    def _read(self) -> dict[str, dict[str, str]]:
        if not self.path.exists():
            return {}
        with self.path.open("r", encoding="utf-8", newline="") as fh:
            return {row[self.key]: row for row in csv.DictReader(fh)}

    def append(self, record: Mapping[str, object]) -> bool:
        row = {column: "" if record.get(column) is None else str(record.get(column)) for column in self.columns}
        record_id = row[self.key]
        if not record_id:
            raise ValueError(f"{self.key} must be non-empty")
        existing = self._read()
        if record_id in existing:
            if existing[record_id] != row:
                raise ValueError(f"immutable record conflict for {self.key}={record_id}")
            return False
        self.path.parent.mkdir(parents=True, exist_ok=True)
        write_header = not self.path.exists()
        with self.path.open("a", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=self.columns)
            if write_header:
                writer.writeheader()
            writer.writerow(row)
        return True

    def append_many(self, records: Iterable[Mapping[str, object]]) -> int:
        return sum(int(self.append(record)) for record in records)


MARKET_COLUMNS = tuple(MarketSnapshot.__dataclass_fields__.keys())
STOCK_COLUMNS = tuple(StockSnapshot.__dataclass_fields__.keys())
DECISION_COLUMNS = tuple(DecisionLog.__dataclass_fields__.keys())
OUTCOME_COLUMNS = tuple(OutcomeLog.__dataclass_fields__.keys())


class HistoricalStore:
    def __init__(self, root: str | Path = "data/history"):
        root = Path(root)
        self.market = AppendOnlyCsvStore(root / "market_snapshots.csv", "snapshot_id", MARKET_COLUMNS)
        self.stock = AppendOnlyCsvStore(root / "stock_snapshots.csv", "snapshot_id", STOCK_COLUMNS)
        self.decisions = AppendOnlyCsvStore(root / "decisions.csv", "decision_id", DECISION_COLUMNS)
        self.outcomes = AppendOnlyCsvStore(root / "outcomes.csv", "outcome_id", OUTCOME_COLUMNS)

    def append_market(self, snapshot: MarketSnapshot) -> bool:
        return self.market.append(snapshot.to_record())

    def append_stock(self, snapshot: StockSnapshot) -> bool:
        return self.stock.append(snapshot.to_record())

    def append_decision(self, decision: DecisionLog) -> bool:
        return self.decisions.append(decision.to_record())

    def append_outcome(self, outcome: OutcomeLog) -> bool:
        return self.outcomes.append(outcome.to_record())
