from datetime import date

from scripts.crypto.fetch_binance_derivatives_archive import daily_url


def test_daily_metrics_url_contract():
    assert daily_url("BTCUSDT", date(2026, 9, 25)) == (
        "https://data.binance.vision/data/futures/um/daily/metrics/"
        "BTCUSDT/BTCUSDT-metrics-2026-09-25.zip"
    )


def test_supported_assets_are_explicit():
    from scripts.crypto.fetch_binance_derivatives_archive import SYMBOLS
    assert SYMBOLS == ("BTCUSDT", "ETHUSDT", "SOLUSDT")


def test_rows_carry_the_registered_primary_source_id(monkeypatch):
    import io
    import json
    import zipfile
    from pathlib import Path

    from scripts.crypto import fetch_binance_derivatives_archive as mod

    csv = (
        "create_time,symbol,sum_open_interest,sum_open_interest_value,"
        "count_toptrader_long_short_ratio,sum_toptrader_long_short_ratio,"
        "count_long_short_ratio,sum_taker_long_short_vol_ratio\n"
        "2026-09-25 00:05:00,BTCUSDT,1,2,3,4,5,6\n"
    )
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("BTCUSDT-metrics-2026-09-25.csv", csv)
    monkeypatch.setattr(mod, "fetch_zip", lambda url: (buf.getvalue(), "h" * 64))

    rows, missing = mod.collect_symbol("BTCUSDT", date(2026, 9, 25), date(2026, 9, 25))

    registry = json.loads(Path("config/permission_evidence_registry_v0.1.json").read_text(encoding="utf-8"))
    derivatives = next(f for f in registry["families"] if f["family_id"] == "derivatives")
    primary = next(s for s in derivatives["datasets"][0]["primary_sources"] if s["role"] == "PRIMARY")
    assert rows and not missing
    assert {r["source_id"] for r in rows} == {primary["source_id"]}


def _metrics_zip(symbol, rows):
    import io
    import zipfile

    header = (
        "create_time,symbol,sum_open_interest,sum_open_interest_value,"
        "count_toptrader_long_short_ratio,sum_toptrader_long_short_ratio,"
        "count_long_short_ratio,sum_taker_long_short_vol_ratio\n"
    )
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr(f"{symbol}-metrics.csv", header + "".join(r.format(s=symbol) + "\n" for r in rows))
    return buf.getvalue()


def test_collected_file_passes_the_evidence_bundle_validator(tmp_path, monkeypatch):
    import json
    import sys

    from scripts.crypto import fetch_binance_derivatives_archive as mod
    from scripts.crypto.validate_permission_evidence_bundle import validate

    rows = [
        "2024-01-01 00:00:00,{s},100.5,4200000.0,1.1,1.25,1.0,0.97",
        "2024-01-01 00:05:00,{s},101.0,,1.1,1.26,1.0,0.98",  # one missing metric value
    ]
    monkeypatch.setattr(
        mod, "fetch_zip",
        lambda url: (_metrics_zip(url.rsplit("/", 1)[-1].split("-")[0], rows), "f" * 64),
    )
    out = tmp_path / "binance_metrics_pit.csv"
    monkeypatch.setattr(sys, "argv", ["x", "--start", "2024-01-01", "--end", "2024-01-01", "--out", str(out)])
    assert mod.main() == 0

    fred = tmp_path / "fred_macro_pit.csv"
    fred.write_text(
        "asset,series_id,observation_timestamp,available_at,source_id,unit,value,ingested_at,provenance_hash\n"
        "MULTI_ASSET,FRED:DGS10,2024-01-01T00:00:00Z,2024-01-02T00:00:00Z,FRED:DGS10,raw,4.0,"
        "2024-01-03T00:00:00Z,0123456789abcdef\n",
        encoding="utf-8",
    )
    result = validate([fred, out])  # the backfill workflow's validation step
    assert result["status"] == "PASS"
    # 3 symbols x (2 timestamps x 4 metrics - 1 missing value)
    assert result["rows"] == 1 + 3 * 7

    manifest = json.loads(out.with_suffix(".manifest.json").read_text(encoding="utf-8"))
    # Dropped, never zero-filled. The series still has an observation that day,
    # so a missing value inside a covered day is not a day gap.
    assert manifest["null_metric_values_dropped"] == 3
    assert manifest["missing_series_days"] == {}

    import pandas as pd
    df = pd.read_csv(out)
    btc_oi = df[df["series_id"] == "BINANCE:BTCUSDT:sum_open_interest"]
    assert btc_oi["value"].tolist() == [100.5, 101.0]
    assert set(df["unit"]) == {"base_asset", "USDT", "ratio"}


FULL = "2024-01-0{day} 00:00:00,{{s}},100.5,4200000.0,1.1,1.25,1.0,0.97"


def _run(tmp_path, monkeypatch, archive, start="2024-01-01", end="2024-01-02"):
    """Run the collector with archive(symbol, day) -> zip bytes, or None for a 404."""
    import json
    import sys

    import requests

    from scripts.crypto import fetch_binance_derivatives_archive as mod

    def fake_fetch(url):
        name = url.rsplit("/", 1)[-1]
        symbol, day = name.split("-")[0], name.removesuffix(".zip")[-10:]
        payload = archive(symbol, day)
        if payload is None:
            response = requests.Response()
            response.status_code = 404
            raise requests.HTTPError(response=response)
        return payload, "f" * 64

    monkeypatch.setattr(mod, "fetch_zip", fake_fetch)
    out = tmp_path / "binance_metrics_pit.csv"
    monkeypatch.setattr(sys, "argv", ["x", "--start", start, "--end", end, "--out", str(out)])
    assert mod.main() == 0
    return out, json.loads(out.with_suffix(".manifest.json").read_text(encoding="utf-8"))


