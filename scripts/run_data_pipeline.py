import argparse
from pathlib import Path

from investment_pipeline.pipeline import build_factor_dataset


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-dir", default="data/raw")
    parser.add_argument("--out-dir", default="data/processed")
    args = parser.parse_args()
    result = build_factor_dataset(Path(args.raw_dir), Path(args.out_dir))
    print({k: (v.__dict__ if hasattr(v, "__dict__") else v) for k, v in result.items()})
