#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = {
    "asset", "series_id", "observation_timestamp", "available_at",
    "source_id", "unit", "value", "ingested_at"
}


def validate(frame: pd.DataFrame, *, as_of: pd.Timestamp | None = None) -> dict:
    missing = sorted(REQUIRED_COLUMNS - set(frame.columns))
    if missing:
        raise SystemExit("P0_PERMISSION_FAIL:missing_columns:" + ",".join(missing))

    frame = frame.copy()
    for col in ["observation_timestamp", "available_at", "ingested_at"]:
        frame[col] = pd.to_datetime(frame[col], utc=True, errors="coerce")
        if frame[col].isna().any():
            raise SystemExit(f"P0_PERMISSION_FAIL:invalid_timestamp:{col}")

    if frame.duplicated(["asset", "series_id", "observation_timestamp", "source_id"]).any():
        raise SystemExit("P0_PERMISSION_FAIL:duplicate_observation_key")

    if (frame["available_at"] < frame["observation_timestamp"]).any():
        raise SystemExit("P0_PERMISSION_FAIL:available_before_observed")

    if as_of is not None:
        as_of = pd.Timestamp(as_of)
        if as_of.tzinfo is None:
            as_of = as_of.tz_localize("UTC")
        else:
            as_of = as_of.tz_convert("UTC")
        if frame["available_at"].gt(as_of).any():
            raise SystemExit("P0_PERMISSION_FAIL:future_available_at")

    value_num = pd.to_numeric(frame["value"], errors="coerce")
    bad_numeric = value_num.isna() & frame["value"].notna()
    if bad_numeric.any():
        raise SystemExit("P0_PERMISSION_FAIL:non_numeric_value")

    frame = frame.sort_values(["asset", "series_id", "observation_timestamp", "source_id"])
    coverage = (
        frame.groupby(["asset", "series_id"], dropna=False)["observation_timestamp"]
        .agg(["min", "max", "count"])
        .reset_index()
    )

    return {
        "status": "PASS",
        "rows": int(len(frame)),
        "series_count": int(coverage.shape[0]),
        "assets": sorted(frame["asset"].astype(str).unique().tolist()),
        "coverage": coverage.to_dict(orient="records"),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=Path)
    ap.add_argument("--as-of", default=None, help="Optional deterministic PIT cutoff timestamp.")
    args = ap.parse_args()
    frame = pd.read_csv(args.input)
    as_of = pd.Timestamp(args.as_of) if args.as_of else None
    print(validate(frame, as_of=as_of))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
