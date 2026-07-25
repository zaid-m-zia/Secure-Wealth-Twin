from __future__ import annotations

import numpy as np
import pandas as pd

from ml.customer_behavior.statistics import BehaviourStatistics


class IncomeStabilityAnalyzer:
    """Estimate income and balance stability metrics."""

    def __init__(self, statistics: BehaviourStatistics | None = None) -> None:
        self.statistics = statistics or BehaviourStatistics()

    def build(self, frame: pd.DataFrame) -> pd.DataFrame:
        monthly_balance = (
            frame.groupby(["customer_id", "transaction_month"], sort=False)["account_balance"]
            .mean()
            .reset_index(name="monthly_average_balance")
        )
        monthly_spending = (
            frame.groupby(["customer_id", "transaction_month"], sort=False)["transaction_amount"]
            .sum()
            .reset_index(name="monthly_total_spending")
        )
        monthly = monthly_balance.merge(monthly_spending, on=["customer_id", "transaction_month"], how="outer")
        monthly = monthly.sort_values(["customer_id", "transaction_month"])

        monthly["month_index"] = monthly.groupby("customer_id", sort=False).cumcount()
        monthly["balance_change"] = monthly.groupby("customer_id", sort=False)["monthly_average_balance"].diff()

        grouped = monthly.groupby("customer_id", sort=False)
        features = grouped.agg(
            income_stability_balance_mean=("monthly_average_balance", "mean"),
            income_stability_balance_std=("monthly_average_balance", lambda series: self.statistics.safe_std(series)),
            income_stability_spending_mean=("monthly_total_spending", "mean"),
            income_stability_spending_std=("monthly_total_spending", lambda series: self.statistics.safe_std(series)),
            income_stability_balance_trend=("monthly_average_balance", lambda series: self._linear_slope(series)),
            income_stability_spending_trend=("monthly_total_spending", lambda series: self._linear_slope(series)),
            income_stability_positive_balance_months=("balance_change", lambda series: float((series > 0).sum())),
        ).reset_index()

        features["income_stability_score"] = features.apply(
            lambda row: self._stability_score(
                row["income_stability_balance_std"],
                row["income_stability_balance_mean"],
                row["income_stability_spending_std"],
                row["income_stability_spending_mean"],
            ),
            axis=1,
        )
        features["income_proxy_volatility"] = features.apply(
            lambda row: self.statistics.ratio(
                row["income_stability_spending_std"],
                row["income_stability_spending_mean"],
            ),
            axis=1,
        )
        return features

    def _stability_score(
        self,
        balance_std: float,
        balance_mean: float,
        spending_std: float,
        spending_mean: float,
    ) -> float:
        balance_cv = self.statistics.ratio(balance_std, balance_mean)
        spending_cv = self.statistics.ratio(spending_std, spending_mean)
        combined = (balance_cv + spending_cv) / 2.0
        return float(round(self.statistics.normalized_inverse(combined), 4))

    @staticmethod
    def _linear_slope(series: pd.Series) -> float:
        numeric = pd.to_numeric(series, errors="coerce").dropna()
        if len(numeric) <= 1:
            return 0.0
        x_values = np.arange(len(numeric), dtype=float)
        slope = np.polyfit(x_values, numeric.to_numpy(dtype=float), 1)[0]
        return float(round(slope, 4))
