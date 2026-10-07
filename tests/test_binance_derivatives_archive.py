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
