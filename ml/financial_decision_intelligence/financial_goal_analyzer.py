from __future__ import annotations

from typing import Any

import pandas as pd


class FinancialGoalAnalyzer:
    """Identify the primary financial-health improvement opportunity."""

    def analyze(self, customer: pd.Series) -> list[dict[str, Any]]:
        health_score = float(customer.get("financial_health_score", 0.0))
        fraud_score = float(customer.get("customer_avg_fraud_score", 0.0))
        if health_score < 65.0:
            return [{
                "recommendation_type": "financial_health_improvement",
                "recommendation": "Improve overall financial health",
                "confidence_score": min(0.95, 0.60 + (65.0 - health_score) / 100.0),
                "priority": "High" if health_score < 45.0 else "Medium",
                "explanation": (
                    f"Financial health is {health_score:.1f}/100. Strengthening savings, spending discipline, "
                    "and cash reserves should be the immediate goal."
                ),
                "supporting_metrics": {
                    "financial_health_score": round(health_score, 2),
                    "average_fraud_score": round(fraud_score, 2),
                },
            }]
        return [{
            "recommendation_type": "financial_goal_maintenance",
            "recommendation": "Maintain your current financial health progress",
            "confidence_score": 0.72,
            "priority": "Low",
            "explanation": f"Financial health is {health_score:.1f}/100; preserve the habits that support this score.",
            "supporting_metrics": {"financial_health_score": round(health_score, 2)},
        }]
