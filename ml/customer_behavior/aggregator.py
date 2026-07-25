from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from ml.customer_behavior.statistics import BehaviourStatistics


@dataclass(frozen=True)
class CustomerBehaviourAggregationResult:
    dataframe: pd.DataFrame
    customer_count: int


class CustomerBehaviourAggregator:
    """Aggregate transaction-level records into one behavioural profile per customer."""

    def __init__(self, statistics: BehaviourStatistics | None = None) -> None:
        self.statistics = statistics or BehaviourStatistics()

    def build(self, frame: pd.DataFrame) -> CustomerBehaviourAggregationResult:
        working = frame.copy()
        working["transaction_timestamp"] = pd.to_datetime(
            working["transaction_date"].dt.strftime("%Y-%m-%d")
            + " "
            + working["transaction_hour"].astype(int).astype(str).str.zfill(2)
            + ":"
            + working["transaction_minute"].astype(int).astype(str).str.zfill(2)
            + ":"
            + working["transaction_second"].astype(int).astype(str).str.zfill(2),
            errors="coerce",
        )

        grouped = working.sort_values("transaction_timestamp").groupby("customer_id", sort=False)
        total_transactions = grouped["transaction_id"].count().rename("total_transactions")
        total_spending = grouped["transaction_amount"].sum().rename("total_spending")
        active_months = grouped["transaction_date"].apply(lambda series: series.dt.to_period("M").nunique()).rename("active_months")
        weekend_transactions = grouped["transaction_date"].apply(lambda series: int(series.dt.dayofweek.isin([5, 6]).sum())).rename("weekend_transactions")
        weekday_transactions = (total_transactions - weekend_transactions).rename("weekday_transactions")

        customer_features = grouped.agg(
            average_transaction_amount=("transaction_amount", "mean"),
            median_transaction_amount=("transaction_amount", "median"),
            maximum_transaction_amount=("transaction_amount", "max"),
            minimum_transaction_amount=("transaction_amount", "min"),
            transaction_amount_std=("transaction_amount", lambda series: self.statistics.safe_std(series)),
            average_account_balance=("account_balance", "mean"),
            balance_volatility=("account_balance", lambda series: self.statistics.safe_std(series)),
            preferred_transaction_hour=("transaction_hour", self.statistics.safe_mode),
            preferred_transaction_weekday=("transaction_date", lambda series: self.statistics.safe_mode(series.dt.dayofweek)),
            location_consistency=("location", lambda series: self._location_consistency(series)),
            gender=("gender", self.statistics.safe_mode),
            customer_dob=("customer_dob", "min"),
            first_transaction_date=("transaction_date", "min"),
            last_transaction_date=("transaction_date", "max"),
        ).reset_index()

        customer_features = customer_features.merge(total_transactions.reset_index(), on="customer_id", how="left")
        customer_features = customer_features.merge(total_spending.reset_index(), on="customer_id", how="left")
        customer_features = customer_features.merge(active_months.reset_index(), on="customer_id", how="left")
        customer_features = customer_features.merge(weekend_transactions.reset_index(), on="customer_id", how="left")
        customer_features = customer_features.merge(weekday_transactions.reset_index(), on="customer_id", how="left")

        customer_features["days_active"] = (
            customer_features["last_transaction_date"] - customer_features["first_transaction_date"]
        ).dt.days.add(1)
        customer_features["days_active"] = customer_features["days_active"].clip(lower=1)
        customer_features["transaction_frequency"] = customer_features["total_transactions"] / customer_features["days_active"]
        customer_features["average_transactions_per_day"] = customer_features["transaction_frequency"]
        customer_features["average_monthly_spending"] = customer_features["total_spending"] / customer_features["active_months"].replace(0, 1)
        customer_features["average_balance_after_transaction"] = (
            customer_features["average_account_balance"] - customer_features["average_transaction_amount"]
        )
        customer_features["age"] = (
            (customer_features["last_transaction_date"] - customer_features["customer_dob"]).dt.days.div(365.25)
        ).fillna(0.0).clip(lower=0.0).round(2)

        return CustomerBehaviourAggregationResult(
            dataframe=customer_features.drop(
                columns=[
                    "active_months",
                    "total_spending",
                    "customer_dob",
                    "first_transaction_date",
                    "last_transaction_date",
                ]
            ),
            customer_count=int(customer_features["customer_id"].nunique()),
        )

    @staticmethod
    def _location_consistency(series: pd.Series) -> float:
        non_null = series.astype("string").fillna("Unknown")
        if non_null.empty:
            return 0.0
        return float(non_null.value_counts(normalize=True).iloc[0])
