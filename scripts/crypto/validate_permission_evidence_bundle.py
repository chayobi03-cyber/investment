#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

REQUIRED = {
    "asset", "series_id", "observation_timestamp", "available_at",
    "source_id", "unit", "value", "ingested_at", "provenance_hash",
}

def read(path: Path) -> pd.DataFrame:
    manifest_path = path.with_suffix(".manifest.json")
    if manifest_path.exists():
        import json
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        status = manifest.get("status")
        if status == "COLLECTED_WITH_GAPS":
            raise SystemExit(f"EVIDENCE_FAIL:source_manifest_has_gaps:{path}")
        if status not in {"COLLECTED_PROVISIONAL_PIT", "PASS"}:
            raise SystemExit(f"EVIDENCE_FAIL:invalid_source_manifest_status:{path}:{status}")
    df = pd.read_csv(path)
    missing = sorted(REQUIRED - set(df.columns))
    if missing:
        raise SystemExit(f"EVIDENCE_FAIL:missing_columns:{path}:{",".join(missing)}")
    for c in ("observation_timestamp", "available_at", "ingested_at"):
        df[c] = pd.to_datetime(df[c], utc=True, errors="coerce")
        if df[c].isna().any():
            raise SystemExit(f"EVIDENCE_FAIL:invalid_timestamp:{path}:{c}")
    if df["provenance_hash"].isna().any() or (df["provenance_hash"].astype(str).str.len() < 16).any():
        raise SystemExit(f"EVIDENCE_FAIL:provenance_missing:{path}")
    if (df["available_at"] < df["observation_timestamp"]).any():
        raise SystemExit(f"EVIDENCE_FAIL:availability_before_observation:{path}")
    return df

def validate(paths: list[Path], *, as_of: pd.Timestamp | None = None) -> dict:
    frames = [read(p) for p in paths]
    df = pd.concat(frames, ignore_index=True)
    if as_of is not None:
        as_of = pd.Timestamp(as_of)
        if as_of.tzinfo is None:
            as_of = as_of.tz_localize("UTC")
        else:
            as_of = as_of.tz_convert("UTC")
        if (df["available_at"] > as_of).any():
            raise SystemExit("EVIDENCE_FAIL:lookahead_available_at")
    key = ["asset", "series_id", "observation_timestamp", "source_id"]
    if df.duplicated(key).any():
        raise SystemExit("EVIDENCE_FAIL:duplicate_observation_key")
    return {
        "status": "PASS",
        "rows": int(len(df)),
        "assets": sorted(df["asset"].astype(str).unique().tolist()),
        "series": int(df["series_id"].nunique()),
        "sources": sorted(df["source_id"].astype(str).unique().tolist()),
        "start": df["observation_timestamp"].min().isoformat(),
        "end": df["observation_timestamp"].max().isoformat(),
    }

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="+", type=Path)
    ap.add_argument("--as-of", default=None)
    args = ap.parse_args()
    print(validate(args.paths, as_of=pd.Timestamp(args.as_of) if args.as_of else None))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
