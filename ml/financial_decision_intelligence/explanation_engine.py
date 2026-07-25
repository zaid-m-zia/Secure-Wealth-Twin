from __future__ import annotations

from typing import Any


class DecisionExplanationEngine:
    """Validate a consistent, explainable recommendation contract."""

    required_fields = {"recommendation", "confidence_score", "priority", "explanation", "supporting_metrics"}

    def finalize(self, recommendation: dict[str, Any]) -> dict[str, Any]:
        missing = self.required_fields.difference(recommendation)
        if missing:
            raise ValueError(f"Recommendation is missing required fields: {sorted(missing)}")
        recommendation["confidence_score"] = round(min(max(float(recommendation["confidence_score"]), 0.0), 1.0), 2)
        if not isinstance(recommendation["supporting_metrics"], dict):
            raise ValueError("supporting_metrics must be a dictionary")
        if not str(recommendation["explanation"]).strip():
            raise ValueError("explanation must not be empty")
        return recommendation
