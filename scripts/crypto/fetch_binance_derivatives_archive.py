#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import io
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import requests

BASE = "https://data.binance.vision/data/futures/um"
SYMBOLS = ("BTCUSDT", "ETHUSDT", "SOLUSDT")
# Must match the PRIMARY derivatives source in config/permission_evidence_registry_v0.1.json.
SOURCE_ID = "BINANCE_VISION_DERIVATIVES_ARCHIVE"
METRICS_COLUMNS = [
    "create_time",
    "symbol",
    "sum_open_interest",
    "sum_open_interest_value",
    "count_toptrader_long_short_ratio",
    "sum_toptrader_long_short_ratio",
    "count_long_short_ratio",
    "sum_taker_long_short_vol_ratio",
]
# Evidence rows are long-format (one value per series per observation), the
# contract enforced by validate_permission_evidence_bundle.REQUIRED.
METRIC_UNITS = {
    "sum_open_interest": "base_asset",
    "sum_open_interest_value": "USDT",
    "sum_toptrader_long_short_ratio": "ratio",
    "sum_taker_long_short_vol_ratio": "ratio",
}
EVIDENCE_COLUMNS = [
    "asset",
    "series_id",
    "observation_timestamp",
    "available_at",
    "source_id",
    "unit",
    "value",
    "ingested_at",
    "provenance_hash",
    "availability_method",
    "symbol",
]

def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()

def fetch_zip(url: str) -> tuple[bytes, str]:
    r = requests.get(
        url,
        headers={"User-Agent": "investment-research/permission-evidence-v0.1"},
        timeout=60,
    )
    r.raise_for_status()
    return r.content, sha256_bytes(r.content)

def unzip_first_csv(payload: bytes) -> pd.DataFrame:
    with zipfile.ZipFile(io.BytesIO(payload)) as zf:
        names = [n for n in zf.namelist() if n.lower().endswith(".csv")]
        if not names:
            raise ValueError("BINANCE_ARCHIVE_CSV_MISSING")
        with zf.open(names[0]) as fh:
            sample = fh.read(4096)
            fh.seek(0)
            has_header = b"create_time" in sample
            return pd.read_csv(
                fh,
                header=0 if has_header else None,
                names=None if has_header else METRICS_COLUMNS,
            )

def daily_url(symbol: str, d: date) -> str:
    stamp = d.isoformat()
    return f"{BASE}/daily/metrics/{symbol}/{symbol}-metrics-{stamp}.zip"

def collect_symbol(symbol: str, start: date, end: date) -> tuple[list[dict], list[str]]:
    days = []
    cursor = start
    while cursor <= end:
        days.append(cursor)
        cursor += timedelta(days=1)

    rows: list[dict] = []
    missing_days: list[str] = []
    with ThreadPoolExecutor(max_workers=8) as ex:
        futures = {ex.submit(fetch_zip, daily_url(symbol, d)): d for d in days}
        for fut in as_completed(futures):
            d = futures[fut]
            try:
                payload, content_hash = fut.result()
            except requests.HTTPError as exc:
                if getattr(exc.response, "status_code", None) == 404:
                    missing_days.append(d.isoformat())
                    continue
                raise
            frame = unzip_first_csv(payload)
            if frame.empty:
                continue

            # Binance's create_time is UTC snapshot time. Archive files are
            # published on a delayed basis; use next UTC day as conservative PIT.
            frame["observation_timestamp"] = pd.to_datetime(
                frame["create_time"], utc=True, errors="coerce"
            )
            frame = frame.dropna(subset=["observation_timestamp"]).copy()
            frame["available_at"] = frame["observation_timestamp"].dt.floor("D") + timedelta(days=1)
            frame["asset"] = symbol.replace("USDT", "")
            frame["source_id"] = SOURCE_ID
            frame["provenance_hash"] = content_hash
            frame["ingested_at"] = pd.Timestamp.now(tz="UTC")
            keep = [
                "asset",
                "symbol",
                "observation_timestamp",
                "available_at",
                "sum_open_interest",
                "sum_open_interest_value",
                "sum_toptrader_long_short_ratio",
                "sum_taker_long_short_vol_ratio",
                "source_id",
                "provenance_hash",
                "ingested_at",
            ]
            available = [c for c in keep if c in frame.columns]
            rows.extend(frame[available].to_dict("records"))
    return rows, missing_days

def to_long_evidence(wide: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """One row per (asset, metric, observation) with series_id, unit and value.

    Missing metric values are dropped, never zero-filled; the count is returned
    so the manifest can report it.
    """
    if wide.empty:
        return pd.DataFrame(columns=EVIDENCE_COLUMNS), 0
    metrics = [m for m in METRIC_UNITS if m in wide.columns]
    ids = [c for c in wide.columns if c not in METRIC_UNITS]
    long = wide.melt(id_vars=ids, value_vars=metrics, var_name="metric", value_name="value")
    long["value"] = pd.to_numeric(long["value"], errors="coerce")
    null_values = int(long["value"].isna().sum())
    long = long.dropna(subset=["value"]).copy()
    long["series_id"] = "BINANCE:" + long["symbol"].astype(str) + ":" + long["metric"]
    long["unit"] = long["metric"].map(METRIC_UNITS)
    long["availability_method"] = "CONSERVATIVE_NEXT_UTC_DAY"
    long = long.sort_values(["asset", "series_id", "observation_timestamp"])
    return long[EVIDENCE_COLUMNS].reset_index(drop=True), null_values


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", required=True)
    ap.add_argument("--end", required=True)
    ap.add_argument("--out", type=Path, default=Path("artifacts/permission/binance_metrics_pit.csv"))
    args = ap.parse_args()

    start = date.fromisoformat(args.start)
    end = date.fromisoformat(args.end)
    all_rows: list[dict] = []
    missing_by_symbol: dict[str, list[str]] = {}
    for symbol in SYMBOLS:
        rows, missing_days = collect_symbol(symbol, start, end)
        all_rows.extend(rows)
        missing_by_symbol[symbol] = sorted(missing_days)

    out, null_values = to_long_evidence(pd.DataFrame(all_rows))
    args.out.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(args.out, index=False)
    import json
    manifest = {
        "status": "COLLECTED_PROVISIONAL_PIT" if not any(missing_by_symbol.values()) else "COLLECTED_WITH_GAPS",
        "missing_days": missing_by_symbol,
        "source": SOURCE_ID,
        "null_metric_values_dropped": null_values,
        "known_quality_warnings": [
            "Binance Public Data reports historical metrics gaps and timestamp-label changes; do not silently treat gaps as zero or forward-fill.",
        ],
    }
    args.out.with_suffix(".manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )
    print(
        f"status={manifest['status']} rows={len(out)} "
        f"assets={sorted(out['asset'].unique().tolist()) if not out.empty else []}"
    )
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
