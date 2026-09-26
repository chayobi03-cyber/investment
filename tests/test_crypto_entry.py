import unittest

import pandas as pd

from src.investment_pipeline.crypto_entry import (
    add_forward_outcomes,
    add_entry_features,
    cluster_episodes,
    generate_signals,
)


def make_frame(n=260):
    dates = pd.date_range("2025-01-01", periods=n, freq="D", tz="UTC")
    base = pd.Series(range(n), dtype=float) * 10 + 1000
    close = base.copy()
    # Deterministic pullback and recovery within a valid long-term trend.
    close.iloc[180:186] *= 0.93
    close.iloc[186:191] *= 0.96
    high = close * 1.01
    low = close * 0.99
    open_ = close.shift(1).fillna(close.iloc[0])
    return pd.DataFrame(
        {
            "timestamp": dates,
            "available_at": dates + pd.Timedelta(hours=1),
            "open": open_,
            "high": high,
            "low": low,
            "close": close,
            "volume": 1000.0,
        }
    )


class CryptoEntryTests(unittest.TestCase):
    def test_prior_high_avoids_lookahead(self):
        out = add_entry_features(make_frame())
        self.assertLessEqual(out.iloc[200]["prior_high60"], out.iloc[199]["high"])

    def test_insufficient_history_is_data_not_ready(self):
        out = generate_signals(make_frame(100))
        self.assertTrue((out["entry_state"] == "B0").all())

    def test_signal_generation_exposes_timing_fields(self):
        out = generate_signals(make_frame())
        self.assertIn("entry_state", out.columns)
        self.assertIn("zone", out.columns)
        self.assertIn("drawdown60", out.columns)
        self.assertIn("stabilization", out.columns)

    def test_episode_clustering_deduplicates(self):
        out = cluster_episodes(generate_signals(make_frame()), cooldown_bars=5)
        candidate = int(out["entry_state"].isin(["B2", "B3", "B4"]).sum())
        primary = int(out["primary_event"].sum())
        self.assertGreater(primary, 0)
        self.assertLessEqual(primary, candidate)

    def test_forward_outcomes_use_next_open(self):
        out = add_forward_outcomes(
            cluster_episodes(generate_signals(make_frame()))
        )
        self.assertAlmostEqual(
            out.iloc[100]["entry_price_20d"],
            out.iloc[101]["open"],
        )
        self.assertIn("mae_20d", out.columns)
        self.assertIn("mfe_20d", out.columns)

    def test_forward_mae_uses_future_window(self):
        df = make_frame()
        out = add_forward_outcomes(generate_signals(df), horizons=(5,))
        row = out.iloc[100]
        entry = out.iloc[101]["open"]
        future_low = out.iloc[101:106]["low"].min()
        self.assertAlmostEqual(row["entry_price_5d"], entry)
        self.assertAlmostEqual(row["mae_5d"], future_low / entry - 1.0)

    def test_insufficient_ma_history_does_not_create_trade_signal(self):
        out = generate_signals(make_frame(199))
        self.assertTrue((out["entry_state"] == "B0").all())


if __name__ == "__main__":
    unittest.main()
