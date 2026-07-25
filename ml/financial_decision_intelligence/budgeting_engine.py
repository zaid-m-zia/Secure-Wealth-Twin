from __future__ import annotations

from typing import Any

import pandas as pd


class BudgetingEngine:
    """Recommend a monthly allocation using observed spending capacity."""

    def recommend(self, customer: pd.Series) -> list[dict[str, Any]]:
        monthly_spending = float(customer.get("average_monthly_spending", 0.0))
        estimated_income = float(customer.get("estimated_monthly_salary", 0.0))
        expense_ratio = float(customer.get("expense_ratio", 0.0))
        spending_capacity = float(customer.get("spending_capacity", 0.0))
        discretionary_target = 25.0 if expense_ratio >= 0.60 else 30.0
        savings_target = 20.0 if expense_ratio >= 0.60 else 15.0
        return [{
            "recommendation_type": "budget_allocation",
            "recommendation": "Adopt a monthly budget allocation",
            "confidence_score": 0.78,
            "priority": "Medium" if expense_ratio >= 0.60 else "Low",
            "explanation": (
                f"Observed monthly spending is {monthly_spending:.2f} against estimated monthly income of "
                f"{estimated_income:.2f}. Allocate 50% to essentials, {discretionary_target:.0f}% to discretionary "
                f"spending, {savings_target:.0f}% to savings and investments, and the remainder to a buffer."
            ),
            "supporting_metrics": {
                "average_monthly_spending": round(monthly_spending, 2),
                "estimated_monthly_salary": round(estimated_income, 2),
                "expense_ratio": round(expense_ratio, 4),
                "spending_capacity": round(spending_capacity, 2),
                "recommended_savings_percent": savings_target,
            },
        }]
