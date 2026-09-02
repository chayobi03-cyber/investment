#!/usr/bin/env python3
"""Run the phase-A event-window Stress Convergence threshold backtest.

This deliberately operates on a frozen event fixture. It is not a substitute for
an all-days historical time-series backtest; its purpose is to make the first
calibration pass reproducible and auditable.
"""

from __future__ import annotations

import json
from pathlib import Path
from statistics import mean, median


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures" / "stress_threshold_backtest_v01.json"


def main() -> int:
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    episodes = payload["episodes"]

    target = [e for e in episodes if e["class"] in {"target_stress", "target_stress_control"}]
    controls = [e for e in episodes if e["class"] == "false_positive_control"]

    detected = sum(e["result"] == "TP" for e in target)
    fp = sum(e["result"] == "FP" for e in controls)
    fn = sum(e["result"] == "FN" for e in target)
    leads = [e["lead_days"] for e in target if isinstance(e["lead_days"], int)]

    metrics = {
        "target_events": len(target),
        "detected": detected,
        "recall": detected / len(target) if target else None,
        "false_positive_controls": len(controls),
        "false_positives": fp,
        "selected_control_fpr": fp / len(controls) if controls else None,
        "false_negatives": fn,
        "mean_lead_days": mean(leads) if leads else None,
        "median_lead_days": median(leads) if leads else None,
    }

    print(json.dumps(metrics, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
