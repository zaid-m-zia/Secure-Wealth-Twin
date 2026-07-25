from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import joblib
import pandas as pd
from sklearn.preprocessing import OneHotEncoder, RobustScaler

from ml.behavioral_intelligence.engine import BehavioralIntelligenceEngine
from ml.agentic_ai.engine import AgenticAIDecisionEngine
from ml.customer_behavior.engine import CustomerBehaviourEngine
from ml.digital_wealth_twin.engine import DigitalWealthTwinEngine
from ml.feature_engineering.engineer import FeatureEngineer
from ml.financial_decision_intelligence.engine import FinancialDecisionIntelligenceEngine
from ml.fraud_intelligence.engine import FraudIntelligenceEngine
from ml.preprocessing.cleaner import TransactionDataCleaner
from ml.preprocessing.loader import CSVTransactionLoader


@dataclass(frozen=True)
class PreprocessingRunResult:
    original_rows: int
    processed_rows: int
    customer_count: int
    engineered_feature_count: int
    memory_usage_bytes: int
    missing_values_remaining: int
    output_directory: Path


class CategoricalEncoder:
    """One-hot encode the categorical model inputs."""

    categorical_columns = ["gender", "location", "age_group", "preferred_time"]

    def __init__(self) -> None:
        self.encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
        self.feature_names_: list[str] = []

    def fit(self, frame: pd.DataFrame) -> "CategoricalEncoder":
        self.encoder.fit(self._prepare_frame(frame))
        self.feature_names_ = self.encoder.get_feature_names_out(self.categorical_columns).tolist()
        return self

    def transform(self, frame: pd.DataFrame) -> pd.DataFrame:
        encoded = self.encoder.transform(self._prepare_frame(frame))
        return pd.DataFrame(encoded, columns=self.feature_names_, index=frame.index)

    def fit_transform(self, frame: pd.DataFrame) -> pd.DataFrame:
        self.fit(frame)
        return self.transform(frame)

    @classmethod
    def _prepare_frame(cls, frame: pd.DataFrame) -> pd.DataFrame:
        prepared = frame.loc[:, cls.categorical_columns].astype("string").fillna("Unknown")
        return prepared.fillna("Unknown")


class RobustFeatureScaler:
    """Apply a RobustScaler to the numeric model inputs."""

    def __init__(self, numeric_columns: list[str]) -> None:
        self.numeric_columns = numeric_columns
        self.scaler = RobustScaler()

    def fit(self, frame: pd.DataFrame) -> "RobustFeatureScaler":
        self.scaler.fit(frame[self.numeric_columns])
        return self

    def transform(self, frame: pd.DataFrame) -> pd.DataFrame:
        transformed = frame.copy()
        transformed[self.numeric_columns] = self.scaler.transform(transformed[self.numeric_columns])
        return transformed

    def fit_transform(self, frame: pd.DataFrame) -> pd.DataFrame:
        self.fit(frame)
        return self.transform(frame)


