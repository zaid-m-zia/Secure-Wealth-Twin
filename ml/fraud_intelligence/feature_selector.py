from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class FraudFeatureSelectionResult:
    feature_columns: list[str]
    transaction_columns: list[str]
    behavioral_columns: list[str]


class FraudFeatureSelector:
    """Select numeric features for unsupervised fraud analysis."""

    preferred_transaction_columns = [
        "transaction_amount",
        "log_transaction_amount",
        "transaction_balance_ratio",
        "balance_after_transaction",
        "age",
        "transaction_hour",
        "day_of_week",
        "average_transaction_amount",
        "std_transaction_amount",
        "transaction_frequency",
        "large_transaction_flag",
        "very_large_transaction_flag",
        "rapid_transaction_flag",
        "low_balance_flag",
        "high_spending_flag",
        "new_customer_flag",
        "dormant_customer_flag",
        "weekend_flag",
    ]

    preferred_behavioral_columns = [
        "spending_velocity",
        "spending_volatility_index",
        "income_stability_score",
        "cash_flow_volatility",
        "cash_flow_direction_score",
        "category_top_location_share",
        "category_amount_entropy",
        "timing_peak_concentration",
        "timing_night_activity_score",
        "weekday_weekend_amount_ratio",
        "monthly_spending_volatility",
        "monthly_trend_strength",
        "financial_fingerprint_magnitude",
    ]

    def __init__(self, max_features: int = 32) -> None:
        self.max_features = max_features

    def select(
        self,
        transaction_frame: pd.DataFrame,
        behavioral_columns: list[str] | None = None,
    ) -> FraudFeatureSelectionResult:
        behavioral_candidates = behavioral_columns or [
            column
            for column in self.preferred_behavioral_columns
            if column in transaction_frame.columns and pd.api.types.is_numeric_dtype(transaction_frame[column])
        ]
        transaction_candidates = [
            column
            for column in self.preferred_transaction_columns
            if column in transaction_frame.columns and pd.api.types.is_numeric_dtype(transaction_frame[column])
        ]

        selected = list(dict.fromkeys(transaction_candidates + behavioral_candidates))
        if len(selected) > self.max_features:
            variances = transaction_frame[selected].fillna(0.0).var(ddof=0)
            selected = variances.sort_values(ascending=False).head(self.max_features).index.tolist()

        return FraudFeatureSelectionResult(
            feature_columns=selected,
            transaction_columns=[column for column in selected if column in transaction_candidates],
            behavioral_columns=[column for column in selected if column in behavioral_candidates],
        )

    def build_matrix(self, frame: pd.DataFrame, feature_columns: list[str]) -> pd.DataFrame:
        matrix = frame[feature_columns].apply(pd.to_numeric, errors="coerce").fillna(0.0)
        return matrix.astype(float)
