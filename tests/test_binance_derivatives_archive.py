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
