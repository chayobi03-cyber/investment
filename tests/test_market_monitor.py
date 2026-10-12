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

    def test_should_alert_priorities_are_pinned(self):
        base = {
            "RISK": "GREEN", "TREND": "GREEN", "BREADTH": "GREEN", "LEADERS": "GREEN",
            "RATES": "GREEN", "FX": "GREEN", "OIL": "GREEN", "GOLD": "GREEN",
            "BUY_TRIGGER": "UNCONFIRMED", "DATA_QUALITY": "GREEN", "metrics": {"VIX_pct": 1.0},
        }
        cases = [
            (None, {}, ("P2", False)),
            (base, {"DATA_QUALITY": "RED"}, ("P1", True)),
            (base, {"RISK": "RED"}, ("P0", True)),
            (base, {"RISK": "RED", "metrics": {"VIX_pct": None}}, ("P2", False)),
            (base, {"BREADTH": "AMBER", "LEADERS": "AMBER"}, ("P1", True)),
            (base, {"BREADTH": "AMBER"}, ("P2", False)),
            (base, {"GOLD": "RED", "TREND": "AMBER"}, ("P2", False)),
        ]
        for prev, change, expected in cases:
            cur = {**base, **change}
            self.assertEqual(MOD.should_alert(prev, cur, MOD.delta(prev, cur)), expected, change)

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
        # A failed quote may still carry a stale change_pct; it must not be used.
        for vix in ({"ok": False, "change_pct": 5.0, "error": "stale"}, None):
            cfg, raw = self._raw(vix)
            state = MOD.build_state(cfg, raw)
            self.assertIsNone(state["metrics"]["VIX_pct"])
            self.assertEqual(state["RISK"], "N/A")

    def _breadth_raw(self, up, total, cfg=None):
        cfg = cfg or MOD.load_config()
        _, raw = self._raw({"ok": True, "change_pct": 0.1, "timestamp": "2026-10-08T00:00:00Z"})
        # `total` ok leaders, `up` of them rising; one failed quote that must be ignored.
        leaders = {f"L{i}": {"ok": True, "change_pct": 1.0 if i < up else -1.0} for i in range(total)}
        leaders["DOWN"] = {"ok": False, "error": "x"}
        raw["groups"]["korea_leaders"] = leaders
        raw["groups"]["us_leaders"] = {}
        return cfg, raw

    def test_breadth_and_leaders_are_pinned(self):
        cases = [
            ((0, 0), None, "N/A"),
            ((0, 10), 0.0, "RED"),
            ((29, 100), 0.29, "RED"),
            ((3, 10), 0.30, "AMBER"),
            ((5, 10), 0.5, "AMBER"),
            ((6999, 10000), 0.6999, "AMBER"),
            ((7, 10), 0.70, "GREEN"),
            ((10, 10), 1.0, "GREEN"),
        ]
        for (up, total), breadth, expected in cases:
            cfg, raw = self._breadth_raw(up, total)
            state = MOD.build_state(cfg, raw)
            self.assertEqual(state["metrics"]["breadth_proxy"], breadth, (up, total))
            self.assertEqual(state["BREADTH"], expected, (up, total))
            self.assertEqual(state["LEADERS"], expected, (up, total))

    def test_leaders_reads_breadth_thresholds_from_config(self):
        cfg = json.loads(json.dumps(MOD.load_config()))
        cfg["thresholds"]["breadth_proxy_red"] = 0.20
        cfg["thresholds"]["breadth_proxy_green"] = 0.60
        for (up, total), expected in [((1, 10), "RED"), ((2, 10), "AMBER"), ((6, 10), "GREEN")]:
            state = MOD.build_state(*self._breadth_raw(up, total, cfg))
            self.assertEqual(state["BREADTH"], expected, (up, total))
            self.assertEqual(state["LEADERS"], expected, (up, total))

    def test_state_key_order_is_pinned(self):
        cfg, raw = self._breadth_raw(5, 10)
        self.assertEqual(
            list(MOD.build_state(cfg, raw)),
            [
                "schema_version", "asof", "session", "REGIME", "RISK", "TREND", "BREADTH",
                "LEADERS", "RATES", "FX", "OIL", "GOLD", "GEO", "BUY_TRIGGER",
                "DATA_QUALITY", "metrics",
            ],
        )


if __name__ == "__main__":
    unittest.main()
