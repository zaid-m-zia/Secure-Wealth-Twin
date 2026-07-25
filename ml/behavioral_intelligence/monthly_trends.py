from __future__ import annotations

import numpy as np
import pandas as pd

from ml.customer_behavior.statistics import BehaviourStatistics


class MonthlyTrendAnalyzer:
    """Compute monthly spending and activity trend statistics."""

    def __init__(self, statistics: BehaviourStatistics | None = None) -> None:
        self.statistics = statistics or BehaviourStatistics()

    def build(self, frame: pd.DataFrame) -> pd.DataFrame:
        monthly = (
            frame.groupby(["customer_id", "transaction_month"], sort=False)
            .agg(
                monthly_spending=("transaction_amount", "sum"),
                monthly_transaction_count=("transaction_id", "count"),
                monthly_average_amount=("transaction_amount", "mean"),
            )
            .reset_index()
            .sort_values(["customer_id", "transaction_month"])
        )
        monthly["month_index"] = monthly.groupby("customer_id", sort=False).cumcount()
        monthly["month_over_month_spending_change"] = monthly.groupby("customer_id", sort=False)["monthly_spending"].pct_change()
        monthly["month_over_month_count_change"] = monthly.groupby("customer_id", sort=False)["monthly_transaction_count"].pct_change()

        grouped = monthly.groupby("customer_id", sort=False)
        features = grouped.agg(
            monthly_spending_mean=("monthly_spending", "mean"),
            monthly_spending_std=("monthly_spending", lambda series: self.statistics.safe_std(series)),
            monthly_transaction_count_mean=("monthly_transaction_count", "mean"),
            monthly_transaction_count_std=("monthly_transaction_count", lambda series: self.statistics.safe_std(series)),
            monthly_spending_slope=("monthly_spending", lambda series: self._linear_slope(series)),
            monthly_transaction_count_slope=("monthly_transaction_count", lambda series: self._linear_slope(series)),
            monthly_spending_momentum=("month_over_month_spending_change", "mean"),
            monthly_count_momentum=("month_over_month_count_change", "mean"),
        ).reset_index()

        features["monthly_spending_volatility"] = features.apply(
            lambda row: self.statistics.ratio(row["monthly_spending_std"], row["monthly_spending_mean"]),
            axis=1,
        )
        features["monthly_trend_strength"] = features.apply(
            lambda row: float(round(abs(row["monthly_spending_slope"]) + abs(row["monthly_transaction_count_slope"]), 4)),
            axis=1,
        )
        features["monthly_seasonal_variation"] = features.apply(
            lambda row: self.statistics.ratio(row["monthly_spending_std"], row["monthly_spending_mean"]),
            axis=1,
        )
        return features.fillna(0.0)

    @staticmethod
    def _linear_slope(series: pd.Series) -> float:
        numeric = pd.to_numeric(series, errors="coerce").dropna()
        if len(numeric) <= 1:
            return 0.0
        x_values = np.arange(len(numeric), dtype=float)
        slope = np.polyfit(x_values, numeric.to_numpy(dtype=float), 1)[0]
        return float(round(slope, 4))
