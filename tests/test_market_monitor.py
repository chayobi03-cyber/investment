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

    def _raw(self, vix):
        cfg = MOD.load_config()
        ts = "2026-10-08T00:00:00Z"
        groups = {
            g: {name: {"ok": True, "change_pct": 0.1, "timestamp": ts} for name in syms}
            for g, syms in cfg["symbols"].items()
        }
        if vix is None:
            groups["indices"].pop("VIX")
        else:
            groups["indices"]["VIX"] = vix
        flat = {f"{g}.{n}": v for g, items in groups.items() for n, v in items.items()}
        return cfg, {"collected_at": ts, "groups": groups, "all": flat}

    def test_build_state_reads_vix_change(self):
        cfg, raw = self._raw({"ok": True, "change_pct": 2.5, "timestamp": "2026-10-08T00:00:00Z"})
        state = MOD.build_state(cfg, raw)
        self.assertEqual(state["metrics"]["VIX_pct"], 2.5)
        self.assertEqual(state["RISK"], "RED")

    def test_build_state_ignores_failed_or_missing_vix(self):
        for vix in ({"ok": False, "error": "timeout"}, None):
            cfg, raw = self._raw(vix)
            state = MOD.build_state(cfg, raw)
            self.assertIsNone(state["metrics"]["VIX_pct"])
            self.assertEqual(state["RISK"], "N/A")


if __name__ == "__main__":
    unittest.main()
