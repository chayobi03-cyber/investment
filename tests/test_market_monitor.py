import json
import tempfile
import unittest
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "market_monitor",
    ROOT / "scripts" / "market_monitor" / "poll.py",
)
MOD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)


class MarketMonitorTests(unittest.TestCase):
    def test_status(self):
        self.assertEqual(MOD.status_from_change(0.2, 1.0), "GREEN")
        self.assertEqual(MOD.status_from_change(0.6, 1.0), "AMBER")
        self.assertEqual(MOD.status_from_change(1.2, 1.0), "RED")

    def test_session_bucket_is_valid(self):
        self.assertIn(MOD.session_bucket(), {"KOREA", "US", "OVERLAP", "GLOBAL_TRANSITION"})

    def test_delta_detects_state_change(self):
        prev = {"RISK": "GREEN", "TREND": "GREEN"}
        cur = {
            "RISK": "RED",
            "TREND": "GREEN",
            "BREADTH": "GREEN",
            "LEADERS": "GREEN",
            "RATES": "GREEN",
            "FX": "GREEN",
            "OIL": "GREEN",
            "GOLD": "GREEN",
            "BUY_TRIGGER": "UNCONFIRMED",
            "DATA_QUALITY": "GREEN",
        }
        self.assertIn("RISK:GREEN->RED", MOD.delta(prev, cur))

    def test_no_alert_for_unchanged_state(self):
        cur = {
            "RISK": "GREEN", "TREND": "GREEN", "BREADTH": "GREEN",
            "LEADERS": "GREEN", "RATES": "GREEN", "FX": "GREEN",
            "OIL": "GREEN", "GOLD": "GREEN", "BUY_TRIGGER": "UNCONFIRMED",
            "DATA_QUALITY": "GREEN", "metrics": {}
        }
        self.assertEqual(MOD.should_alert(cur, cur, []), ("P2", False))


if __name__ == "__main__":
    unittest.main()
