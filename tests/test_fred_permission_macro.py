from pathlib import Path
import json

from scripts.crypto.fetch_fred_permission_macro import SERIES


def test_fred_registry_does_not_fake_dxy():
    assert "DTWEXBGS" in SERIES
    assert SERIES["DTWEXBGS"] == "BROAD_USD_INDEX"
    assert "DXY" not in SERIES


def test_macro_collector_is_present():
    path = Path("scripts/crypto/fetch_fred_permission_macro.py")
    assert path.exists()
