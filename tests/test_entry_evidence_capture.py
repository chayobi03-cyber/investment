from pathlib import Path
import importlib.util

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location("entry_evidence",ROOT/"scripts/market_monitor/capture_entry_evidence_kis.py")
assert SPEC and SPEC.loader
MOD=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)

def test_gap():
    assert MOD.derive_gap(100,103)==3.0
    assert MOD.derive_gap(None,103) is None

def test_first_regular():
    rows=[{"stck_cntg_hour":"153000"},{"stck_cntg_hour":"090100"},{"stck_cntg_hour":"090000"},{"stck_cntg_hour":"085900"}]
    assert MOD.first_regular_bar(rows)["stck_cntg_hour"]=="090000"

def test_evidence_types_and_gap():
    rows=MOD.build_records(
        "r1","005930","20260923",
        {"output2":[{"x":"estimate"}]},
        {"output":[{"stck_bsop_date":"20260922","frgn_ntby_qty":"200"}]},
        [{"stck_cntg_hour":"090000","stck_prdy_clpr":"100","stck_oprc":"102","stck_hgpr":"103","stck_lwpr":"101","stck_prpr":"102","cntg_vol":"1000"}],
        {"stck_prdy_clpr":"100"},
        "2026-09-23T06:00:00Z",
    )
    kinds={r["evidence_type"] for r in rows}
    assert {"foreign_flow_estimate","foreign_flow_daily_confirmed","intraday_1m","opening_gap_derived"} <= kinds
    gap=next(r for r in rows if r["evidence_type"]=="opening_gap_derived")
    assert gap["gap_pct"]==2.0

def test_bar_timestamp_semantics():
    rows=MOD.build_records(
        "r2","000660","20260923",{"output2":[]},{"output":[]},
        [{"stck_cntg_hour":"090500","stck_oprc":"100","stck_hgpr":"101","stck_lwpr":"99","stck_prpr":"100","cntg_vol":"1"}],
        {}, "2026-09-23T06:00:00Z")
    row=next(r for r in rows if r["evidence_type"]=="intraday_1m")
    assert row["observed_at"]=="2026-09-23T09:05:00+09:00"
    assert row["timestamp_semantics"]=="SOURCE_BAR_TIME"

def test_hash_order_independence():
    assert MOD.sha256_json({"b":2,"a":1})==MOD.sha256_json({"a":1,"b":2})
