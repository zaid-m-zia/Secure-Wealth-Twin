from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import joblib
import pandas as pd

from ml.behavioral_intelligence.normalization import BehavioralFeatureNormalizer


@dataclass(frozen=True)
class BehavioralFeatureArtifacts:
    normalized_features_path: Path
    raw_features_path: Path
    fingerprints_path: Path
    feature_columns_path: Path
    scaler_path: Path


class BehavioralFeatureService:
    """Reusable service for loading and querying behavioral intelligence artifacts."""

    def __init__(self, artifact_dir: str | Path) -> None:
        self.artifact_dir = Path(artifact_dir)
        self.normalizer = BehavioralFeatureNormalizer()
        self._feature_columns: dict[str, list[str]] | None = None
        self._scaler: object | None = None

    @property
    def feature_columns(self) -> dict[str, list[str]]:
        if self._feature_columns is None:
            feature_columns_path = self.artifact_dir / "behavioral_feature_columns.json"
            with feature_columns_path.open("r", encoding="utf-8") as file_handle:
                self._feature_columns = json.load(file_handle)
        return self._feature_columns

    @property
    def scaler(self):
        if self._scaler is None:
            self._scaler = self.normalizer.load(self.artifact_dir / "behavioral_scaler.pkl")
        return self._scaler

    def load_normalized_features(self) -> pd.DataFrame:
        return pd.read_parquet(self.artifact_dir / "behavioral_intelligence_features.parquet")

    def load_raw_features(self) -> pd.DataFrame:
        return pd.read_parquet(self.artifact_dir / "behavioral_intelligence_features_raw.parquet")

    def load_fingerprints(self) -> pd.DataFrame:
        return pd.read_parquet(self.artifact_dir / "financial_fingerprints.parquet")

    def get_customer_features(self, customer_id: str) -> pd.Series | None:
        features = self.load_normalized_features()
        matches = features.loc[features["customer_id"] == customer_id]
        if matches.empty:
            return None
        return matches.iloc[0]

    def get_customer_fingerprint(self, customer_id: str) -> pd.Series | None:
        fingerprints = self.load_fingerprints()
        matches = fingerprints.loc[fingerprints["customer_id"] == customer_id]
        if matches.empty:
            return None
        return matches.iloc[0]

    def merge_with_customer_features(self, customer_features: pd.DataFrame) -> pd.DataFrame:
        normalized = self.load_normalized_features()
        return customer_features.merge(normalized, on="customer_id", how="left")

    def transform_new_features(self, raw_features: pd.DataFrame) -> pd.DataFrame:
        numeric_columns = self.feature_columns["numeric_columns"]
        return self.normalizer.transform(raw_features, self.scaler, numeric_columns)
