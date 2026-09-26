"""Investment data pipeline V1.

Stages are intentionally explicit:
raw source rows -> completeness gate -> raw factors -> point-in-time normalization.
"""

from .crypto_entry import (
    EntrySignal,
    add_entry_features,
    add_forward_outcomes,
    cluster_episodes,
    generate_signals,
)
from .crypto_risk import (
    CryptoDecision,
    CryptoObservation,
    DataNotReady,
    compute_market_score,
    evaluate,
)
from .pipeline import build_factor_dataset

__all__ = [
    "build_factor_dataset",
    "CryptoDecision",
    "CryptoObservation",
    "DataNotReady",
    "compute_market_score",
    "evaluate",
    "EntrySignal",
    "add_entry_features",
    "add_forward_outcomes",
    "cluster_episodes",
    "generate_signals",
]
