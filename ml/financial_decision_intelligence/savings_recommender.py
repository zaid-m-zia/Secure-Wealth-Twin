from __future__ import annotations

from typing import Any

import pandas as pd


class SavingsRecommender:
    """Generate savings and emergency-fund recommendations."""

    def recommend(self, customer: pd.Series) -> list[dict[str, Any]]:
        monthly_spending = max(float(customer.get("average_monthly_spending", 0.0)), 0.0)
        emergency_preparedness = float(customer.get("emergency_preparedness", 0.0))
        savings_tendency = float(customer.get("savings_tendency", 0.0))
        average_balance = max(float(customer.get("average_account_balance", 0.0)), 0.0)
        target_fund = monthly_spending * 6.0
        shortfall = max(target_fund - average_balance, 0.0)
        monthly_saving = max(shortfall / 12.0, monthly_spending * 0.10)
        if emergency_preparedness < 100.0:
            return [{
                "recommendation_type": "emergency_fund",
                "recommendation": "Build a six-month emergency fund",
                "confidence_score": min(0.96, 0.70 + (100.0 - emergency_preparedness) / 300.0),
                "priority": "Critical" if emergency_preparedness < 35.0 else "High",
                "explanation": (
                    f"Current balances cover about {emergency_preparedness * 0.06:.1f} months of typical spending. "
                    f"Aim for an emergency reserve of {target_fund:.2f} and automate at least {monthly_saving:.2f} monthly."
                ),
                "supporting_metrics": {
                    "emergency_preparedness": round(emergency_preparedness, 2),
                    "average_monthly_spending": round(monthly_spending, 2),
                    "average_account_balance": round(average_balance, 2),
                    "emergency_fund_target": round(target_fund, 2),
                    "estimated_emergency_fund_shortfall": round(shortfall, 2),
                    "recommended_monthly_saving": round(monthly_saving, 2),
                    "savings_tendency": round(savings_tendency, 2),
                },
            }]
        return [{
            "recommendation_type": "savings_maintenance",
            "recommendation": "Continue automated monthly savings",
            "confidence_score": 0.76,
            "priority": "Low",
            "explanation": "Emergency preparedness is strong; maintain automatic savings to preserve the reserve.",
            "supporting_metrics": {"emergency_preparedness": round(emergency_preparedness, 2)},
        }]
