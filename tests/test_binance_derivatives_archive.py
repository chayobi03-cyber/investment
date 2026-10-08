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
    assert manifest["null_metric_values_dropped"] == 3  # dropped, never zero-filled

    import pandas as pd
    df = pd.read_csv(out)
    btc_oi = df[df["series_id"] == "BINANCE:BTCUSDT:sum_open_interest"]
    assert btc_oi["value"].tolist() == [100.5, 101.0]
    assert set(df["unit"]) == {"base_asset", "USDT", "ratio"}
