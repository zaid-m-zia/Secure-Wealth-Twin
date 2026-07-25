from __future__ import annotations

from typing import Any


class RecommendationRanker:
    """Rank recommendations so urgent, high-confidence actions appear first."""

    def rank(self, recommendations: list[dict[str, Any]]) -> list[dict[str, Any]]:
        ranked = sorted(
            recommendations,
            key=lambda item: (int(item.get("priority_score", 0)), float(item.get("confidence_score", 0.0))),
            reverse=True,
        )
        for rank, recommendation in enumerate(ranked, start=1):
            recommendation["rank"] = rank
        return ranked
