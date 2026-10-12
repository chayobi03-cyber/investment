import json
import tempfile
import unittest
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
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
            "BUY_TRIGGER": "UNCONFIRMED", "DATA_QUALITY": "GREEN", "metrics": {"VIX_pct": 1.0, "VIX_15m_pct": 1.0, "VIX_daily_close_pct": None},
        }
        cases = [
            (None, {}, ("P2", False)),
            (base, {"DATA_QUALITY": "RED"}, ("P1", True)),
            (base, {"RISK": "RED"}, ("P0", True)),
            (base, {"RISK": "RED", "metrics": {"VIX_pct": None, "VIX_15m_pct": None, "VIX_daily_close_pct": None}}, ("P2", False)),
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
            g: {
                name: {"ok": True, "change_pct_5m": 0.05, "change_pct_15m": 0.1,
                       "session_change_pct": 0.2, "last_completed_session_return_pct": 0.1,
                       "market_session_state": "ACTIVE", "timestamp": ts}
                for name in syms
            }
            for g, syms in cfg["symbols"].items()
        }
        if vix is None:
            groups["indices"].pop("VIX")
        else:
            groups["indices"]["VIX"] = vix
        flat = {f"{g}.{n}": v for g, items in groups.items() for n, v in items.items()}
        return cfg, {"collected_at": ts, "groups": groups, "all": flat}

    def test_build_state_reads_vix_change(self):
        cfg, raw = self._raw({"ok": True, "change_pct_15m": 2.5, "change_pct_5m": 0.8, "session_change_pct": 1.2, "last_completed_session_return_pct": 0.1, "market_session_state": "ACTIVE", "timestamp": "2026-10-08T00:00:00Z"})
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
        leaders = {
            f"L{i}": {
                "ok": True,
                "change_pct_15m": 1.0 if i < up else -1.0,
                "change_pct_5m": 0.1 if i < up else -0.1,
                "session_change_pct": 1.0 if i < up else -1.0,
                "last_completed_session_return_pct": 0.5 if i < up else -0.5,
                "market_session_state": "ACTIVE",
                "timestamp": "2026-10-08T00:00:00Z",
            }
            for i in range(total)
        }
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


    def test_chart_parser_separates_5m_15m_and_daily_close_returns(self):
        zone = ZoneInfo("Asia/Seoul")
        bars = [
            (datetime(2026, 10, 9, 15, 25, tzinfo=zone), 6625.93),
            (datetime(2026, 10, 12, 9, 0, tzinfo=zone), 6500.0),
            (datetime(2026, 10, 12, 15, 25, tzinfo=zone), 6384.24),
            (datetime(2026, 10, 13, 9, 0, tzinfo=zone), 6380.0),
            (datetime(2026, 10, 13, 9, 15, tzinfo=zone), 6350.0),
            (datetime(2026, 10, 13, 9, 25, tzinfo=zone), 6320.0),
            (datetime(2026, 10, 13, 9, 30, tzinfo=zone), 6310.0),
        ]
        timestamps = [int(dt.timestamp()) for dt, _ in bars]
        closes = [price for _, price in bars]
        now = datetime(2026, 10, 13, 9, 30, tzinfo=zone)
        result = MOD.summarize_chart_payload(
            "^KS11",
            {"exchangeTimezoneName": "Asia/Seoul", "currency": "KRW", "exchangeName": "KSE"},
            timestamps,
            closes,
            market_session="KOREA",
            cfg=MOD.load_config(),
            now=now,
        )
        self.assertEqual(result["market_session_state"], "ACTIVE")
        self.assertAlmostEqual(result["change_pct_5m"], (6310 / 6320 - 1) * 100, places=6)
        self.assertAlmostEqual(result["change_pct_15m"], (6310 / 6350 - 1) * 100, places=6)
        self.assertAlmostEqual(
            result["last_completed_session_return_pct"],
            (6384.24 / 6625.93 - 1) * 100,
            places=5,
        )
        self.assertNotAlmostEqual(result["change_pct_15m"], result["last_completed_session_return_pct"], places=2)

    def test_fresh_fx_cannot_mask_stale_required_korea_series(self):
        cfg, raw = self._raw({"ok": True, "change_pct_5m": 0.05, "change_pct_15m": 0.1, "session_change_pct": 0.2, "last_completed_session_return_pct": 0.1, "market_session_state": "CLOSED", "timestamp": "2026-10-08T00:00:00Z"})
        raw["collected_at"] = "2026-10-08T00:45:00Z"  # 09:45 KST: Korea session is active.
        for key in ("KOSPI", "KOSDAQ", "VIX", "NASDAQ", "SOX", "SP500"):
            if key in raw["groups"]["indices"]:
                raw["groups"]["indices"][key]["market_session_state"] = "CLOSED"
        raw["groups"]["indices"]["KOSPI"]["market_session_state"] = "ACTIVE"
        raw["groups"]["indices"]["KOSDAQ"]["market_session_state"] = "ACTIVE"
        for name in cfg["symbols"]["korea_leaders"]:
            raw["groups"]["korea_leaders"][name]["timestamp"] = "2026-10-08T00:00:00Z"
            raw["groups"]["korea_leaders"][name]["market_session_state"] = "ACTIVE"
        raw["groups"]["indices"]["KOSPI"]["timestamp"] = "2026-10-08T00:00:00Z"
        raw["groups"]["indices"]["KOSDAQ"]["timestamp"] = "2026-10-08T00:00:00Z"
        for name in cfg["symbols"]["us_leaders"]:
            raw["groups"]["us_leaders"][name]["market_session_state"] = "CLOSED"
        raw["groups"]["macro"]["USD_JPY"]["timestamp"] = raw["collected_at"]
        raw["groups"]["macro"]["USD_JPY"]["market_session_state"] = "ACTIVE"

        state = MOD.build_state(cfg, raw)
        self.assertEqual(state["metrics"]["freshness_by_series"]["indices.KOSPI"], "STALE")
        self.assertNotEqual(state["DATA_QUALITY"], "GREEN")
        severity, alert = MOD.should_alert(None, state, [])
        self.assertEqual(severity, "P1")
        self.assertTrue(alert)


    def test_closed_session_uses_daily_close_and_initial_stress_is_alerted(self):
        cfg, raw = self._raw({
            "ok": True,
            "change_pct_5m": 0.05,
            "change_pct_15m": 0.1,
            "session_change_pct": None,
            "last_completed_session_return_pct": 2.0,
            "market_session_state": "CLOSED",
            "timestamp": "2026-10-12T20:00:00Z",
        })
        raw["collected_at"] = "2026-10-12T22:30:00Z"  # 07:30 KST, before the Korea session.
        for group in raw["groups"].values():
            for item in group.values():
                item["market_session_state"] = "CLOSED"
        korea_ts = "2026-10-12T06:00:00Z"
        us_ts = "2026-10-12T20:00:00Z"
        daily_moves = {"KOSPI": -3.65, "KOSDAQ": -4.83, "SP500": -0.8, "NASDAQ": -0.44, "SOX": -2.7, "VIX": 2.0}
        for name, item in raw["groups"]["indices"].items():
            item["timestamp"] = korea_ts if name in {"KOSPI", "KOSDAQ"} else us_ts
            item["last_completed_session_return_pct"] = daily_moves.get(name, 0.1)
        for item in raw["groups"]["korea_leaders"].values():
            item["timestamp"] = korea_ts
            item["last_completed_session_return_pct"] = -4.0
        for item in raw["groups"]["us_leaders"].values():
            item["timestamp"] = us_ts
            item["last_completed_session_return_pct"] = 0.5

        state = MOD.build_state(cfg, raw)
        self.assertEqual(state["session"], "GLOBAL_TRANSITION")
        self.assertEqual(state["DATA_QUALITY"], "GREEN")
        self.assertIsNone(state["metrics"]["KOSPI_15m_pct"])
        self.assertAlmostEqual(state["metrics"]["KOSPI_daily_close_pct"], -3.65, places=6)
        self.assertEqual(state["TREND"], "RED")
        severity, alert = MOD.should_alert(None, state, [])
        self.assertEqual(severity, "P0")
        self.assertTrue(alert)


if __name__ == "__main__":
    unittest.main()
