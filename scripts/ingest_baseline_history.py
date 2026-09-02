"""M1-B baseline historical-data ingestion and evidence generator.

The promotion gate is intentionally fail-closed: secondary data can be fetched
for reconciliation, but M1-B cannot become GREEN unless primary-source OHLCV
exports are present and both source layers pass the required integrity checks.
No source observation is silently deleted or repaired.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.data_qa.validation import (
    find_duplicate_timestamps,
    find_missing_timestamps,
    find_point_in_time_violations,
    validate_ohlc,
)

MATRIX_PATH = ROOT / "docs/data/BASELINE_PROVENANCE_MATRIX.json"
ARTIFACT_DIR = ROOT / "artifacts/baseline_history"
PRIMARY_DIR = Path(os.getenv("INVESTMENT_PRIMARY_DATA_DIR", ROOT / "data/raw/primary"))
SECONDARY_DIR = Path(os.getenv("INVESTMENT_SECONDARY_DATA_DIR", ROOT / "data/raw/secondary"))


@dataclass(frozen=True)
class Observation:
    symbol: str
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    source: str
    retrieval_timestamp: str
    decision_timestamp: str


def now_utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fetch_json(url: str) -> dict:
    request = Request(url, headers={"User-Agent": "investment-m1b-ingest/1.0"})
    with urlopen(request, timeout=30) as response:  # noqa: S310 - fixed public secondary source
        return json.loads(response.read().decode("utf-8"))


def load_matrix() -> dict:
    return json.loads(MATRIX_PATH.read_text(encoding="utf-8"))


def load_csv(path: Path, symbol: str, source: str, retrieval_timestamp: str, decision_timestamp: str) -> list[Observation]:
    rows: list[Observation] = []
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        required = {"date", "open", "high", "low", "close", "volume"}
        missing = required - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"{path}: missing required columns: {sorted(missing)}")
        for raw in reader:
            timestamp = str(raw["date"]).strip()
            rows.append(
                Observation(
                    symbol=symbol,
                    timestamp=timestamp,
                    open=float(raw["open"]),
                    high=float(raw["high"]),
                    low=float(raw["low"]),
                    close=float(raw["close"]),
                    volume=float(raw["volume"]),
                    source=source,
                    retrieval_timestamp=retrieval_timestamp,
                    decision_timestamp=decision_timestamp,
                )
            )
    return rows


def fetch_yahoo_secondary(symbol: str, start: str, retrieval_timestamp: str) -> list[Observation]:
    start_epoch = int(datetime.fromisoformat(start).replace(tzinfo=timezone.utc).timestamp())
    end_epoch = int(datetime.now(timezone.utc).timestamp())
    query = urlencode(
        {
            "period1": start_epoch,
            "period2": end_epoch,
            "interval": "1d",
            "events": "div,splits",
            "includeAdjustedClose": "true",
        }
    )
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?{query}"
    payload = fetch_json(url)
    result = payload["chart"]["result"][0]
    timestamps = result.get("timestamp", [])
    quote = result["indicators"]["quote"][0]
    rows: list[Observation] = []
    for idx, epoch in enumerate(timestamps):
        values = {key: quote[key][idx] for key in ("open", "high", "low", "close", "volume")}
        if any(value is None for value in values.values()):
            continue
        timestamp = datetime.fromtimestamp(epoch, tz=timezone.utc).date().isoformat()
        rows.append(
            Observation(
                symbol=symbol,
                timestamp=timestamp,
                open=float(values["open"]),
                high=float(values["high"]),
                low=float(values["low"]),
                close=float(values["close"]),
                volume=float(values["volume"]),
                source="Yahoo Finance",
                retrieval_timestamp=retrieval_timestamp,
                decision_timestamp=timestamp,
            )
        )
    return rows


def issues_for(rows: list[Observation]) -> list[dict]:
    payload = [asdict(row) for row in rows]
    issues: list[dict] = []
    issues.extend(asdict(issue) for issue in validate_ohlc(payload))
    issues.extend(asdict(issue) for issue in find_duplicate_timestamps(payload))
    issues.extend(asdict(issue) for issue in find_point_in_time_violations(payload))
    if rows:
        expected = {rows[0].symbol: [row.timestamp for row in rows]}
        issues.extend(asdict(issue) for issue in find_missing_timestamps(payload, expected))
    return issues


def main() -> int:
    matrix = load_matrix()
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    retrieval_timestamp = now_utc()
    decision_timestamp = retrieval_timestamp
    series_results: list[dict] = []
    all_gate_issues: list[dict] = []

    for spec in matrix["series"]:
        symbol = spec["series_id"]
        start = spec["inception_or_start"]
        primary_path = PRIMARY_DIR / f"{symbol}.csv"
        secondary_path = SECONDARY_DIR / f"{symbol}.csv"
        result = {
            "series_id": symbol,
            "primary_source": spec["primary_source"],
            "secondary_source": spec["secondary_source"],
            "primary_raw_path": str(primary_path.relative_to(ROOT)),
            "secondary_raw_path": str(secondary_path.relative_to(ROOT)),
            "retrieval_timestamp": retrieval_timestamp,
            "status": "BLOCKING",
        }

        primary_rows: list[Observation] = []
        secondary_rows: list[Observation] = []

        if primary_path.exists():
            primary_rows = load_csv(primary_path, symbol, spec["primary_source"]["provider"], retrieval_timestamp, decision_timestamp)
            result["primary_sha256"] = sha256_file(primary_path)
            result["primary_rows"] = len(primary_rows)
            result["primary_issues"] = issues_for(primary_rows)
            all_gate_issues.extend(result["primary_issues"])
        else:
            result["primary_issues"] = [
                {
                    "code": "PRIMARY_RAW_MISSING",
                    "symbol": symbol,
                    "timestamp": retrieval_timestamp,
                    "message": "official-issuer OHLCV export is required before M1-B promotion",
                    "severity": "ERROR",
                }
            ]
            all_gate_issues.extend(result["primary_issues"])

        if secondary_path.exists():
            secondary_rows = load_csv(secondary_path, symbol, spec["secondary_source"]["provider"], retrieval_timestamp, decision_timestamp)
            result["secondary_sha256"] = sha256_file(secondary_path)
            result["secondary_rows"] = len(secondary_rows)
        else:
            try:
                secondary_rows = fetch_yahoo_secondary(symbol, start, retrieval_timestamp)
                raw_path = SECONDARY_DIR / f"{symbol}.csv"
                raw_path.parent.mkdir(parents=True, exist_ok=True)
                with raw_path.open("w", newline="", encoding="utf-8") as handle:
                    writer = csv.writer(handle)
                    writer.writerow(["date", "open", "high", "low", "close", "volume"])
                    writer.writerows([[r.timestamp, r.open, r.high, r.low, r.close, r.volume] for r in secondary_rows])
                result["secondary_sha256"] = sha256_file(raw_path)
                result["secondary_rows"] = len(secondary_rows)
            except Exception as exc:  # noqa: BLE001 - evidence records failure deterministically
                result["secondary_fetch_error"] = f"{type(exc).__name__}: {exc}"
                all_gate_issues.append(
                    {
                        "code": "SECONDARY_FETCH_FAILED",
                        "symbol": symbol,
                        "timestamp": retrieval_timestamp,
                        "message": result["secondary_fetch_error"],
                        "severity": "ERROR",
                    }
                )

        if primary_rows and secondary_rows:
            primary_dates = {row.timestamp for row in primary_rows}
            secondary_dates = {row.timestamp for row in secondary_rows}
            result["cross_source"] = {
                "primary_date_count": len(primary_dates),
                "secondary_date_count": len(secondary_dates),
                "intersection_count": len(primary_dates & secondary_dates),
                "date_coverage_gap_primary_minus_secondary": len(primary_dates - secondary_dates),
                "date_coverage_gap_secondary_minus_primary": len(secondary_dates - primary_dates),
            }
        else:
            result["cross_source"] = {"status": "NOT_RUN"}

        result["status"] = (
            "GREEN"
            if not result["primary_issues"] and not result.get("secondary_fetch_error")
            else "BLOCKING"
        )
        series_results.append(result)

    gate_green = bool(series_results) and not all_gate_issues and all(
        item["status"] == "GREEN" for item in series_results
    )

    evidence = {
        "schema_version": "1.0",
        "created_at": retrieval_timestamp,
        "status": "GREEN" if gate_green else "BLOCKING",
        "promotion_decision": "M1-B GREEN" if gate_green else "M1-B BLOCKED",
        "reason": None if gate_green else "Primary-source OHLCV evidence is missing or one or more integrity checks failed.",
        "primary_data_directory": str(PRIMARY_DIR.relative_to(ROOT)),
        "secondary_data_directory": str(SECONDARY_DIR.relative_to(ROOT)),
        "series": series_results,
        "gate_issues": all_gate_issues,
        "provenance_matrix_sha256": hashlib.sha256(MATRIX_PATH.read_bytes()).hexdigest(),
        "machine_check": {
            "all_five_series_present": len(series_results) == 5,
            "all_primary_raw_present": all((PRIMARY_DIR / f"{item['series_id']}.csv").exists() for item in series_results),
            "all_secondary_raw_present": all((SECONDARY_DIR / f"{item['series_id']}.csv").exists() for item in series_results),
            "gate_pass": gate_green,
        },
    }

    evidence_path = ARTIFACT_DIR / "m1b_evidence.json"
    evidence_path.write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
    (ARTIFACT_DIR / "m1b_summary.txt").write_text(
        f"status={evidence['status']}\n"
        f"promotion_decision={evidence['promotion_decision']}\n"
        f"primary_raw_present={evidence['machine_check']['all_primary_raw_present']}\n"
        f"secondary_raw_present={evidence['machine_check']['all_secondary_raw_present']}\n"
        f"gate_pass={evidence['machine_check']['gate_pass']}\n",
        encoding="utf-8",
    )

    print(json.dumps(evidence["machine_check"], ensure_ascii=False, sort_keys=True))
    return 0 if gate_green else 1


if __name__ == "__main__":
    raise SystemExit(main())
