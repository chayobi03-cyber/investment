import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_script(path: str) -> dict:
    result = subprocess.run(
        [sys.executable, str(ROOT / path)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout)


def test_capital_matrix_has_exactly_12_cases():
    output = run_script("scripts/run_capital_matrix.py")
    assert output["case_count"] == 12
    assert len(output["cases"]) == 12
    assert {row["case_id"] for row in output["cases"]}.__len__() == 12


def test_stress_matrix_has_12_cases_and_60_results():
    output = run_script("scripts/run_stress_matrix.py")
    assert output["case_count"] == 12
    assert output["scenario_count"] == 5
    assert output["result_count"] == 60

    losses = [row["loss_krw"] for row in output["results"]]
    assert min(losses) < 0
