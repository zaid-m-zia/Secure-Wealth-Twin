from __future__ import annotations

import pandas as pd


class DecisionConfidenceScorer:
    """Calculate a bounded confidence score from source coverage and decision evidence."""

    coverage_columns = [
        "financial_health_score",
        "agentic_average_fraud_score",
        "income_stability_score",
        "behaviour_profile",
    ]

    def score(self, customer: pd.Series, action_confidences: list[float], escalation_confidence: float) -> float:
        coverage = sum(column in customer.index and pd.notna(customer[column]) for column in self.coverage_columns)
        coverage_score = coverage / len(self.coverage_columns)
        action_score = sum(action_confidences) / len(action_confidences) if action_confidences else 0.60
        confidence = coverage_score * 0.25 + action_score * 0.45 + escalation_confidence * 0.30
        return round(min(max(confidence, 0.0), 1.0), 2)
