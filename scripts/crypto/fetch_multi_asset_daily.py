#!/usr/bin/env python3
from __future__ import annotations

import argparse
import time
from pathlib import Path

import pandas as pd
import requests

BASE_URL = "https://api.exchange.coinbase.com/products/{product}/candles"
MAX_CANDLES = 300
PRODUCTS = {"BTC": "BTC-USD", "ETH": "ETH-USD", "SOL": "SOL-USD"}


def fetch_asset(asset: str, days: int) -> pd.DataFrame:
    if asset not in PRODUCTS:
        raise ValueError(f"unsupported_asset:{asset}")
    if days < 200:
        raise ValueError("days_must_be_at_least_200")

    end = pd.Timestamp.now(tz="UTC").floor("D")
    start = end - pd.Timedelta(days=int(days) + 2)
    cursor = end
    rows: list[list[float]] = []

    while cursor > start:
        batch_start = max(start, cursor - pd.Timedelta(days=int(MAX_CANDLES)))
        response = requests.get(
            BASE_URL.format(product=PRODUCTS[asset]),
            params={"granularity": 86400, "start": batch_start.isoformat(), "end": cursor.isoformat()},
            headers={"User-Agent": "investment-research/crypto-cross-asset-v0.1"},
            timeout=30,
        )
        response.raise_for_status()
        batch = response.json()
        if not batch:
            break
        rows.extend(batch)
        cursor = batch_start - pd.Timedelta(seconds=1)
        time.sleep(0.10)

    frame = pd.DataFrame(
        rows,
        columns=["timestamp_s", "low", "high", "open", "close", "volume"],
    )
    frame["asset"] = asset
    frame["series_id"] = f"COINBASE:{PRODUCTS[asset]}:1d"
    frame["timestamp"] = pd.to_datetime(frame["timestamp_s"], unit="s", utc=True)
    frame["available_at"] = frame["timestamp"] + pd.Timedelta(days=1)

    for col in ["open", "high", "low", "close", "volume"]:
        frame[col] = pd.to_numeric(frame[col], errors="coerce")

    return (
        frame[
            ["asset","series_id","timestamp","available_at","open","high","low","close","volume"]
        ]
        .sort_values("timestamp")
        .drop_duplicates(["asset","series_id","timestamp"])
        .tail(days)
        .reset_index(drop=True)
    )


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=3000)
    ap.add_argument("--out", type=Path, default=Path("artifacts/crypto/cross_asset_1d.csv"))
    args = ap.parse_args()

    frames = [fetch_asset(asset, args.days) for asset in PRODUCTS]
    result = pd.concat(frames, ignore_index=True).sort_values(["asset","timestamp"])
    args.out.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(args.out, index=False)
    print(
        f"assets={sorted(result['asset'].unique().tolist())} "
        f"rows={len(result)} start={result['timestamp'].min()} end={result['timestamp'].max()}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
