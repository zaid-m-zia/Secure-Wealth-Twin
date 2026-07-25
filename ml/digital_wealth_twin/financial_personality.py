from __future__ import annotations

import pandas as pd


class FinancialPersonalityAnalyzer:
    """Assign a financial personality label to each customer."""

    def build(self, state: pd.DataFrame) -> pd.DataFrame:
        personalities: list[str] = []
        for _, row in state.iterrows():
            personalities.append(self._classify(row))
        return pd.DataFrame({"customer_id": state["customer_id"], "financial_personality": personalities})

    @staticmethod
    def _classify(row: pd.Series) -> str:
        behaviour_profile = str(row.get("behaviour_profile", "Moderate"))
        expense_ratio = float(row.get("expense_ratio", 0.5))
        spending_consistency = float(row.get("spending_consistency", 0.5))
        risk_tolerance = float(row.get("risk_tolerance_estimate", 50.0))
        savings_tendency = float(row.get("savings_tendency", 50.0))

        if behaviour_profile in {"Conservative", "Stable"} or (expense_ratio <= 0.45 and savings_tendency >= 60.0):
            return "Conservative"
        if behaviour_profile in {"Aggressive", "Volatile"} or (expense_ratio >= 0.65 and risk_tolerance >= 60.0):
            return "Aggressive"
        if risk_tolerance >= 65.0 and spending_consistency <= 0.45:
            return "Opportunist"
        return "Balanced"
