"""Run Experiment A (score monotonicity + walk-forward stability) against
the processed factor panel produced by run_data_pipeline.py.

See docs/investment/WALKFORWARD_VALIDATION_METHODOLOGY_V1.md.

Usage:
    PYTHONPATH=src python scripts/run_walkforward_validation.py \
        --processed-dir data/processed \
        --score-col return_20d_score \
        --price-col close \
        --out data/processed/walkforward_report.json

This does not publish a ranking. It only reports whether the named score
column had a consistent, non-look-ahead relationship with realized forward
returns in the frozen historical panel. Per the data pipeline's production
gate, do not treat a passing report as authorization to connect a score to
BuyStrength/Action without also completing the remaining Level 6-10
validation steps (parameter sensitivity, transaction costs, cross-market
validation, multiple-testing correction, shadow operation).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from investment_pipeline.walkforward import run_experiment_a


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--processed-dir", default="data/processed")
    parser.add_argument("--score-col", required=True, help="Normalized (0-100) point-in-time score column, e.g. return_20d_score")
    parser.add_argument("--price-col", default="close")
    parser.add_argument("--as-of-col", default="as_of")
    parser.add_argument("--ticker-col", default="ticker")
    parser.add_argument("--horizons", default="5,20,60,120")
    parser.add_argument("--n-buckets", type=int, default=5)
    parser.add_argument("--min-bucket-history", type=int, default=30)
    parser.add_argument("--n-folds", type=int, default=4)
    parser.add_argument("--min-train-periods", type=int, default=60)
    parser.add_argument("--out", default=None, help="Output JSON path; defaults to <processed-dir>/walkforward_report.json")
    args = parser.parse_args()

    processed_dir = Path(args.processed_dir)
    panel_path = processed_dir / "normalized_factors.csv"
    if not panel_path.exists():
        raise FileNotFoundError(
            f"{panel_path} not found. Run scripts/run_data_pipeline.py first; "
            "this validation harness must not run against fabricated or hand-entered data."
        )
    panel = pd.read_csv(panel_path)
    if args.score_col not in panel.columns:
        raise KeyError(f"{args.score_col} not found in {panel_path}. Available columns: {list(panel.columns)}")

    horizons = tuple(int(h) for h in args.horizons.split(","))
    report = run_experiment_a(
        panel,
        score_col=args.score_col,
        price_col=args.price_col,
        as_of_col=args.as_of_col,
        ticker_col=args.ticker_col,
        horizons=horizons,
        n_buckets=args.n_buckets,
        min_bucket_history=args.min_bucket_history,
        n_folds=args.n_folds,
        min_train_periods=args.min_train_periods,
    )

    out_path = Path(args.out) if args.out else processed_dir / "walkforward_report.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False, default=str), encoding="utf-8")

    for horizon, result in report["horizons"].items():
        print(f"{args.score_col} @ {horizon}: falsification_status={result['falsification_status']} "
              f"monotonic={result['monotonic_full_sample']} full_sample_rank_ic={result['full_sample_rank_ic']}")
    print(f"Full report written to {out_path}")


if __name__ == "__main__":
    main()
