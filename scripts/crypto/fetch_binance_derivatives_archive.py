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

def collect_symbol(symbol: str, start: date, end: date) -> list[dict]:
    days = []
    cursor = start
    while cursor <= end:
        days.append(cursor)
        cursor += timedelta(days=1)

    rows: list[dict] = []
    with ThreadPoolExecutor(max_workers=8) as ex:
        futures = {ex.submit(fetch_zip, daily_url(symbol, d)): d for d in days}
        for fut in as_completed(futures):
            d = futures[fut]
            try:
                payload, content_hash = fut.result()
            except requests.HTTPError as exc:
                if getattr(exc.response, "status_code", None) == 404:
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
            frame["available_at"] = frame["observation_timestamp"].dt.floor("D") + pd.Timedelta(days=1)
            frame["asset"] = symbol.replace("USDT", "")
            frame["source_id"] = "BINANCE_VISION_METRICS"
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
    return rows

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", required=True)
    ap.add_argument("--end", required=True)
    ap.add_argument("--out", type=Path, default=Path("artifacts/permission/binance_metrics_pit.csv"))
    args = ap.parse_args()

    start = date.fromisoformat(args.start)
    end = date.fromisoformat(args.end)
    all_rows: list[dict] = []
    for symbol in SYMBOLS:
        all_rows.extend(collect_symbol(symbol, start, end))

    out = pd.DataFrame(all_rows)
    if not out.empty:
        out = out.sort_values(["asset", "observation_timestamp"])
        out["series_id"] = "BINANCE:" + out["symbol"].astype(str) + ":METRICS"
        out["unit"] = "mixed"
        out["availability_method"] = "CONSERVATIVE_NEXT_UTC_DAY"
    args.out.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(args.out, index=False)
    print(
        f"status=COLLECTED_PROVISIONAL_PIT rows={len(out)} "
        f"assets={sorted(out['asset'].unique().tolist()) if not out.empty else []}"
    )
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
