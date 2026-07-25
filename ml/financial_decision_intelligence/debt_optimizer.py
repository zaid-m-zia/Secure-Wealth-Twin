from __future__ import annotations

from typing import Any

import pandas as pd


class DebtOptimizer:
    """Recommend debt reduction when the wealth twin signals financial pressure."""

    def recommend(self, customer: pd.Series) -> list[dict[str, Any]]:
        debt_pressure = float(customer.get("debt_pressure_estimate", 0.0))
        balance_utilisation = float(customer.get("balance_utilisation", 0.0))
        expense_ratio = float(customer.get("expense_ratio", 0.0))
        if debt_pressure >= 50.0:
            return [{
                "recommendation_type": "debt_reduction",
                "recommendation": "Prioritize a debt reduction strategy",
                "confidence_score": min(0.94, 0.60 + debt_pressure / 250.0),
                "priority": "Critical" if debt_pressure >= 75.0 else "High",
                "explanation": (
                    f"Debt pressure is estimated at {debt_pressure:.1f}/100. Direct surplus cash to the highest-cost "
                    "debt first while maintaining minimum payments on all obligations."
                ),
                "supporting_metrics": {
                    "debt_pressure_estimate": round(debt_pressure, 2),
                    "balance_utilisation": round(balance_utilisation, 4),
                    "expense_ratio": round(expense_ratio, 4),
                },
            }]
        return []
