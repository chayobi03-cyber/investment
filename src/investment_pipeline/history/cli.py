from __future__ import annotations

import argparse

from .ingest import ingest_decisions_json, ingest_market_csv, ingest_stock_csv
from .outcomes import evaluate_decisions
from .store import HistoricalStore


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Historical Investment DB V1 CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    market = sub.add_parser("market", help="append market snapshots from CSV")
    market.add_argument("--input", required=True)
    market.add_argument("--model-version", required=True)
    market.add_argument("--data-version", required=True)
    market.add_argument("--origin", default="live")
    market.add_argument("--root", default="data/history")

    stock = sub.add_parser("stock", help="append stock snapshots from CSV")
    stock.add_argument("--input", required=True)
    stock.add_argument("--model-version", required=True)
    stock.add_argument("--data-version", required=True)
    stock.add_argument("--origin", default="live")
    stock.add_argument("--root", default="data/history")

    decisions = sub.add_parser("decisions", help="append decisions from JSON")
    decisions.add_argument("--input", required=True)
    decisions.add_argument("--root", default="data/history")

    outcomes = sub.add_parser("outcomes", help="evaluate decisions against future prices")
    outcomes.add_argument("--decisions", required=True)
    outcomes.add_argument("--prices", required=True)
    outcomes.add_argument("--root", default="data/history")
    outcomes.add_argument("--model-version", default="outcome-v1")
    outcomes.add_argument("--benchmark-column")

    return parser


def main() -> int:
    args = build_parser().parse_args()
    store = HistoricalStore(args.root)
    if args.command == "market":
        count = ingest_market_csv(args.input, store, model_version=args.model_version, data_version=args.data_version, record_origin=args.origin)
    elif args.command == "stock":
        count = ingest_stock_csv(args.input, store, model_version=args.model_version, data_version=args.data_version, record_origin=args.origin)
    elif args.command == "decisions":
        count = ingest_decisions_json(args.input, store)
    else:
        count = evaluate_decisions(args.decisions, args.prices, store, model_version=args.model_version, benchmark_column=args.benchmark_column)
    print(f"records_written={count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
