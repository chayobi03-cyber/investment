"""Investment data pipeline V1.

Stages are intentionally explicit:
raw source rows -> completeness gate -> raw factors -> point-in-time normalization.
"""

from .pipeline import build_factor_dataset

__all__ = ["build_factor_dataset"]
