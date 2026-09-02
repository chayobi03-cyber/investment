import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_fixture_manifest_is_frozen():
    data = json.loads((ROOT / 'fixtures' / 'v0.2.3' / 'manifest.json').read_text())
    assert data['fixture_id'] == 'SC-FIX-0001'
    assert data['status'] == 'OFFICIAL_RECOVERED'
    assert data['files']['daily_panel.csv'].startswith('sha256:')
    assert data['source']['workflow_run_id'] == 33640923172


def test_anchor_registry_has_11_cases():
    text = (ROOT / 'fixtures' / 'v0.2.3' / 'anchors.yaml').read_text()
    assert text.count('  - id: ') == 11
    assert 'id: 2000_dotcom' in text
    assert 'id: 2008_gfc' in text
    assert 'id: 2020_covid' in text
    assert 'id: 2022_rate_shock' in text
