from __future__ import annotations

from typing import Any


class FinancialPriorityEngine:
    """Assign an actionable priority from financial risk and recommendation type."""

    priority_weights = {"Low": 1, "Medium": 2, "High": 3, "Critical": 4}
    protected_types = {"emergency_fund", "debt_reduction"}

    def prioritize(self, recommendations: list[dict[str, Any]]) -> list[dict[str, Any]]:
        for recommendation in recommendations:
            metrics = recommendation.get("supporting_metrics", {})
            fraud_score = float(metrics.get("average_fraud_score", 0.0))
            priority = str(recommendation.get("priority", "Low"))
            if fraud_score >= 61.0 and recommendation.get("recommendation_type") in self.protected_types:
                priority = "Critical"
            recommendation["priority"] = priority
            recommendation["priority_score"] = self.priority_weights[priority]
        return recommendations
