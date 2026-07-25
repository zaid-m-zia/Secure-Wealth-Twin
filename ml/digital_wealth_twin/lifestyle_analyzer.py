from __future__ import annotations

import pandas as pd


class LifestyleAnalyzer:
    """Classify customer lifestyle based on spending and balance patterns."""

    def build(self, state: pd.DataFrame) -> pd.DataFrame:
        working = state.copy()
        average_balance = working.get("average_account_balance", 0.0)
        monthly_spending = working.get("average_monthly_spending", 0.0)

        balance_thresholds = {
            "essential": float(average_balance.quantile(0.25)),
            "moderate": float(average_balance.quantile(0.50)),
            "comfortable": float(average_balance.quantile(0.75)),
        }
        spending_thresholds = {
            "essential": float(monthly_spending.quantile(0.25)),
            "moderate": float(monthly_spending.quantile(0.50)),
            "comfortable": float(monthly_spending.quantile(0.75)),
        }

        categories: list[str] = []
        for _, row in working.iterrows():
            categories.append(
                self._classify_lifestyle(
                    float(row.get("average_account_balance", 0.0)),
                    float(row.get("average_monthly_spending", 0.0)),
                    balance_thresholds,
                    spending_thresholds,
                )
            )

        return pd.DataFrame({"customer_id": working["customer_id"], "lifestyle_category": categories})

    @staticmethod
    def _classify_lifestyle(
        average_balance: float,
        monthly_spending: float,
        balance_thresholds: dict[str, float],
        spending_thresholds: dict[str, float],
    ) -> str:
        if average_balance >= balance_thresholds["comfortable"] and monthly_spending >= spending_thresholds["comfortable"]:
            return "Premium"
        if average_balance >= balance_thresholds["moderate"] and monthly_spending >= spending_thresholds["moderate"]:
            return "Comfortable"
        if average_balance >= balance_thresholds["essential"] or monthly_spending >= spending_thresholds["essential"]:
            return "Moderate"
        return "Essential"
