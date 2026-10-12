import hashlib
import json
import unittest

import pandas as pd

from datetime import timedelta

import numpy as np

from scripts.crypto.run_crypto_decomposition_v0_2 import (
    add_signal_type,
    decompose,
    grouped_summary,
)


class CryptoDecompositionTests(unittest.TestCase):
    def test_signal_type_is_deterministic(self):
        frame = pd.DataFrame(
            {
                "breakout": [True, False, False],
                "entry_state": ["B3", "B2", "B4"],
                "zone": ["BREAKOUT", "Z1", "Z3"],
            }
        )
        out = add_signal_type(frame)
        self.assertEqual(
            out["signal_type"].tolist(),
            ["breakout", "pullback", "pullback"],
        )

    def test_grouped_summary_keeps_event_count_and_return_stats(self):
        frame = pd.DataFrame(
            {
                "signal_type": ["pullback", "pullback", "breakout"],
                "forward_return_20d": [0.10, -0.02, 0.05],
                "mae_20d": [-0.05, -0.10, -0.03],
            }
        )
        out = grouped_summary(frame, ["signal_type"])
        rows = {x["signal_type"]: x for x in out}
        self.assertEqual(rows["pullback"]["events"], 2)
        self.assertAlmostEqual(rows["pullback"]["median_return_20d"], 0.04)
        self.assertEqual(rows["breakout"]["events"], 1)
        self.assertAlmostEqual(rows["breakout"]["positive_rate_20d"], 1.0)

    def test_decompose_runs_end_to_end(self):
        rng = np.random.default_rng(0)
        n = 900
        drift = np.repeat(rng.choice([0.004, -0.006, 0.008], size=n // 30 + 1), 30)[:n]
        close = 100 * np.exp(np.cumsum(drift + rng.normal(0, 0.025, n)))
        open_ = close * np.exp(rng.normal(0, 0.01, n))
        ts = pd.date_range("2022-01-01", periods=n, freq="D", tz="UTC")
        raw = pd.DataFrame({
            "timestamp": ts, "available_at": ts + timedelta(days=1),
            "open": open_, "high": np.maximum(open_, close) * 1.01,
            "low": np.minimum(open_, close) * 0.99, "close": close,
            "volume": rng.lognormal(10, 0.3, n),
        })
        result = decompose(raw)
        self.assertGreater(result["full_sample"]["primary_events"], 0)
        years = {row["year"] for row in result["full_sample"]["by_year"]}
        self.assertTrue(years <= {2022, 2023, 2024})
        self.assertFalse(result["threshold_retuned"])


def golden_fixture(n: int = 1500) -> pd.DataFrame:
    rng = np.random.default_rng(7)
    drift = np.repeat(rng.choice([0.004, -0.006, 0.0, 0.008], size=n // 30 + 1), 30)[:n]
    close = 100 * np.exp(np.cumsum(drift + rng.normal(0, 0.025, n)))
    open_ = close * np.exp(rng.normal(0, 0.01, n))
    ts = pd.date_range("2021-01-01", periods=n, freq="D", tz="UTC")
    return pd.DataFrame({
        "timestamp": ts, "available_at": ts + timedelta(days=1),
        "open": open_, "high": np.maximum(open_, close) * 1.01,
        "low": np.minimum(open_, close) * 0.99, "close": close,
        "volume": rng.lognormal(10, 0.3, n),
    })


def golden_permission_history(raw: pd.DataFrame) -> pd.DataFrame:
    ts = raw["timestamp"].iloc[::7].reset_index(drop=True)
    i = np.arange(len(ts))
    return pd.DataFrame({
        "decision_timestamp": ts, "available_at": ts + timedelta(days=1),
        "permission_status": np.where(i % 3 == 0, "BLOCKED", "PASS"),
        "market_gate": np.array(["GREEN", "YELLOW", "RED"])[i % 3],
        "confirmed_regime": np.array(["R1", "R2", "R3", "R4", "R5", "R6"])[(i // 5) % 6],
        "buy_allowed": False,
    })


def artifact_digest(result: dict) -> str:
    # Rounded so the pin survives last-bit float noise across library versions.
    def canon(x):
        if isinstance(x, float):
            return round(x, 10)
        if isinstance(x, dict):
            return {k: canon(v) for k, v in x.items()}
        if isinstance(x, list):
            return [canon(v) for v in x]
        return x

    text = json.dumps(canon(result), sort_keys=True, default=str)
    return hashlib.sha256(text.encode()).hexdigest()


class DecompositionArtifactGoldenTests(unittest.TestCase):
    """Pins the full decompose() artifact, with and without the PIT permission overlay."""

    def test_artifact_without_permission_history_is_pinned(self):
        result = decompose(golden_fixture())
        self.assertEqual(result["permission_overlay"]["status"], "DATA_NOT_READY")
        self.assertEqual(
            artifact_digest(result),
            "15c56e3908e04cd8d9dd31b0aff1ddc818e4e22d72dd3eb8ac624913cf8cf121",
        )

    def test_artifact_with_permission_history_is_pinned(self):
        raw = golden_fixture()
        result = decompose(raw, permission_history=golden_permission_history(raw))
        self.assertEqual(result["permission_overlay"]["status"], "PASS")
        self.assertEqual(result["market_regime"]["status"], "AVAILABLE")
        self.assertEqual(
            artifact_digest(result),
            "83cccb25305e9a627925b92e1fab9594a21a1b57788371ec58a8836140fb9d54",
        )

    def test_published_signal_type_is_uppercase(self):
        raw = golden_fixture()
        for history in (None, golden_permission_history(raw)):
            result = decompose(raw, permission_history=history)
            groups = (
                result["full_sample"]["by_signal_type"]
                + result["fixed_oos"]["by_signal_type"]
                + result["market_regime"]["by_regime_and_signal_type"]
                + [g for fold in result["walk_forward"] for g in fold["by_signal_type"]]
            )
            self.assertTrue(groups)
            self.assertEqual({g["signal_type"] for g in groups}, {"BREAKOUT", "PULLBACK"})


if __name__ == "__main__":
    unittest.main()
