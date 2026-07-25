from __future__ import annotations

import numpy as np
import pandas as pd


class WealthTwinProfileBuilder:
    """Assemble the final Digital Wealth Twin profile for each customer."""

    twin_metric_columns = [
        "spending_capacity",
        "savings_tendency",
        "financial_stability",
        "wealth_score",
        "financial_health_score",
        "investment_readiness",
        "debt_pressure_estimate",
        "spending_discipline",
        "risk_tolerance_estimate",
        "income_consistency",
        "emergency_preparedness",
        "lifestyle_category",
        "financial_personality",
    ]

    def build(self, state: pd.DataFrame) -> pd.DataFrame:
        working = state.copy()
        working["debt_pressure_estimate"] = self._debt_pressure(working)
        working["spending_discipline"] = self._spending_discipline(working)
        working["income_consistency"] = self._income_consistency(working)
        return working[
            ["customer_id", "debt_pressure_estimate", "spending_discipline", "income_consistency"]
        ]

    def _debt_pressure(self, frame: pd.DataFrame) -> np.ndarray:
        balance_utilisation = frame.get("balance_utilisation", 0.5)
        expense_ratio = frame.get("expense_ratio", 0.5)
        low_balance_signal = (frame.get("average_account_balance", 0.0) <= frame["average_account_balance"].quantile(0.25)).astype(float)
        pressure = (
            balance_utilisation.clip(0.0, 1.0) * 0.40
            + expense_ratio.clip(0.0, 1.0) * 0.40
            + low_balance_signal * 0.20
        )
        return np.round(np.clip(pressure * 100.0, 0.0, 100.0), 2)

    def _spending_discipline(self, frame: pd.DataFrame) -> np.ndarray:
        spending_consistency = frame.get("spending_consistency", 0.5)
        expense_ratio = frame.get("expense_ratio", 0.5)
        transaction_regularity = frame.get("transaction_regularity", 0.5)
        discipline = (
            spending_consistency.clip(0.0, 1.0) * 0.40
            + (1.0 - expense_ratio.clip(0.0, 1.0)) * 0.35
            + transaction_regularity.clip(0.0, 1.0) * 0.25
        )
        return np.round(np.clip(discipline * 100.0, 0.0, 100.0), 2)

    def _income_consistency(self, frame: pd.DataFrame) -> np.ndarray:
        income_stability = frame.get("income_stability_score", frame.get("income_stability_score", 0.5))
        cash_flow_volatility = frame.get("cash_flow_volatility", 0.5)
        consistency = income_stability.clip(0.0, 1.0) * 0.65 + (1.0 - cash_flow_volatility.clip(0.0, 1.0)) * 0.35
        return np.round(np.clip(consistency * 100.0, 0.0, 100.0), 2)

    def select_twin_columns(self, frame: pd.DataFrame) -> list[str]:
        profile_columns = [
            "customer_id",
            "gender",
            "age",
            "behaviour_profile",
            "financial_fingerprint_signature",
            "customer_avg_fraud_score",
            "customer_max_fraud_score",
            "customer_flagged_share",
        ]
        available_profile_columns = [column for column in profile_columns if column in frame.columns]
        available_metrics = [column for column in self.twin_metric_columns if column in frame.columns]
        return available_profile_columns + available_metrics
