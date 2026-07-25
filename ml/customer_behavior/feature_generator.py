from __future__ import annotations

import pandas as pd

from ml.customer_behavior.statistics import BehaviourStatistics


class BehaviourFeatureGenerator:
    """Generate deterministic behaviour features for customer profiles."""

    def __init__(self, statistics: BehaviourStatistics | None = None) -> None:
        self.statistics = statistics or BehaviourStatistics()

    def build(self, frame: pd.DataFrame) -> pd.DataFrame:
        working = frame.copy()

        working["spending_volatility"] = working.apply(
            lambda row: self.statistics.ratio(row["transaction_amount_std"], row["average_transaction_amount"]),
            axis=1,
        )
        working["spending_consistency"] = working["spending_volatility"].apply(self.statistics.normalized_inverse)
        working["preferred_time_of_day"] = working["preferred_transaction_hour"].apply(self._hour_to_time_of_day)
        working["weekday_transaction_share"] = working.apply(lambda row: self._weekday_share(row), axis=1)
        working["weekend_transaction_share"] = working.apply(lambda row: self._weekend_share(row), axis=1)
        working["weekday_vs_weekend_behavior"] = working.apply(self._weekday_vs_weekend_behavior, axis=1)
        working["estimated_monthly_salary"] = working.apply(self._estimate_salary, axis=1)
        working["expense_ratio"] = working.apply(self._expense_ratio, axis=1)
        working["balance_utilisation"] = working.apply(self._balance_utilisation, axis=1)
        working["transaction_regularity"] = working.apply(self._transaction_regularity, axis=1)
        return working

    @staticmethod
    def _hour_to_time_of_day(hour: object) -> str:
        hour_int = int(hour)
        if 5 <= hour_int < 12:
            return "Morning"
        if 12 <= hour_int < 17:
            return "Afternoon"
        if 17 <= hour_int < 21:
            return "Evening"
        return "Night"

    @staticmethod
    def _weekday_share(row: pd.Series) -> float:
        total_transactions = float(row.get("total_transactions", 0))
        if total_transactions <= 0:
            return 0.0
        weekday_transactions = float(row.get("weekday_transactions", 0))
        return float(round(weekday_transactions / total_transactions, 4))

    @staticmethod
    def _weekend_share(row: pd.Series) -> float:
        total_transactions = float(row.get("total_transactions", 0))
        if total_transactions <= 0:
            return 0.0
        weekend_transactions = float(row.get("weekend_transactions", 0))
        return float(round(weekend_transactions / total_transactions, 4))

    @staticmethod
    def _weekday_vs_weekend_behavior(row: pd.Series) -> str:
        if row["weekend_transaction_share"] >= 0.6:
            return "Weekend-Heavy"
        if row["weekday_transaction_share"] >= 0.6:
            return "Weekday-Heavy"
        return "Balanced"

    @staticmethod
    def _estimate_salary(row: pd.Series) -> float:
        return float(round((row["average_monthly_spending"] * 1.8) + (row["average_account_balance"] * 0.15), 2))

    @staticmethod
    def _expense_ratio(row: pd.Series) -> float:
        denominator = float(row["estimated_monthly_salary"])
        if denominator <= 0:
            return 0.0
        return float(round(row["average_monthly_spending"] / denominator, 4))

    @staticmethod
    def _balance_utilisation(row: pd.Series) -> float:
        denominator = float(row["average_account_balance"])
        if denominator <= 0:
            return 0.0
        value = 1.0 - (float(row["average_balance_after_transaction"]) / denominator)
        return float(round(max(min(value, 1.0), 0.0), 4))

    @staticmethod
    def _transaction_regularity(row: pd.Series) -> float:
        days_active = max(float(row.get("days_active", 0)), 1.0)
        total_transactions = max(float(row.get("total_transactions", 0)), 1.0)
        expected_gap = days_active / total_transactions
        return float(round(1.0 / (1.0 + expected_gap), 4))