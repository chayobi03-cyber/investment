"""B3+ push decision (scripts/crypto/push/decide.mjs): who gets alerted and when."""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
NODE = shutil.which("node")
pytestmark = pytest.mark.skipif(NODE is None, reason="node not installed")


def decide(snapshot: dict, last: dict) -> dict:
    script = (
        "import { decideAlert } from './scripts/crypto/push/decide.mjs';"
        f"process.stdout.write(JSON.stringify(decideAlert({json.dumps(snapshot)}, {json.dumps(last)})));"
    )
    out = subprocess.run([NODE, "--input-type=module", "-e", script],
                         capture_output=True, text=True, cwd=ROOT, check=True)
    return json.loads(out.stdout)


@pytest.mark.parametrize("state", ["B0", "B1", "B2"])
def test_below_b3_never_sends(state):
    assert not decide({"daily_core_state": state, "decision_bar": "d1"}, {})["send"]


@pytest.mark.parametrize("state", ["B3", "B4"])
def test_b3_plus_sends_once_per_daily_bar(state):
    snap = {"daily_core_state": state, "decision_bar": "d2"}
    assert decide(snap, {})["send"]
    assert decide(snap, {"decision_bar": "d1"})["send"]
    assert not decide(snap, {"decision_bar": "d2"})["send"]
