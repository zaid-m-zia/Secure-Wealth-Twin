from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from ml.fraud_intelligence.isolation_forest import IsolationForestDetector, IsolationForestResult
from ml.fraud_intelligence.statistical_detector import StatisticalAnomalyDetector, StatisticalAnomalyResult


@dataclass(frozen=True)
class AnomalyDetectionResult:
    isolation_forest: IsolationForestResult
    statistical: StatisticalAnomalyResult


class AnomalyDetector:
    """Coordinate unsupervised anomaly detection methods."""

    def __init__(self) -> None:
        self.isolation_forest = IsolationForestDetector()
        self.statistical_detector = StatisticalAnomalyDetector()

    def detect(self, feature_matrix: pd.DataFrame) -> AnomalyDetectionResult:
        isolation_result = self.isolation_forest.fit_predict(feature_matrix)
        statistical_result = self.statistical_detector.detect(feature_matrix)
        return AnomalyDetectionResult(
            isolation_forest=isolation_result,
            statistical=statistical_result,
        )
