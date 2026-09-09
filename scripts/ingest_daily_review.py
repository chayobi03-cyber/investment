#!/usr/bin/env python3
"""CLI entry point for persisting one daily market-review bundle."""

from __future__ import annotations

import argparse

from investment_pipeline.history.daily import ingest_daily_bundle


def main() -> int:
    p = argparse.ArgumentParser(description="Persist a daily investment review bundle")
    p.add_argument("--market", required=True, help="market snapshot CSV")
    p.add_argument("--stock", required=True, help="stock snapshot CSV")
    p.add_argument("--decisions", help="decision log JSON")
    p.add_argument("--root", default="data/history")
    p.add_argument("--model-version", required=True)
    p.add_argument("--data-version", required=True)
    p.add_argument("--origin", default="live")
    args = p.parse_args()
    manifest = ingest_daily_bundle(
        market_csv=args.market,
        stock_csv=args.stock,
        decisions_json=args.decisions,
        root=args.root,
        model_version=args.model_version,
        data_version=args.data_version,
        record_origin=args.origin,
    )
    print(manifest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
