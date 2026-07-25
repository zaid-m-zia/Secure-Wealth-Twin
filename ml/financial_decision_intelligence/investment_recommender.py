from __future__ import annotations

from typing import Any

import pandas as pd


class InvestmentRecommender:
    """Assess whether foundational financial conditions support investing."""

    def recommend(self, customer: pd.Series) -> list[dict[str, Any]]:
        readiness = float(customer.get("investment_readiness", 0.0))
        emergency_preparedness = float(customer.get("emergency_preparedness", 0.0))
        debt_pressure = float(customer.get("debt_pressure_estimate", 0.0))
        risk_tolerance = float(customer.get("risk_tolerance_estimate", 0.0))
        ready = readiness >= 60.0 and emergency_preparedness >= 70.0 and debt_pressure < 50.0
        if ready:
            return [{
                "recommendation_type": "investment_readiness",
                "recommendation": "Start a diversified investment plan",
                "confidence_score": min(0.92, 0.65 + readiness / 300.0),
                "priority": "Medium",
                "explanation": (
                    f"Investment readiness is {readiness:.1f}/100 with emergency preparedness at "
                    f"{emergency_preparedness:.1f}/100. Use diversified, risk-appropriate investments rather than "
                    "concentrated positions."
                ),
                "supporting_metrics": {
                    "investment_readiness": round(readiness, 2),
                    "emergency_preparedness": round(emergency_preparedness, 2),
                    "debt_pressure_estimate": round(debt_pressure, 2),
                    "risk_tolerance_estimate": round(risk_tolerance, 2),
                },
            }]
        return [{
            "recommendation_type": "investment_readiness",
            "recommendation": "Strengthen cash reserves before increasing investments",
            "confidence_score": 0.81,
            "priority": "High" if emergency_preparedness < 50.0 or debt_pressure >= 60.0 else "Medium",
            "explanation": (
                "Investment readiness is limited by cash-reserve or debt conditions. Prioritize an emergency fund and "
                "lower financial pressure before taking additional investment risk."
            ),
            "supporting_metrics": {
                "investment_readiness": round(readiness, 2),
                "emergency_preparedness": round(emergency_preparedness, 2),
                "debt_pressure_estimate": round(debt_pressure, 2),
                "risk_tolerance_estimate": round(risk_tolerance, 2),
            },
        }]
