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


if __name__ == "__main__":
    unittest.main()