class PreprocessingPipeline:
    """Run the full preprocessing and feature engineering workflow."""

    def __init__(self, source_path: str | Path, output_dir: str | Path, chunksize: int = 50_000) -> None:
        self.source_path = Path(source_path)
        self.output_dir = Path(output_dir)
        self.chunksize = chunksize
        self.loader = CSVTransactionLoader(self.source_path, chunksize=chunksize)
        self.cleaner = TransactionDataCleaner()
        self.engineer = FeatureEngineer()
        self.customer_behavior_engine = CustomerBehaviourEngine()
        self.behavioral_intelligence_engine = BehavioralIntelligenceEngine()
        self.fraud_intelligence_engine = FraudIntelligenceEngine()
        self.digital_wealth_twin_engine = DigitalWealthTwinEngine()
        self.financial_decision_intelligence_engine = FinancialDecisionIntelligenceEngine()
        self.agentic_ai_decision_engine = AgenticAIDecisionEngine()
        self.encoder = CategoricalEncoder()
        self.scaler: RobustFeatureScaler | None = None

    def run(self) -> PreprocessingRunResult:
        raw_frame = self.loader.load()
        original_rows = len(raw_frame)

        cleaned_frame = self.cleaner.clean(raw_frame)
        customer_features = self.customer_behavior_engine.build(cleaned_frame, self.output_dir)
        behavioral_result = self.behavioral_intelligence_engine.build(
            cleaned_frame,
            self.output_dir,
            customer_features=customer_features,
        )
        feature_result = self.engineer.build(cleaned_frame)
        engineered_frame = feature_result.dataframe

        fraud_result = self.fraud_intelligence_engine.build(
            engineered_frame,
            behavioral_result.normalized_features,
            self.output_dir,
            behavioral_numeric_columns=behavioral_result.numeric_columns,
        )

        fingerprint_frame = pd.read_parquet(self.output_dir / "financial_fingerprints.parquet")
        wealth_twin_result = self.digital_wealth_twin_engine.build(
            customer_features=customer_features,
            behavioral_features=behavioral_result.normalized_features,
            financial_fingerprints=fingerprint_frame,
            fraud_scores=fraud_result.fraud_scores,
            output_dir=self.output_dir,
        )
        financial_decision_result = self.financial_decision_intelligence_engine.build(
            customer_features=customer_features,
            behavioral_features=behavioral_result.normalized_features,
            fraud_scores=fraud_result.fraud_scores,
            wealth_twins=wealth_twin_result.twins,
            output_dir=self.output_dir,
        )
        self.agentic_ai_decision_engine.build(
            customer_features=customer_features,
            behavioral_features=behavioral_result.normalized_features,
            fraud_scores=fraud_result.fraud_scores,
            wealth_twins=wealth_twin_result.twins,
            financial_recommendations=financial_decision_result.recommendations,
            output_dir=self.output_dir,
        )

        encoded_frame = self.encoder.fit_transform(engineered_frame)
        processed_frame = pd.concat(
            [engineered_frame.reset_index(drop=True), encoded_frame.reset_index(drop=True)],
            axis=1,
        )

        binary_columns = [
            "weekend_flag",
            "large_transaction_flag",
            "very_large_transaction_flag",
            "rapid_transaction_flag",
            "new_customer_flag",
            "low_balance_flag",
            "high_spending_flag",
            "dormant_customer_flag",
        ]
        numeric_columns = [
            column
            for column in processed_frame.columns
            if column not in {"transaction_id", "customer_id", "customer_dob", "transaction_date", "transaction_timestamp"}
            and column not in binary_columns
            and pd.api.types.is_numeric_dtype(processed_frame[column])
        ]

        self.scaler = RobustFeatureScaler(numeric_columns)
        scaled_frame = self.scaler.fit_transform(processed_frame)

        model_feature_columns = numeric_columns + self.encoder.feature_names_ + binary_columns

        self.output_dir.mkdir(parents=True, exist_ok=True)
        processed_dataset_path = self.output_dir / "processed_dataset.parquet"
        processed_csv_path = self.output_dir / "processed_dataset.csv"
        encoder_path = self.output_dir / "encoder.pkl"
        scaler_path = self.output_dir / "scaler.pkl"
        feature_columns_path = self.output_dir / "feature_columns.json"

        scaled_frame.to_parquet(processed_dataset_path, index=False)
        scaled_frame.to_csv(processed_csv_path, index=False)
        joblib.dump(self.encoder, encoder_path)
        joblib.dump(self.scaler, scaler_path)
        with feature_columns_path.open("w", encoding="utf-8") as file_handle:
            json.dump(
                {
                    "feature_columns": model_feature_columns,
                    "numeric_columns": numeric_columns,
                    "encoded_columns": self.encoder.feature_names_,
                    "binary_columns": binary_columns,
                },
                file_handle,
                indent=2,
                sort_keys=True,
            )

        memory_usage_bytes = int(scaled_frame.memory_usage(deep=True).sum())
        missing_values_remaining = int(scaled_frame.isna().sum().sum())
        customer_count = int(scaled_frame["customer_id"].nunique())
        engineered_feature_count = len(feature_result.feature_columns)

        return PreprocessingRunResult(
            original_rows=original_rows,
            processed_rows=len(scaled_frame),
            customer_count=customer_count,
            engineered_feature_count=engineered_feature_count,
            memory_usage_bytes=memory_usage_bytes,
            missing_values_remaining=missing_values_remaining,
            output_directory=self.output_dir,
        )
