#!/usr/bin/env python3
"""Persist a structured live market-review result into Historical DB."""

from __future__ import annotations

import argparse
import json

from investment_pipeline.history.live_adapter import record_live_review_file


def main() -> int:
    parser = argparse.ArgumentParser(description="Record one live market review")
    parser.add_argument("--input", required=True, help="structured daily market-review JSON")
    parser.add_argument("--root", default="data/history", help="Historical DB root")
    parser.add_argument("--origin", default="live", help="record origin, default=live")
    args = parser.parse_args()
    manifest = record_live_review_file(args.input, root=args.root, origin=args.origin)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
