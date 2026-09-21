import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MONITOR = ROOT / "scripts" / "market_monitor"
sys.path.insert(0, str(MONITOR))


def load(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_event_edge_uses_net_dividend():
    mod = load("dividend_event", MONITOR / "dividend_event_p0p6.py")
    x = mod.event_edge(275000, 4604)
    assert round(x["net_dividend"], 2) == round(4604 * (1 - 0.154), 2)
    assert x["gross_yield_pct"] > x["net_yield_pct"]
    assert x["event_edge_pct"] > 0


def test_event_window_excludes_ex_date_as_entry():
    mod = load("dividend_event2", MONITOR / "dividend_event_p0p6.py")
    rows = [
        {"asset_id": "SAMSUNG_ELECTRONICS", "date": "2026-09-28", "close": 275000},
        {"asset_id": "SAMSUNG_ELECTRONICS", "date": "2026-09-29", "close": 270000},
    ]
    out = mod.build_event_rows(rows, gross_dividend=4604)
    assert len(out) == 1
    assert out[0]["date"] == "2026-09-28"


def test_missing_dividend_fails_closed():
    mod = load("dividend_event3", MONITOR / "dividend_event_p0p6.py")
    result = mod.run(Path("/tmp/nonexistent-event-input.jsonl"), gross_dividend=None)
    assert result["status"] == "DATA_NOT_READY"
    assert "point-in-time expected dividend" in result["reason"]
