from __future__ import annotations

import pandas as pd


class BehaviourProfileBuilder:
    """Assign deterministic behavioural categories to customers."""

    def build(self, frame: pd.DataFrame) -> pd.DataFrame:
        working = frame.copy()
        thresholds = {
            "low_frequency": float(working["transaction_frequency"].quantile(0.25)),
            "high_frequency": float(working["transaction_frequency"].quantile(0.75)),
            "low_balance": float(working["average_account_balance"].quantile(0.25)),
            "high_balance": float(working["average_account_balance"].quantile(0.75)),
            "high_volatility": float(working["spending_volatility"].quantile(0.75)),
            "low_consistency": float(working["spending_consistency"].quantile(0.25)),
            "high_consistency": float(working["spending_consistency"].quantile(0.75)),
            "low_expense_ratio": float(working["expense_ratio"].quantile(0.25)),
            "high_expense_ratio": float(working["expense_ratio"].quantile(0.75)),
            "low_regularity": float(working["transaction_regularity"].quantile(0.25)),
        }
        profiles: list[str] = []
        reasons: list[str] = []

        for _, row in working.iterrows():
            profile, reason = self._classify(row, thresholds)
            profiles.append(profile)
            reasons.append(reason)

        working["behaviour_profile"] = profiles
        working["behaviour_profile_reason"] = reasons
        return working

    def _classify(self, row: pd.Series, thresholds: dict[str, float]) -> tuple[str, str]:
        total_transactions = float(row["total_transactions"])
        transaction_frequency = float(row["transaction_frequency"])
        average_account_balance = float(row["average_account_balance"])
        balance_utilisation = float(row["balance_utilisation"])
        spending_consistency = float(row["spending_consistency"])
        spending_volatility = float(row["spending_volatility"])
        expense_ratio = float(row["expense_ratio"])
        transaction_regularity = float(row["transaction_regularity"])

        if total_transactions <= 3 or transaction_frequency <= thresholds["low_frequency"]:
            return "Low Frequency", "Low transaction count or infrequent activity relative to the dataset."
        if transaction_frequency >= thresholds["high_frequency"]:
            return "High Frequency", "High average daily transaction intensity."
        if average_account_balance >= thresholds["high_balance"] and balance_utilisation <= 0.35:
            return "High Balance", "Average account balance is elevated relative to the dataset."
        if average_account_balance <= thresholds["low_balance"] or balance_utilisation >= 0.70:
            return "Low Balance", "Average balance utilisation is high."
        if spending_volatility >= thresholds["high_volatility"] or transaction_regularity <= thresholds["low_regularity"]:
            return "Volatile", "Irregular transactions and variable spending patterns."
        if spending_consistency >= thresholds["high_consistency"] and transaction_regularity >= 0.55:
            return "Stable", "Consistent transaction sizes and regular timing."
        if expense_ratio <= thresholds["low_expense_ratio"] and spending_consistency >= thresholds["high_consistency"]:
            return "Conservative", "Controlled spending relative to estimated income."
        if expense_ratio >= thresholds["high_expense_ratio"] or balance_utilisation >= 0.55:
            return "Aggressive", "Higher relative spending and utilisation."
        return "Moderate", "Balanced spending and utilisation characteristics."