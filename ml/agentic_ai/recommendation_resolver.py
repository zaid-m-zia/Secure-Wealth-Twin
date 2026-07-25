from __future__ import annotations

from typing import Any


class RecommendationConflictResolver:
    """Resolve incompatible advice according to financial safety and liquidity rules."""

    blocked_during_escalation = {"investment_readiness", "budget_allocation"}
    liquidity_first_types = {"emergency_fund", "debt_reduction"}

    def resolve(self, recommendations: list[dict[str, Any]], fraud_escalated: bool) -> list[dict[str, Any]]:
        selected: list[dict[str, Any]] = []
        liquidity_first = any(item.get("recommendation_type") in self.liquidity_first_types for item in recommendations)
        for recommendation in recommendations:
            recommendation_type = str(recommendation.get("recommendation_type", ""))
            if fraud_escalated and recommendation_type in self.blocked_during_escalation:
                continue
            if liquidity_first and recommendation_type == "investment_readiness":
                continue
            selected.append(recommendation)
            if len(selected) == 3:
                break
        return selected
