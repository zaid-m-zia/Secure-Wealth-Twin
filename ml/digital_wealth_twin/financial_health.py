from __future__ import annotations

import numpy as np
import pandas as pd


class FinancialHealthAnalyzer:
    """Compute financial health and emergency preparedness scores."""

    def build(self, state: pd.DataFrame) -> pd.DataFrame:
        working = state.copy()
        average_balance = working.get("average_account_balance", 0.0)
        monthly_spending = working.get("average_monthly_spending", 1.0).replace(0, 1.0)
        financial_stability = working.get("financial_stability", 50.0)
        savings_tendency = working.get("savings_tendency", 50.0)
        fraud_exposure = working.get("customer_avg_fraud_score", 0.0)

        months_covered = np.clip(average_balance / monthly_spending, 0.0, 12.0)
        emergency_preparedness = np.clip((months_covered / 6.0) * 100.0, 0.0, 100.0)
        financial_health_score = np.clip(
            financial_stability * 0.30
            + savings_tendency * 0.25
            + emergency_preparedness * 0.25
            + (100.0 - fraud_exposure) * 0.20,
            0.0,
            100.0,
        )

        working["emergency_preparedness"] = np.round(emergency_preparedness, 2)
        working["financial_health_score"] = np.round(financial_health_score, 2)
        return working[["customer_id", "emergency_preparedness", "financial_health_score"]]
