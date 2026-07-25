from __future__ import annotations

import pandas as pd

from ml.customer_behavior.statistics import BehaviourStatistics


class CashFlowTrendAnalyzer:
    """Derive cash-flow trend features from balance and spending dynamics."""

    def __init__(self, statistics: BehaviourStatistics | None = None) -> None:
        self.statistics = statistics or BehaviourStatistics()

    def build(self, frame: pd.DataFrame) -> pd.DataFrame:
        monthly = (
            frame.groupby(["customer_id", "transaction_month"], sort=False)
            .agg(
                monthly_spending=("transaction_amount", "sum"),
                monthly_transaction_count=("transaction_id", "count"),
                monthly_average_balance=("account_balance", "mean"),
            )
            .reset_index()
            .sort_values(["customer_id", "transaction_month"])
        )
        monthly["month_index"] = monthly.groupby("customer_id", sort=False).cumcount()
        monthly["net_balance_change"] = monthly.groupby("customer_id", sort=False)["monthly_average_balance"].diff()
        monthly["spending_change"] = monthly.groupby("customer_id", sort=False)["monthly_spending"].diff()

        grouped = monthly.groupby("customer_id", sort=False)
        features = grouped.agg(
            cash_flow_spending_mean=("monthly_spending", "mean"),
            cash_flow_spending_std=("monthly_spending", lambda series: self.statistics.safe_std(series)),
            cash_flow_balance_change_mean=("net_balance_change", "mean"),
            cash_flow_balance_change_std=("net_balance_change", lambda series: self.statistics.safe_std(series)),
            cash_flow_spending_trend=("monthly_spending", lambda series: self._linear_slope(series)),
            cash_flow_balance_trend=("monthly_average_balance", lambda series: self._linear_slope(series)),
            cash_flow_positive_months=("net_balance_change", lambda series: float((series > 0).sum())),
            cash_flow_negative_months=("net_balance_change", lambda series: float((series < 0).sum())),
        ).reset_index()

        features["cash_flow_volatility"] = features.apply(
            lambda row: self.statistics.ratio(row["cash_flow_spending_std"], row["cash_flow_spending_mean"]),
            axis=1,
        )
        features["cash_flow_direction_score"] = features.apply(
            lambda row: self._direction_score(
                row["cash_flow_spending_trend"],
                row["cash_flow_balance_trend"],
            ),
            axis=1,
        )
        features["cash_flow_net_ratio"] = features.apply(
            lambda row: self.statistics.ratio(
                row["cash_flow_balance_change_mean"],
                row["cash_flow_spending_mean"],
            ),
            axis=1,
        )
        return features

    @staticmethod
    def _linear_slope(series: pd.Series) -> float:
        numeric = pd.to_numeric(series, errors="coerce").dropna()
        if len(numeric) <= 1:
            return 0.0
        import numpy as np

        x_values = np.arange(len(numeric), dtype=float)
        slope = np.polyfit(x_values, numeric.to_numpy(dtype=float), 1)[0]
        return float(round(slope, 4))

    @staticmethod
    def _direction_score(spending_trend: float, balance_trend: float) -> float:
        if spending_trend <= 0 and balance_trend >= 0:
            return 1.0
        if spending_trend >= 0 and balance_trend <= 0:
            return -1.0
        return 0.0
