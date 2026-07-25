from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class StatisticalAnomalyResult:
    scores: np.ndarray
    normalized_scores: np.ndarray
    z_scores: pd.DataFrame


class StatisticalAnomalyDetector:
    """Detect statistical outliers using robust z-score analysis."""

    z_score_threshold: float = 3.0

    def detect(self, feature_matrix: pd.DataFrame) -> StatisticalAnomalyResult:
        numeric = feature_matrix.apply(pd.to_numeric, errors="coerce").fillna(0.0)
        medians = numeric.median()
        mad = (numeric - medians).abs().median().replace(0, 1.0)
        z_scores = (numeric - medians).abs() / (1.4826 * mad)
        row_scores = z_scores.max(axis=1).to_numpy(dtype=float)
        normalized_scores = np.clip((row_scores / self.z_score_threshold) * 100.0, 0.0, 100.0)
        return StatisticalAnomalyResult(
            scores=row_scores,
            normalized_scores=normalized_scores,
            z_scores=z_scores,
        )