def _full_day(symbol, day):
    return _metrics_zip(symbol, [FULL.format(day=int(day[-2:]))])


def _assert_bundle_fails(out, reason):
    import pytest

    from scripts.crypto.validate_permission_evidence_bundle import validate

    with pytest.raises(SystemExit, match=reason):
        validate([out])


def test_complete_archive_has_no_series_gaps(tmp_path, monkeypatch):
    from scripts.crypto.validate_permission_evidence_bundle import validate

    out, manifest = _run(tmp_path, monkeypatch, _full_day)
    assert manifest["status"] == "COLLECTED_PROVISIONAL_PIT"
    assert manifest["missing_series_days"] == {}
    assert validate([out])["series"] == 12


def test_a_blank_metric_for_a_whole_day_is_a_gap(tmp_path, monkeypatch):
    def archive(symbol, day):
        if symbol == "SOLUSDT" and day == "2024-01-02":
            return _metrics_zip(symbol, ["2024-01-02 00:00:00,{s},100.5,4200000.0,1.1,1.25,1.0,"])
        return _full_day(symbol, day)

    out, manifest = _run(tmp_path, monkeypatch, archive)
    assert manifest["status"] == "COLLECTED_WITH_GAPS"
    assert manifest["missing_series_days"] == {"BINANCE:SOLUSDT:sum_taker_long_short_vol_ratio": ["2024-01-02"]}
    assert manifest["null_metric_values_dropped"] == 1
    _assert_bundle_fails(out, "source_manifest_has_gaps")


def test_a_metric_column_missing_from_the_archive_is_a_gap(tmp_path, monkeypatch):
    import io
    import zipfile

    def archive(symbol, day):
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr(
                f"{symbol}-metrics.csv",
                "create_time,symbol,sum_open_interest,sum_open_interest_value_usd,"
                "count_toptrader_long_short_ratio,sum_toptrader_long_short_ratio,"
                "count_long_short_ratio,sum_taker_long_short_vol_ratio\n"
                f"{day} 00:00:00,{symbol},100.5,4200000.0,1.1,1.25,1.0,0.97\n",
            )
        return buf.getvalue()

    out, manifest = _run(tmp_path, monkeypatch, archive)
    assert manifest["status"] == "COLLECTED_WITH_GAPS"
    assert sorted(manifest["missing_series_days"]) == [
        f"BINANCE:{s}:sum_open_interest_value" for s in ("BTCUSDT", "ETHUSDT", "SOLUSDT")
    ]
    _assert_bundle_fails(out, "source_manifest_has_gaps")


def test_a_header_only_day_is_a_gap(tmp_path, monkeypatch):
    from scripts.crypto import fetch_binance_derivatives_archive as mod

    def archive(symbol, day):
        if symbol == "ETHUSDT" and day == "2024-01-02":
            return _metrics_zip(symbol, [])
        return _full_day(symbol, day)

    out, manifest = _run(tmp_path, monkeypatch, archive)
    assert manifest["status"] == "COLLECTED_WITH_GAPS"
    assert manifest["missing_days"]["ETHUSDT"] == []  # the file existed
    assert manifest["missing_series_days"] == {
        f"BINANCE:ETHUSDT:{m}": ["2024-01-02"] for m in mod.METRIC_UNITS
    }
    _assert_bundle_fails(out, "source_manifest_has_gaps")


def test_nothing_collected_fails_closed(tmp_path, monkeypatch):
    out, manifest = _run(tmp_path, monkeypatch, lambda symbol, day: _metrics_zip(symbol, []))
    assert manifest["status"] == "COLLECTED_WITH_GAPS"
    assert len(manifest["missing_series_days"]) == 12
    _assert_bundle_fails(out, "source_manifest_has_gaps")

    out.with_suffix(".manifest.json").unlink()  # even without a manifest
    _assert_bundle_fails(out, "no_rows")


def test_a_missing_archive_day_is_still_a_gap(tmp_path, monkeypatch):
    out, manifest = _run(
        tmp_path, monkeypatch,
        lambda symbol, day: None if (symbol, day) == ("BTCUSDT", "2024-01-01") else _full_day(symbol, day),
    )
    assert manifest["missing_days"]["BTCUSDT"] == ["2024-01-01"]
    assert manifest["status"] == "COLLECTED_WITH_GAPS"
    _assert_bundle_fails(out, "source_manifest_has_gaps")


def test_a_non_numeric_value_raises_instead_of_being_dropped(tmp_path, monkeypatch):
    import pytest

    def archive(symbol, day):
        return _metrics_zip(symbol, [f"{day} 00:00:00,{{s}},100.5,#N/A!,1.1,1.25,1.0,0.97"])

    with pytest.raises(ValueError, match="BINANCE_NON_NUMERIC_METRIC:.*:sum_open_interest_value:"):
        _run(tmp_path, monkeypatch, archive)


def test_start_after_end_is_rejected(tmp_path, monkeypatch):
    import pytest

    with pytest.raises(SystemExit):
        _run(tmp_path, monkeypatch, _full_day, start="2024-01-05", end="2024-01-01")
