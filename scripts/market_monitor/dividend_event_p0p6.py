#!/usr/bin/env python3
"""Dividend-event overlay for the existing Observation/P0-P6 research harness.

This module deliberately does not change the P0-P6 definitions. It adds a
point-in-time dividend-event layer and evaluates whether the event adds
incremental information after the market permission gates.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import median
from typing import Any

from p0_p6_backtest import signal_level

WINDOW_START = "2026-09-22"
EX_DATE = "2026-09-29"
WINDOW_END = "2026-09-28"
DEFAULT_TAX_RATE = 0.154
HORIZONS = (1, 5, 20, 60)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows = []
    with path.open(encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            if "date" not in row or "asset_id" not in row:
                raise ValueError(f"line {line_no}: date and asset_id are required")
            rows.append(row)
    return rows


def event_edge(
    price: float,
    gross_dividend: float,
    *,
    tax_rate: float = DEFAULT_TAX_RATE,
    expected_gap_pct: float = 0.0,
    costs_pct: float = 0.0,
) -> dict[str, float]:
    if price <= 0 or gross_dividend < 0:
        raise ValueError("price must be > 0 and dividend must be >= 0")
    net = gross_dividend * (1.0 - tax_rate)
    net_yield_pct = net / price * 100.0
    edge_pct = net_yield_pct - expected_gap_pct - costs_pct
    return {
        "gross_dividend": gross_dividend,
        "net_dividend": net,
        "gross_yield_pct": gross_dividend / price * 100.0,
        "net_yield_pct": net_yield_pct,
        "event_edge_pct": edge_pct,
    }


def eligible(row: dict[str, Any], *, asset_id: str = "SAMSUNG_ELECTRONICS") -> bool:
    return (
        str(row.get("asset_id")) == asset_id
        and WINDOW_START <= str(row.get("date")) <= WINDOW_END
    )


def build_event_rows(
    rows: list[dict[str, Any]],
    *,
    gross_dividend: float | None,
    tax_rate: float = DEFAULT_TAX_RATE,
    expected_gap_pct: float = 0.0,
    costs_pct: float = 0.0,
) -> list[dict[str, Any]]:
    if gross_dividend is None:
        raise ValueError("DATA_NOT_READY: point-in-time expected dividend is missing")

    out = []
    for row in rows:
        if not eligible(row):
            continue
        price = row.get("entry_open")
        if price is None:
            price = row.get("close")
        if price is None:
            continue

        p = event_edge(
            float(price),
            float(gross_dividend),
            tax_rate=tax_rate,
            expected_gap_pct=expected_gap_pct,
            costs_pct=costs_pct,
        )
        level = signal_level(row)
        event_level = 0
        if p["event_edge_pct"] > 0 and level >= 2:
            event_level = 2
        if p["event_edge_pct"] > 0 and level >= 3:
            event_level = 3

        enriched = dict(row)
        enriched["dividend_event"] = {
            "decision_date": row["date"],
            "record_date": "2026-09-30",
            "ex_date": EX_DATE,
            "gross_dividend_source": "input_vintage",
            "gross_dividend": p["gross_dividend"],
            "net_dividend": p["net_dividend"],
            "gross_yield_pct": p["gross_yield_pct"],
            "net_yield_pct": p["net_yield_pct"],
            "expected_gap_pct": expected_gap_pct,
            "costs_pct": costs_pct,
            "event_edge_pct": p["event_edge_pct"],
            "p0_p6_level": level,
            "event_permission_level": event_level,
        }
        out.append(enriched)
    return out


def forward_total_return(row: dict[str, Any], horizon: int) -> float | None:
    entry = row.get("entry_open")
    series = row.get("asset_rows")
    if entry is None or not isinstance(series, list) or len(series) < horizon:
        return None
    final_close = float(series[horizon - 1]["close"])
    return (final_close / float(entry) - 1.0) * 100.0


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {"n_entries": len(rows)}
    for h in HORIZONS:
        values = [v for r in rows if (v := forward_total_return(r, h)) is not None]
        out[f"{h}d"] = {
            "n": len(values),
            "mean_price_return_pct": sum(values) / len(values) if values else None,
            "median_price_return_pct": median(values) if values else None,
            "positive_rate": sum(v > 0 for v in values) / len(values) if values else None,
            "worst_price_return_pct": min(values) if values else None,
        }
    return out


def run(
    events_path: Path,
    *,
    gross_dividend: float | None,
    tax_rate: float = DEFAULT_TAX_RATE,
    expected_gap_pct: float = 0.0,
    costs_pct: float = 0.0,
) -> dict[str, Any]:
    try:
        rows = load_jsonl(events_path)
        event_rows = build_event_rows(
            rows,
            gross_dividend=gross_dividend,
            tax_rate=tax_rate,
            expected_gap_pct=expected_gap_pct,
            costs_pct=costs_pct,
        )
    except (ValueError, KeyError) as exc:
        return {"status": "DATA_NOT_READY", "reason": str(exc)}

    return {
        "status": "RESEARCH_OK",
        "window": {
            "start": WINDOW_START,
            "last_pre_ex_entry": WINDOW_END,
            "ex_date_control": EX_DATE,
        },
        "event_rows": event_rows,
        "summary": summarize(event_rows),
        "note": (
            "Price return is reported separately. A production study must add "
            "the realized dividend only after the ex-date and must preserve the "
            "point-in-time dividend vintage used at each decision timestamp."
        ),
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=Path)
    ap.add_argument("--gross-dividend", type=float, required=True)
    ap.add_argument("--tax-rate", type=float, default=DEFAULT_TAX_RATE)
    ap.add_argument("--expected-gap-pct", type=float, default=0.0)
    ap.add_argument("--costs-pct", type=float, default=0.0)
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()

    payload = json.dumps(
        run(
            args.input,
            gross_dividend=args.gross_dividend,
            tax_rate=args.tax_rate,
            expected_gap_pct=args.expected_gap_pct,
            costs_pct=args.costs_pct,
        ),
        ensure_ascii=False,
        indent=2,
    )
    if args.output:
        args.output.write_text(payload + "\n", encoding="utf-8")
    print(payload)
