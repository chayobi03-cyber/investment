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


def _response(status, body=b"observation_date,DGS10\n2024-01-02,4.0\n"):
    import requests

    r = requests.Response()
    r.status_code = status
    r._content = body
    r.url = "https://fred.stlouisfed.org/graph/fredgraph.csv"
    return r


def test_fetch_retries_timeouts_and_server_errors(monkeypatch):
    import requests

    from scripts.crypto import fetch_fred_permission_macro as mod

    outcomes = [requests.ReadTimeout("slow"), _response(503), _response(200)]
    calls, sleeps = [], []

    def fake_get(*args, **kwargs):
        calls.append(1)
        out = outcomes.pop(0)
        if isinstance(out, Exception):
            raise out
        return out

    monkeypatch.setattr(mod.requests, "get", fake_get)
    monkeypatch.setattr(mod.time, "sleep", sleeps.append)
    data, _ = mod.fetch_series("DGS10", "2024-01-01", "2024-01-07")
    assert len(calls) == 3 and sleeps == [2, 4]
    assert data["value"].tolist() == [4.0]


def test_fetch_gives_up_after_the_last_retry(monkeypatch):
    import pytest
    import requests

    from scripts.crypto import fetch_fred_permission_macro as mod

    sleeps = []

    def always_timeout(*args, **kwargs):
        raise requests.ReadTimeout("slow")

    monkeypatch.setattr(mod.requests, "get", always_timeout)
    monkeypatch.setattr(mod.time, "sleep", sleeps.append)
    with pytest.raises(requests.ReadTimeout):
        mod.fetch_series("DGS10", "2024-01-01", "2024-01-07")
    assert sleeps == [2, 4, 8]


def test_fetch_does_not_retry_client_errors(monkeypatch):
    import pytest
    import requests

    from scripts.crypto import fetch_fred_permission_macro as mod

    calls = []
    monkeypatch.setattr(mod.requests, "get", lambda *a, **k: calls.append(1) or _response(404))
    monkeypatch.setattr(mod.time, "sleep", lambda s: None)
    with pytest.raises(requests.HTTPError):
        mod.fetch_series("NOPE", "2024-01-01", "2024-01-07")
    assert len(calls) == 1
