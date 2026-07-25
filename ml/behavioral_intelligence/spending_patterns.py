from __future__ import annotations

import numpy as np
import pandas as pd

from ml.customer_behavior.statistics import BehaviourStatistics


class SpendingPatternAnalyzer:
    """Analyze customer spending patterns from transaction history."""

    def __init__(self, statistics: BehaviourStatistics | None = None) -> None:
        self.statistics = statistics or BehaviourStatistics()

    def build(self, frame: pd.DataFrame) -> pd.DataFrame:
        grouped = frame.groupby("customer_id", sort=False)
        features = grouped.agg(
            spending_pattern_mean=("transaction_amount", "mean"),
            spending_pattern_median=("transaction_amount", "median"),
            spending_pattern_std=("transaction_amount", lambda series: self.statistics.safe_std(series)),
            spending_pattern_skew=("transaction_amount", lambda series: self._safe_skew(series)),
            spending_pattern_total=("transaction_amount", "sum"),
            spending_pattern_count=("transaction_id", "count"),
        ).reset_index()

        first_last = grouped.agg(
            first_transaction_date=("transaction_date", "min"),
            last_transaction_date=("transaction_date", "max"),
        ).reset_index()
        first_last["active_days"] = (
            first_last["last_transaction_date"] - first_last["first_transaction_date"]
        ).dt.days.add(1).clip(lower=1)
        features = features.merge(first_last[["customer_id", "active_days"]], on="customer_id", how="left")

        features["spending_velocity"] = features["spending_pattern_total"] / features["active_days"]
        features["spending_volatility_index"] = features.apply(
            lambda row: self.statistics.ratio(row["spending_pattern_std"], row["spending_pattern_mean"]),
            axis=1,
        )
        features["spending_burst_score"] = features.apply(
            lambda row: self.statistics.ratio(row["spending_pattern_skew"], row["spending_pattern_std"] + 1.0),
            axis=1,
        )

        category_shares = self._amount_category_shares(frame)
        features = features.merge(category_shares, on="customer_id", how="left")
        return features.drop(columns=["active_days"])

    def _amount_category_shares(self, frame: pd.DataFrame) -> pd.DataFrame:
        category_counts = (
            frame.groupby(["customer_id", "amount_category"], sort=False)
            .size()
            .unstack(fill_value=0)
            .reset_index()
        )
        count_columns = [column for column in category_counts.columns if column != "customer_id"]
        totals = category_counts[count_columns].sum(axis=1).replace(0, 1)
        for column in count_columns:
            category_counts[f"spending_share_{str(column).lower()}"] = (
                category_counts[column] / totals
            ).round(4)
        share_columns = [f"spending_share_{str(column).lower()}" for column in count_columns]
        return category_counts[["customer_id", *share_columns]]

    @staticmethod
    def _safe_skew(series: pd.Series) -> float:
        numeric = pd.to_numeric(series, errors="coerce").dropna()
        if len(numeric) <= 2:
            return 0.0
        return float(numeric.skew())
