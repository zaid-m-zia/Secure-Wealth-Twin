from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class BehaviourStatistics:
    """Reusable statistical helpers for customer behaviour aggregation."""

    @staticmethod
    def safe_mode(series: pd.Series, default: object = "Unknown") -> object:
        non_null = series.dropna()
        if non_null.empty:
            return default
        modes = non_null.mode()
        if modes.empty:
            return non_null.iloc[0]
        return modes.iloc[0]

    @staticmethod
    def safe_std(series: pd.Series) -> float:
        numeric = pd.to_numeric(series, errors="coerce").dropna()
        if len(numeric) <= 1:
            return 0.0
        return float(numeric.std(ddof=0))

    @staticmethod
    def safe_mean(series: pd.Series) -> float:
        numeric = pd.to_numeric(series, errors="coerce").dropna()
        if numeric.empty:
            return 0.0
        return float(numeric.mean())

    @staticmethod
    def coefficient_of_variation(series: pd.Series) -> float:
        numeric = pd.to_numeric(series, errors="coerce").dropna()
        if len(numeric) <= 1:
            return 0.0
        mean_value = float(numeric.mean())
        if mean_value == 0:
            return 0.0
        return float(numeric.std(ddof=0) / abs(mean_value))

    @staticmethod
    def ratio(numerator: float, denominator: float) -> float:
        if denominator == 0 or pd.isna(denominator):
            return 0.0
        return float(numerator / denominator)

    @staticmethod
    def normalized_inverse(value: float) -> float:
        if pd.isna(value):
            return 0.0
        return float(1.0 / (1.0 + max(value, 0.0)))

    @staticmethod
    def percentile_rank(values: Iterable[float], threshold: float) -> float:
        array = np.asarray(list(values), dtype=float)
        if array.size == 0:
            return 0.0
        return float(np.mean(array <= threshold))