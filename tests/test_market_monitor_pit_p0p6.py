import importlib.util
import json
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


DECISION = load(
    "decision_pipeline_test",
    ROOT / "scripts/market_monitor/decision_pipeline.py",
)
POLL = load(
    "market_monitor_poll_test",
    ROOT / "scripts/market_monitor/poll.py",
)
BUILDER = load(
    "historical_pit_builder_test",
    ROOT / "scripts/market_monitor/build_historical_pit_v3.py",
)
BACKTEST = load(
    "p0_p6_backtest_test",
    ROOT / "scripts/market_monitor/p0_p6_backtest.py",
)
PIT_CONTRACT = load(
    "pit_contract_test",
    ROOT / "scripts/market_monitor/pit_contract.py",
)


def test_live_monitor_emits_observation_schema_v3():
    observed = datetime(2026, 9, 22, 0, 0, tzinfo=timezone.utc)
    available = datetime(2026, 9, 22, 0, 5, tzinfo=timezone.utc)
    row = POLL.build_live_observation(
        "SK_HYNIX",
        "korea_leaders",
        {
            "ok": True,
            "symbol": "000660.KS",
            "price": 100.0,
            "prev_price": 98.0,
            "change_pct": 2.0408,
            "timestamp": observed.isoformat().replace("+00:00", "Z"),
        },
        available,
    )
    assert row is not None
    assert row["schema_version"] == "3.0"
    assert row["observed_at"].startswith("2026-09-22T00:00")
    assert row["available_at"].startswith("2026-09-22T00:05")
    assert row["source_id"] == "yahoo_finance_chart"
    assert row["rule_version"] == "observation-v3.0-live-adapter"
    assert row["returns_pct"]["d1"] is None
    assert row["intraday_change_pct"] is not None
    assert row["observation_interval"] == "5m"
    assert row["quality"]["status"] == "AMBER"


def test_historical_builder_keeps_vendor_ohlc_raw():
    frame = BUILDER.pd.DataFrame(
        {
            "date": [BUILDER.pd.Timestamp("2026-01-01", tz="UTC")],
            "open": [100.0],
            "high": [101.0],
            "low": [99.0],
            "close_raw": [100.0],
            "close": [100.0],
            "volume": [1000.0],
        }
    )
    rows = BUILDER.series_feature_rows("SAMSUNG", frame)
    assert rows[0]["price_vintage_policy"] == "VENDOR_CURRENT_RAW"
    assert rows[0]["corporate_action_adjustment_applied"] is False
    assert rows[0]["normalization_status"] == "RAW_OHLC_NO_CORPORATE_ACTION_ADJUSTMENT"


def test_historical_split_boundaries_are_time_ordered():
    assert BUILDER.split_for_date("2018-12-31") == "development"
    assert BUILDER.split_for_date("2019-01-01") == "validation"
    assert BUILDER.split_for_date("2021-12-31") == "validation"
    assert BUILDER.split_for_date("2022-01-01") == "oos"


def test_pit_contract_blocks_vendor_history_proxy():
    result = PIT_CONTRACT.validate_pit_manifest(
        {
            "pit_status": "VENDOR_HISTORY_PROXY",
            "pit_archival_revisions": False,
            "price_vintage_policy": "VENDOR_CURRENT_RAW",
        }
    )
    assert result["status"] == "NOT_GREEN"
    assert result["strict_pit"] is False
    assert "vendor history is not archival PIT" in result["blockers"]


def test_pit_contract_accepts_complete_archival_manifest():
    result = PIT_CONTRACT.validate_pit_manifest(
        {
            "pit_status": "STRICT_PIT_ARCHIVAL",
            "pit_archival_revisions": True,
            "price_vintage_policy": "AS_PUBLISHED",
            "source_version": "krx-archive-v1",
            "artifact_sha256": "abc",
        }
    )
    assert result["status"] == "GREEN"
    assert result["strict_pit"] is True
    assert result["blockers"] == []


