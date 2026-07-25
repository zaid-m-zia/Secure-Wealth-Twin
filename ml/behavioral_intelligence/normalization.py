from __future__ import annotations

from dataclasses import dataclass

import joblib
import pandas as pd
from sklearn.preprocessing import RobustScaler


@dataclass(frozen=True)
class BehavioralNormalizationResult:
    normalized_frame: pd.DataFrame
    raw_frame: pd.DataFrame
    numeric_columns: list[str]
    scaler: RobustScaler


class BehavioralFeatureNormalizer:
    """Normalize behavioral intelligence features for downstream ML use."""

    identifier_columns = {"customer_id", "financial_fingerprint_vector", "financial_fingerprint_signature"}

    def fit_transform(self, frame: pd.DataFrame) -> BehavioralNormalizationResult:
        numeric_columns = self._select_numeric_columns(frame)
        scaler = RobustScaler()
        normalized = frame.copy()
        normalized[numeric_columns] = scaler.fit_transform(frame[numeric_columns].fillna(0.0))
        return BehavioralNormalizationResult(
            normalized_frame=normalized,
            raw_frame=frame,
            numeric_columns=numeric_columns,
            scaler=scaler,
        )

    def transform(self, frame: pd.DataFrame, scaler: RobustScaler, numeric_columns: list[str]) -> pd.DataFrame:
        normalized = frame.copy()
        normalized[numeric_columns] = scaler.transform(frame[numeric_columns].fillna(0.0))
        return normalized

    def save(self, scaler: RobustScaler, path: str) -> None:
        joblib.dump(scaler, path)

    @classmethod
    def load(cls, path: str) -> RobustScaler:
        return joblib.load(path)

    def _select_numeric_columns(self, frame: pd.DataFrame) -> list[str]:
        return [
            column
            for column in frame.columns
            if column not in self.identifier_columns
            and pd.api.types.is_numeric_dtype(frame[column])
        ]
