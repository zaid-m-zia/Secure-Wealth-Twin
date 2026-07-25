from __future__ import annotations

import numpy as np
import pandas as pd


class SpendingCapacityAnalyzer:
    """Estimate how much discretionary spending capacity a customer has."""

    def build(self, state: pd.DataFrame) -> pd.DataFrame:
        working = state.copy()
        monthly_spending = working.get("average_monthly_spending", working.get("spending_pattern_total", 0.0))
        estimated_income = working.get("estimated_monthly_salary", monthly_spending * 1.8)
        average_balance = working.get("average_account_balance", 0.0)

        capacity_ratio = np.where(
            estimated_income > 0,
            1.0 - (monthly_spending / estimated_income),
            0.0,
        )
        balance_buffer = np.clip(average_balance / (monthly_spending.replace(0, 1.0) * 3.0), 0.0, 1.0)
        spending_capacity = np.clip((capacity_ratio * 0.6 + balance_buffer * 0.4) * 100.0, 0.0, 100.0)

        working["spending_capacity"] = np.round(spending_capacity, 2)
        return working[["customer_id", "spending_capacity"]]