def test_backtest_runs_p0_to_p5_and_blocks_p6():
    row = {
        "schema_version": "3.0",
        "date": "2022-01-03",
        "split": "oos",
        "asset_id": "TEST",
        "episode_id": "E1",
        "close": 100.0,
        "price_signal": True,
        "price_location_pass": True,
        "extension_pass": True,
        "leadership_pass": True,
        "macro_pass": True,
        "attribution_pass": True,
        "fundamentals_pass": False,
        "entry_open": 100.0,
        "entry_date": "2022-01-04",
        "asset_rows": [
            {"date": "2022-01-04", "open": 100.0, "high": 103.0, "low": 99.0, "close": 102.0},
            {"date": "2022-01-05", "open": 102.0, "high": 105.0, "low": 101.0, "close": 104.0},
            {"date": "2022-01-06", "open": 104.0, "high": 106.0, "low": 103.0, "close": 105.0},
            {"date": "2022-01-07", "open": 105.0, "high": 107.0, "low": 104.0, "close": 106.0},
            {"date": "2022-01-10", "open": 106.0, "high": 108.0, "low": 105.0, "close": 107.0},
        ],
        "entry_opportunity_label": True,
    }

    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        events = root / "events.jsonl"
        events.write_text(json.dumps(row) + "\n", encoding="utf-8")
        manifest = root / "manifest.json"
        manifest.write_text(
            json.dumps(
                {
                    "pit_status": "VENDOR_HISTORY_PROXY",
                    "pit_rows": 1000,
                    "pit_asset_rows": 1000,
                    "pit_asset_days_by_year": {"2022": 1000},
                    "asset_count": 10,
                    "fundamentals_status": "DATA_NOT_READY",
                    "pit_archival_revisions": False,
                    "price_vintage_policy": "VENDOR_CURRENT_RAW",
                }
            ),
            encoding="utf-8",
        )

        result = BACKTEST.run(events, manifest)
        assert result["status"] == "PARTIAL_OK"
        assert result["splits"]["oos"]["P0"]["status"] == "OK"
        assert result["splits"]["oos"]["P5"]["status"] == "OK"
        assert result["splits"]["oos"]["P6"]["status"] == "DATA_NOT_READY"
        assert result["splits"]["oos"]["P0"]["5d_mean_return_pct"] is not None
        assert "false_positive_rate" not in result["splits"]["oos"]["P0"]
        assert result["splits"]["oos"]["P0"]["classification"]["status"] == "DATA_NOT_READY"


def test_decision_pipeline_primitives_remain_compatible():
    shock = DECISION.signed_shock(102.0, 100.0, stress_polarity=1)
    assert shock["raw_pct"] > 0
    assert shock["stress_signed_pct"] > 0

def test_dart_fundamental_pit_respects_filing_time():
    dart = load(
        "pit_fundamentals_test",
        ROOT / "scripts/market_monitor/pit_fundamentals.py",
    )
    rows = [
        {
            "corp_code": "00126380",
            "corp_name": "Example",
            "stock_code": "000000",
            "rcept_no": "20260331000001",
            "rcept_dt": "20260331",
            "bsns_year": "2025",
            "reprt_code": "11011",
            "fs_div": "CFS",
            "sj_div": "BS",
            "account_id": "ifrs-full_Assets",
            "account_nm": "자산총계",
            "thstrm_amount": "1000000",
        },
        {
            "corp_code": "00126380",
            "corp_name": "Example",
            "stock_code": "000000",
            "rcept_no": "20260630000001",
            "rcept_dt": "20260630",
            "bsns_year": "2026",
            "reprt_code": "11011",
            "fs_div": "CFS",
            "sj_div": "BS",
            "account_id": "ifrs-full_Assets",
            "account_nm": "자산총계",
            "thstrm_amount": "1200000",
        },
    ]
    decision_at = datetime(2026, 5, 1, tzinfo=timezone.utc)
    result = dart.available_facts(rows, decision_at=decision_at)
    assert result["status"] == "OK"
    assert result["eligible_count"] == 1
    assert result["facts"][0]["rcept_no"] == "20260331000001"
    assert result["facts"][0]["pit_status"] == "DART_AS_PUBLISHED_CAPTURE"
    assert result["excluded_count"] == 1


def test_dart_fundamental_pit_blocks_latest_value_without_filing_provenance():
    dart = load(
        "pit_fundamentals_missing_test",
        ROOT / "scripts/market_monitor/pit_fundamentals.py",
    )
    result = dart.available_facts(
        [{"account_id": "ifrs-full_Assets", "account_nm": "자산총계"}],
        decision_at=datetime(2026, 5, 1, tzinfo=timezone.utc),
    )
    assert result["status"] == "DATA_NOT_READY"
    assert result["eligible_count"] == 0
