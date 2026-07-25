from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest


@dataclass(frozen=True)
class IsolationForestResult:
    scores: np.ndarray
    normalized_scores: np.ndarray
    model: IsolationForest


class IsolationForestDetector:
    """Primary unsupervised anomaly detector using Isolation Forest."""

    def __init__(
        self,
        contamination: float = 0.05,
        random_state: int = 42,
        n_estimators: int = 200,
    ) -> None:
        self.contamination = contamination
        self.random_state = random_state
        self.n_estimators = n_estimators
        self.model: IsolationForest | None = None

    def fit_predict(self, feature_matrix: pd.DataFrame) -> IsolationForestResult:
        self.model = IsolationForest(
            contamination=self.contamination,
            random_state=self.random_state,
            n_estimators=self.n_estimators,
        )
        self.model.fit(feature_matrix)
        raw_scores = -self.model.score_samples(feature_matrix)
        normalized_scores = self._normalize_scores(raw_scores)
        return IsolationForestResult(
            scores=raw_scores,
            normalized_scores=normalized_scores,
            model=self.model,
        )

    @staticmethod
    def _normalize_scores(raw_scores: np.ndarray) -> np.ndarray:
        minimum = float(np.min(raw_scores))
        maximum = float(np.max(raw_scores))
        if maximum == minimum:
            return np.zeros_like(raw_scores)
        scaled = (raw_scores - minimum) / (maximum - minimum)
        return np.clip(scaled * 100.0, 0.0, 100.0)
