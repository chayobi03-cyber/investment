import unittest

import pandas as pd

from scripts.crypto.run_crypto_decomposition_v0_2 import (
    add_signal_type,
    grouped_summary,
)


class CryptoDecompositionTests(unittest.TestCase):
    def test_signal_type_is_deterministic(self):
        frame = pd.DataFrame(
            {
                "breakout": [True, False, False],
                "entry_state": ["B3", "B2", "B4"],
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


if __name__ == "__main__":
    unittest.main()
