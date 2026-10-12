"""KRX / OpenDART connector construction contract and KRX dataset serialization."""

import json

import pytest

from src.investment_pipeline.connectors import krx, opendart


@pytest.fixture
def no_env(monkeypatch):
    for name in ("KRX_API_BASE_URL", "KRX_API_KEY", "OPENDART_API_KEY"):
        monkeypatch.delenv(name, raising=False)


def test_krx_constructor_requires_base_url_then_key(no_env, monkeypatch):
    with pytest.raises(ValueError, match="^KRX_API_BASE_URL is required$"):
        krx.KRXClient()
    # "/" is empty after rstrip
    with pytest.raises(ValueError, match="^KRX_API_BASE_URL is required$"):
        krx.KRXClient(base_url="/", api_key="k")
    with pytest.raises(ValueError, match="^KRX_API_KEY is required$"):
        krx.KRXClient(base_url="https://krx.example/")
    monkeypatch.setenv("KRX_API_BASE_URL", "https://env.example/")
    monkeypatch.setenv("KRX_API_KEY", "env-key")
    assert (krx.KRXClient().base_url, krx.KRXClient().api_key) == ("https://env.example", "env-key")
    client = krx.KRXClient(base_url="https://arg.example//", api_key="arg-key")
    assert (client.base_url, client.api_key) == ("https://arg.example", "arg-key")


def test_opendart_constructor_requires_key(no_env, monkeypatch):
    with pytest.raises(ValueError, match="^OPENDART_API_KEY is required$"):
        opendart.OpenDARTClient()
    assert opendart.OpenDARTClient(api_key="arg-key").api_key == "arg-key"
    monkeypatch.setenv("OPENDART_API_KEY", "env-key")
    assert opendart.OpenDARTClient().api_key == "env-key"


def test_krx_fetch_dataset_writes_unescaped_indented_json(tmp_path, monkeypatch):
    client = krx.KRXClient(base_url="https://krx.example", api_key="k")
    payload = {"종목": "삼성전자", "rows": [{"close": 1.5}]}
    monkeypatch.setattr(client, "get_json", lambda path, params=None: payload)
    out = client.fetch_dataset("/x", {}, tmp_path / "sub" / "out.json")
    assert out == tmp_path / "sub" / "out.json"
    assert out.read_text(encoding="utf-8") == json.dumps(payload, ensure_ascii=False, indent=2)
    assert out.read_text(encoding="utf-8") == (
        '{\n  "종목": "삼성전자",\n  "rows": [\n    {\n      "close": 1.5\n    }\n  ]\n}'
    )


def test_unused_env_helpers_are_gone():
    # Constructors are the single validation path (ValueError, explicit args win).
    assert not hasattr(krx, "require_env")
    assert not hasattr(opendart, "require_env")
