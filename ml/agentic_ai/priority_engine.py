from __future__ import annotations


class AgenticPriorityEngine:
    """Determine a final customer-level priority from safety and financial signals."""

    priority_scores = {"Low": 1, "Medium": 2, "High": 3, "Critical": 4}

    def determine(self, fraud_priority: str, recommendations: list[dict[str, object]]) -> str:
        highest = self.priority_scores.get(fraud_priority, 1)
        for recommendation in recommendations:
            highest = max(highest, self.priority_scores.get(str(recommendation.get("priority", "Low")), 1))
        return next(label for label, score in self.priority_scores.items() if score == highest)
