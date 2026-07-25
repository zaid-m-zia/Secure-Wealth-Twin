from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class BehaviorDeviationResult:
    scores: np.ndarray
    normalized_scores: np.ndarray


class BehaviorDeviationCalculator:
    """Measure deviation of a transaction from the customer's behavioral baseline."""

    def calculate(self, frame: pd.DataFrame) -> BehaviorDeviationResult:
        amount_baseline = frame["average_transaction_amount"].replace(0, np.nan)
        amount_ratio = (frame["transaction_amount"] / amount_baseline).fillna(1.0)
        amount_deviation = (amount_ratio - 1.0).abs()

        preferred_hour = frame.get("preferred_transaction_hour", frame.get("timing_peak_hour", pd.Series(12, index=frame.index)))
        hour_deviation = (frame["transaction_hour"] - preferred_hour).abs() / 12.0

        balance_ratio = frame.get("transaction_balance_ratio", pd.Series(0.0, index=frame.index)).fillna(0.0)
        spending_volatility = frame.get("spending_volatility_index", pd.Series(0.0, index=frame.index)).fillna(0.0)

        combined = (
            amount_deviation.fillna(0.0) * 0.45
            + hour_deviation.fillna(0.0) * 0.20
            + balance_ratio.clip(0.0, 1.0) * 0.20
            + spending_volatility.fillna(0.0) * 0.15
        )
        normalized_scores = np.clip(combined.to_numpy(dtype=float) * 100.0, 0.0, 100.0)
        return BehaviorDeviationResult(
            scores=combined.to_numpy(dtype=float),
            normalized_scores=normalized_scores,
        )


@dataclass(frozen=True)
class FinancialDnaDistanceResult:
    scores: np.ndarray
    normalized_scores: np.ndarray


class FinancialDnaDistanceCalculator:
    """Estimate distance from the customer's financial fingerprint baseline."""

    fingerprint_columns = [
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
    ]

    def calculate(self, frame: pd.DataFrame) -> FinancialDnaDistanceResult:
        available_columns = [column for column in self.fingerprint_columns if column in frame.columns]
        if not available_columns:
            zeros = np.zeros(len(frame), dtype=float)
            return FinancialDnaDistanceResult(scores=zeros, normalized_scores=zeros)

        profile = frame[available_columns].apply(pd.to_numeric, errors="coerce").fillna(0.0)
        transaction_vector = pd.DataFrame(index=frame.index)
        amount_ratio = (
            frame["transaction_amount"] / frame["average_transaction_amount"].replace(0, np.nan)
        ).fillna(1.0)
        balance_ratio = frame.get("transaction_balance_ratio", pd.Series(0.0, index=frame.index)).fillna(0.0)
        hour_ratio = frame["transaction_hour"] / 24.0

        for column in available_columns:
            if "spending" in column:
                transaction_vector[column] = amount_ratio
            elif "timing" in column or "night" in column:
                transaction_vector[column] = hour_ratio
            elif "cash_flow" in column or "balance" in column or "income" in column:
                transaction_vector[column] = balance_ratio
            elif "weekday" in column or "weekend" in column:
                transaction_vector[column] = frame.get("weekend_flag", pd.Series(0.0, index=frame.index)).fillna(0.0)
            elif "category" in column:
                transaction_vector[column] = 1.0 - frame.get("category_top_location_share", pd.Series(0.0, index=frame.index)).fillna(0.0)
            else:
                transaction_vector[column] = amount_ratio * 0.5 + balance_ratio * 0.5

        profile_values = profile.to_numpy(dtype=float)
        signal_values = transaction_vector.to_numpy(dtype=float)
        profile_norm = np.linalg.norm(profile_values, axis=1)
        profile_norm = np.where(profile_norm == 0, 1.0, profile_norm)
        signal_norm = np.linalg.norm(signal_values, axis=1)
        signal_norm = np.where(signal_norm == 0, 1.0, signal_norm)
        dot_product = (profile_values * signal_values).sum(axis=1)
        cosine_similarity = dot_product / (profile_norm * signal_norm)
        distance = 1.0 - np.clip(cosine_similarity, -1.0, 1.0)
        normalized_scores = np.clip(distance * 100.0, 0.0, 100.0)
        return FinancialDnaDistanceResult(scores=distance, normalized_scores=normalized_scores)


@dataclass(frozen=True)
class FraudScoreFusionResult:
    fraud_scores: np.ndarray
    component_scores: pd.DataFrame


class FraudScoreFusion:
    """Fuse component scores into a final 0-100 fraud score."""

    weights = {
        "isolation_forest_score": 0.30,
        "behavior_deviation_score": 0.20,
        "financial_dna_distance_score": 0.20,
        "rule_based_score": 0.15,
        "statistical_outlier_score": 0.15,
    }

    def fuse(self, component_scores: pd.DataFrame) -> FraudScoreFusionResult:
        fused = np.zeros(len(component_scores), dtype=float)
        for column, weight in self.weights.items():
            if column in component_scores.columns:
                fused += component_scores[column].to_numpy(dtype=float) * weight
        fused = np.clip(fused, 0.0, 100.0)
        return FraudScoreFusionResult(fraud_scores=fused, component_scores=component_scores)


class RiskLevelClassifier:
    """Map fraud scores to risk bands."""

    bands = (
        (81.0, "Critical"),
        (61.0, "High"),
        (31.0, "Medium"),
        (0.0, "Low"),
    )

    def classify(self, fraud_scores: np.ndarray) -> pd.Series:
        labels: list[str] = []
        for score in fraud_scores:
            labels.append(self._classify_score(float(score)))
        return pd.Series(labels)

    def _classify_score(self, score: float) -> str:
        for threshold, label in self.bands:
            if score >= threshold:
                return label
        return "Low"
