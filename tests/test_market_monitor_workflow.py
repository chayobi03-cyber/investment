"""Run the market-monitor workflow's git steps against a local origin, twice.

The first run creates runtime/market-state with a tracked state file; every
later run must still be able to switch to that branch and push a new state.
"""
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "market-monitor.yml"

pytestmark = pytest.mark.skipif(shutil.which("git") is None, reason="needs git")


def _step(name: str) -> str:
    steps = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))["jobs"]["poll"]["steps"]
    return next(s["run"] for s in steps if s["name"] == name)


def _git(cwd: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=cwd, check=True, capture_output=True, text=True
    ).stdout


def _run_monitor(origin: Path, work: Path, tmp: Path, state: str) -> None:
    """Checkout main, restore, write a new state, update the runtime branch."""
    if work.exists():
        shutil.rmtree(work)
    _git(origin.parent, "clone", "-q", "--depth", "1", "--branch", "main", origin.as_uri(), str(work))
    saved = tmp / "market_state.json"
    script = "\n".join([
        _step("Restore previous runtime state"),
        # stands in for poll.py, which rewrites the working copy before cp
        f"printf '%s' '{state}' > runtime/market_state.json",
        f"cp runtime/market_state.json {saved}",
        _step("Update runtime branch").replace("/tmp/market_state.json", str(saved)),
    ])
    subprocess.run(["bash", "-e", "-c", script], cwd=work, check=True, capture_output=True, text=True)


def test_runtime_branch_update_works_on_every_run(tmp_path):
    origin = tmp_path / "origin.git"
    _git(tmp_path, "init", "-q", "--bare", "--initial-branch=main", str(origin))
    seed = tmp_path / "seed"
    _git(tmp_path, "clone", "-q", origin.as_uri(), str(seed))
    (seed / "README.md").write_text("main\n", encoding="utf-8")
    _git(seed, "add", "README.md")
    _git(seed, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "init")
    _git(seed, "push", "-q", "origin", "HEAD:main")

    work = tmp_path / "work"
    for n in range(1, 4):
        state = f'{{"run": {n}}}'
        _run_monitor(origin, work, tmp_path, state)
        stored = _git(tmp_path, "--git-dir", str(origin), "show", "runtime/market-state:runtime/market_state.json")
        assert stored == state
