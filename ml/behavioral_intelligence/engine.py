from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from ml.behavioral_intelligence.cash_flow_trends import CashFlowTrendAnalyzer
from ml.behavioral_intelligence.category_frequency import CategoryFrequencyAnalyzer
from ml.behavioral_intelligence.financial_fingerprint import FinancialFingerprintBuilder
from ml.behavioral_intelligence.income_stability import IncomeStabilityAnalyzer
from ml.behavioral_intelligence.monthly_trends import MonthlyTrendAnalyzer
from ml.behavioral_intelligence.normalization import BehavioralFeatureNormalizer
from ml.behavioral_intelligence.spending_patterns import SpendingPatternAnalyzer
from ml.behavioral_intelligence.transaction_context import TransactionContextBuilder
from ml.behavioral_intelligence.transaction_timing import TransactionTimingAnalyzer
from ml.behavioral_intelligence.weekday_weekend import WeekdayWeekendAnalyzer


@dataclass(frozen=True)
class BehavioralIntelligenceResult:
    raw_features: pd.DataFrame
    normalized_features: pd.DataFrame
    fingerprints: pd.DataFrame
    feature_columns: list[str]
    numeric_columns: list[str]
    fingerprint_columns: list[str]
    customer_count: int
    output_directory: Path


class BehavioralIntelligenceEngine:
    """Orchestrate financial behavior intelligence feature generation."""

    def __init__(self) -> None:
        self.context_builder = TransactionContextBuilder()
        self.spending_pattern_analyzer = SpendingPatternAnalyzer()
        self.income_stability_analyzer = IncomeStabilityAnalyzer()
        self.cash_flow_analyzer = CashFlowTrendAnalyzer()
        self.category_frequency_analyzer = CategoryFrequencyAnalyzer()
        self.transaction_timing_analyzer = TransactionTimingAnalyzer()
        self.weekday_weekend_analyzer = WeekdayWeekendAnalyzer()
        self.monthly_trend_analyzer = MonthlyTrendAnalyzer()
        self.fingerprint_builder = FinancialFingerprintBuilder()
        self.normalizer = BehavioralFeatureNormalizer()

    def build(
        self,
        frame: pd.DataFrame,
        output_dir: str | Path,
        customer_features: pd.DataFrame | None = None,
    ) -> BehavioralIntelligenceResult:
        context = self.context_builder.build(frame)
        feature_frames = [
            self.spending_pattern_analyzer.build(context),
            self.income_stability_analyzer.build(context),
            self.cash_flow_analyzer.build(context),
            self.category_frequency_analyzer.build(context),
            self.transaction_timing_analyzer.build(context),
            self.weekday_weekend_analyzer.build(context),
            self.monthly_trend_analyzer.build(context),
        ]

        raw_features = feature_frames[0]
        for feature_frame in feature_frames[1:]:
            raw_features = raw_features.merge(feature_frame, on="customer_id", how="outer")

        if customer_features is not None:
            merge_columns = [
                column
                for column in customer_features.columns
                if column not in raw_features.columns and column != "customer_id"
            ]
            if merge_columns:
                raw_features = raw_features.merge(
                    customer_features[["customer_id", *merge_columns]],
                    on="customer_id",
                    how="left",
                )

        fingerprint_result = self.fingerprint_builder.build(raw_features)
        raw_features = raw_features.merge(
            fingerprint_result.dataframe[
                [
                    "customer_id",
                    "financial_fingerprint_vector",
                    "financial_fingerprint_signature",
                    "financial_fingerprint_magnitude",
                ]
            ],
            on="customer_id",
            how="left",
        )

        normalization_result = self.normalizer.fit_transform(raw_features)
        normalized_features = normalization_result.normalized_frame

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        raw_features_path = output_path / "behavioral_intelligence_features_raw.parquet"
        normalized_features_path = output_path / "behavioral_intelligence_features.parquet"
        fingerprints_path = output_path / "financial_fingerprints.parquet"
        feature_columns_path = output_path / "behavioral_feature_columns.json"
        scaler_path = output_path / "behavioral_scaler.pkl"

        raw_features.to_parquet(raw_features_path, index=False)
        normalized_features.to_parquet(normalized_features_path, index=False)
        fingerprint_result.dataframe.to_parquet(fingerprints_path, index=False)
        self.normalizer.save(normalization_result.scaler, scaler_path)

        feature_columns = [
            column
            for column in raw_features.columns
            if column
            not in {
                "customer_id",
                "financial_fingerprint_vector",
                "financial_fingerprint_signature",
            }
        ]
        with feature_columns_path.open("w", encoding="utf-8") as file_handle:
            json.dump(
                {
                    "feature_columns": feature_columns,
                    "numeric_columns": normalization_result.numeric_columns,
                    "fingerprint_columns": fingerprint_result.fingerprint_columns,
                },
                file_handle,
                indent=2,
                sort_keys=True,
            )

        return BehavioralIntelligenceResult(
            raw_features=raw_features,
            normalized_features=normalized_features,
            fingerprints=fingerprint_result.dataframe,
            feature_columns=feature_columns,
            numeric_columns=normalization_result.numeric_columns,
            fingerprint_columns=fingerprint_result.fingerprint_columns,
            customer_count=int(raw_features["customer_id"].nunique()),
            output_directory=output_path,
        )
