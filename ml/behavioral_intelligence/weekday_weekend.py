from __future__ import annotations

import pandas as pd

from ml.customer_behavior.statistics import BehaviourStatistics


class WeekdayWeekendAnalyzer:
    """Analyze weekday versus weekend transaction and spending behavior."""

    def __init__(self, statistics: BehaviourStatistics | None = None) -> None:
        self.statistics = statistics or BehaviourStatistics()

    def build(self, frame: pd.DataFrame) -> pd.DataFrame:
        grouped = frame.groupby(["customer_id", "is_weekend"], sort=False)
        summary = grouped.agg(
            transaction_count=("transaction_id", "count"),
            total_spending=("transaction_amount", "sum"),
            average_amount=("transaction_amount", "mean"),
        ).reset_index()

        weekday = summary.loc[summary["is_weekend"] == 0].rename(
            columns={
                "transaction_count": "weekday_transaction_count",
                "total_spending": "weekday_total_spending",
                "average_amount": "weekday_average_amount",
            }
        )
        weekend = summary.loc[summary["is_weekend"] == 1].rename(
            columns={
                "transaction_count": "weekend_transaction_count",
                "total_spending": "weekend_total_spending",
                "average_amount": "weekend_average_amount",
            }
        )

        features = weekday[["customer_id", "weekday_transaction_count", "weekday_total_spending", "weekday_average_amount"]].merge(
            weekend[["customer_id", "weekend_transaction_count", "weekend_total_spending", "weekend_average_amount"]],
            on="customer_id",
            how="outer",
        )
        features = features.fillna(0.0)

        total_transactions = features["weekday_transaction_count"] + features["weekend_transaction_count"]
        total_spending = features["weekday_total_spending"] + features["weekend_total_spending"]
        total_transactions = total_transactions.replace(0, 1)
        total_spending = total_spending.replace(0, 1)

        features["weekday_transaction_share"] = (features["weekday_transaction_count"] / total_transactions).round(4)
        features["weekend_transaction_share"] = (features["weekend_transaction_count"] / total_transactions).round(4)
        features["weekday_spending_share"] = (features["weekday_total_spending"] / total_spending).round(4)
        features["weekend_spending_share"] = (features["weekend_total_spending"] / total_spending).round(4)
        features["weekday_weekend_amount_ratio"] = features.apply(
            lambda row: self.statistics.ratio(row["weekday_average_amount"], row["weekend_average_amount"]),
            axis=1,
        )
        features["weekday_weekend_behavior_score"] = (
            features["weekday_transaction_share"] - features["weekend_transaction_share"]
        ).round(4)
        return features
