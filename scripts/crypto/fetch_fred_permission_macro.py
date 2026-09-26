#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import io
from pathlib import Path

import pandas as pd
import requests

FRED_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv"
SERIES = {
    "DGS10": "US10Y",
    "DFII10": "US_REAL_YIELD_10Y",
    "DCOILWTICO": "WTI",
    "DEXKOUS": "USD_KRW",
    "DTWEXBGS": "BROAD_USD_INDEX",
}

def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()

def fetch_series(series_id: str, start: str, end: str) -> tuple[pd.DataFrame, str]:
    r = requests.get(
        FRED_URL,
        params={"id": series_id, "cosd": start, "coed": end},
        headers={"User-Agent": "investment-research/permission-evidence-v0.1"},
        timeout=30,
    )
    r.raise_for_status()
    raw = r.content
    frame = pd.read_csv(io.BytesIO(raw))
    date_col = "observation_date"
    if date_col not in frame.columns:
        raise ValueError(f"FRED_DATE_COLUMN_MISSING:{series_id}")
    value_col = series_id
    if value_col not in frame.columns:
        raise ValueError(f"FRED_VALUE_COLUMN_MISSING:{series_id}")
    frame["observation_timestamp"] = pd.to_datetime(
        frame[date_col], utc=True, errors="coerce"
    )
    frame["value"] = pd.to_numeric(frame[value_col], errors="coerce")
    frame = frame.dropna(subset=["observation_timestamp", "value"]).copy()
    return frame[["observation_timestamp", "value"]], sha256_bytes(raw)

def build_evidence(series_id: str, frame: pd.DataFrame, content_hash: str) -> pd.DataFrame:
    out = frame.copy()
    # Conservative PIT model: treat the observation as available no earlier
    # than the following UTC day. This avoids lookahead but is intentionally
    # not used as a same-day release-time claim.
    out["available_at"] = out["observation_timestamp"] + pd.Timedelta(days=1)
    out["asset"] = "MULTI_ASSET"
    out["series_id"] = f"FRED:{series_id}"
    out["source_id"] = f"FRED:{series_id}"
    out["unit"] = "raw"
    out["ingested_at"] = pd.Timestamp.now(tz="UTC")
    out["provenance_hash"] = content_hash
    out["availability_method"] = "CONSERVATIVE_NEXT_UTC_DAY"
    return out[
        [
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
        ]
    ]

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", default="2010-01-01")
    ap.add_argument("--end", default=None)
    ap.add_argument("--out", type=Path, default=Path("artifacts/permission/fred_macro_pit.csv"))
    args = ap.parse_args()
    end = args.end or pd.Timestamp.now(tz="UTC").strftime("%Y-%m-%d")

    frames = []
    manifest = []
    for fred_id, logical_id in SERIES.items():
        data, content_hash = fetch_series(fred_id, args.start, end)
        data["logical_id"] = logical_id
        frames.append(build_evidence(fred_id, data, content_hash))
        manifest.append(
            {
                "source_id": f"FRED:{fred_id}",
                "series_id": f"FRED:{fred_id}",
                "logical_id": logical_id,
                "rows": int(len(data)),
                "content_hash": content_hash,
                "availability_method": "CONSERVATIVE_NEXT_UTC_DAY",
            }
        )

    result = pd.concat(frames, ignore_index=True).sort_values(
        ["series_id", "observation_timestamp"]
    )
    args.out.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.out, index=False)
    manifest_path = args.out.with_suffix(".manifest.json")
    import json
    manifest_path.write_text(
        json.dumps(
            {
                "status": "COLLECTED_PROVISIONAL_PIT",
                "start": args.start,
                "end": end,
                "series": manifest,
                "dxy_status": "NOT_COLLECTED_EXACT_DXY_ONLY",
                "note": "DTWEXBGS is broad USD index diagnostic, not a DXY substitute.",
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(
        f"status=COLLECTED_PROVISIONAL_PIT rows={len(result)} "
        f"series={result['series_id'].nunique()}"
    )
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
