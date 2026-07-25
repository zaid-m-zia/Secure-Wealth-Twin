from __future__ import annotations

from typing import Any

import pandas as pd


class ExplainableReasoningEngine:
    """Build transparent, deterministic reasoning chains and decision summaries."""

    def build_reasoning_chain(
        self,
        customer: pd.Series,
        escalation: dict[str, Any],
        actions: list[dict[str, Any]],
    ) -> list[str]:
        health = float(customer.get("financial_health_score", 0.0))
        behaviour = str(customer.get("behaviour_profile", "Unknown"))
        chain = [
            f"Customer behaviour profile is {behaviour}.",
            f"Digital Wealth Twin financial health score is {health:.1f}/100.",
            f"Fraud assessment: {escalation['reason']}",
        ]
        if actions:
            chain.append("Conflicting recommendations were resolved with fraud safety and liquidity needs first.")
            chain.append("Selected actions: " + "; ".join(str(action["recommendation"]) for action in actions) + ".")
        else:
            chain.append("No additional financial action was selected until the fraud review is completed.")
        return chain

    @staticmethod
    def supporting_evidence(customer: pd.Series) -> dict[str, object]:
        return {
            "behaviour_profile": str(customer.get("behaviour_profile", "Unknown")),
            "financial_health_score": round(float(customer.get("financial_health_score", 0.0)), 2),
            "investment_readiness": round(float(customer.get("investment_readiness", 0.0)), 2),
            "emergency_preparedness": round(float(customer.get("emergency_preparedness", 0.0)), 2),
            "maximum_fraud_score": round(float(customer.get("agentic_maximum_fraud_score", 0.0)), 2),
            "average_fraud_score": round(float(customer.get("agentic_average_fraud_score", 0.0)), 2),
            "income_stability_score": round(float(customer.get("income_stability_score", 0.0)), 4),
        }

    @staticmethod
    def risk_summary(customer: pd.Series, escalation: dict[str, Any]) -> dict[str, object]:
        return {
            "escalated": bool(escalation["escalated"]),
            "risk_priority": str(escalation["priority"]),
            "maximum_fraud_score": round(float(customer.get("agentic_maximum_fraud_score", 0.0)), 2),
            "average_fraud_score": round(float(customer.get("agentic_average_fraud_score", 0.0)), 2),
            "flagged_transactions": int(customer.get("agentic_flagged_transactions", 0)),
        }

    @staticmethod
    def financial_summary(customer: pd.Series) -> dict[str, object]:
        return {
            "financial_health_score": round(float(customer.get("financial_health_score", 0.0)), 2),
            "emergency_preparedness": round(float(customer.get("emergency_preparedness", 0.0)), 2),
            "debt_pressure_estimate": round(float(customer.get("debt_pressure_estimate", 0.0)), 2),
            "investment_readiness": round(float(customer.get("investment_readiness", 0.0)), 2),
            "spending_capacity": round(float(customer.get("spending_capacity", 0.0)), 2),
        }
