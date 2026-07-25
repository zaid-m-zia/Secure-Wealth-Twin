from __future__ import annotations

import numpy as np
import pandas as pd


class WealthMetricsCalculator:
    """Compute wealth score and financial stability metrics."""

    def build(self, state: pd.DataFrame) -> pd.DataFrame:
        working = state.copy()
        average_balance = working.get("average_account_balance", 0.0)
        monthly_spending = working.get("average_monthly_spending", 1.0).replace(0, 1.0)
        income_stability = working.get("income_stability_score", 0.5)
        spending_consistency = working.get("spending_consistency", 0.5)
        transaction_regularity = working.get("transaction_regularity", 0.5)
        savings_tendency = working.get("savings_tendency", 50.0)

        balance_strength = np.clip(average_balance / (monthly_spending * 6.0), 0.0, 1.0)
        financial_stability = np.clip(
            (income_stability * 0.35 + spending_consistency * 0.35 + transaction_regularity * 0.30) * 100.0,
            0.0,
            100.0,
        )
        wealth_score = np.clip(
            balance_strength * 35.0 + savings_tendency * 0.35 + financial_stability * 0.30,
            0.0,
            100.0,
        )

        working["financial_stability"] = np.round(financial_stability, 2)
        working["wealth_score"] = np.round(wealth_score, 2)
        return working[["customer_id", "financial_stability", "wealth_score"]]
