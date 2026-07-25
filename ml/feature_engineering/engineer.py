from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class FeatureEngineeringResult:
    dataframe: pd.DataFrame
    feature_columns: list[str]


class FeatureEngineer:
    """Build transaction, behavior, and risk features for model preparation."""

    def build(self, frame: pd.DataFrame) -> FeatureEngineeringResult:
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

        working = self._add_transaction_features(working)
        customer_features = self._build_customer_features(working)
        working = working.merge(customer_features, on="customer_id", how="left")
        working = self._add_risk_features(working)

        feature_columns = [
            column
            for column in working.columns
            if column not in {"transaction_id", "customer_id", "customer_dob", "transaction_timestamp"}
        ]
        return FeatureEngineeringResult(dataframe=working, feature_columns=feature_columns)

    def _add_transaction_features(self, frame: pd.DataFrame) -> pd.DataFrame:
        working = frame.copy()

        working["age"] = self._calculate_age(working["customer_dob"], working["transaction_date"])
        working["age_group"] = working["age"].apply(self._age_group)
        working["day_of_week"] = working["transaction_date"].dt.dayofweek
        working["weekend_flag"] = working["day_of_week"].isin([5, 6]).astype(int)
        working["month"] = working["transaction_date"].dt.month
        working["year"] = working["transaction_date"].dt.year
        working["time_of_day"] = working["transaction_hour"].apply(self._time_of_day)

        working["balance_after_transaction"] = working["account_balance"] - working["transaction_amount"]
        working["transaction_balance_ratio"] = working["transaction_amount"] / working["account_balance"].replace(0, np.nan)
        working["transaction_balance_ratio"] = working["transaction_balance_ratio"].fillna(0.0)
        working["log_transaction_amount"] = np.log1p(working["transaction_amount"])
        return working

    def _build_customer_features(self, frame: pd.DataFrame) -> pd.DataFrame:
        grouped = frame.sort_values("transaction_timestamp").groupby("customer_id", sort=False)

        customer_features = grouped.agg(
            average_transaction_amount=("transaction_amount", "mean"),
            median_transaction_amount=("transaction_amount", "median"),
            std_transaction_amount=("transaction_amount", lambda series: float(series.std(ddof=0)) if len(series) > 1 else 0.0),
            maximum_transaction_amount=("transaction_amount", "max"),
            minimum_transaction_amount=("transaction_amount", "min"),
            total_transactions=("transaction_id", "count"),
            average_balance=("account_balance", "mean"),
            first_transaction_date=("transaction_date", "min"),
            last_transaction_date=("transaction_date", "max"),
            preferred_transaction_hour=("transaction_hour", self._mode_value),
            preferred_weekday=("day_of_week", self._mode_value),
            preferred_time=("time_of_day", self._mode_value),
        ).reset_index()

        customer_features["days_active"] = (
            customer_features["last_transaction_date"] - customer_features["first_transaction_date"]
        ).dt.days.add(1)
        customer_features["days_active"] = customer_features["days_active"].clip(lower=1)
        customer_features["average_daily_spending"] = (
            customer_features["average_transaction_amount"] * customer_features["total_transactions"]
        ) / customer_features["days_active"]
        customer_features["transaction_frequency"] = customer_features["total_transactions"] / customer_features["days_active"]
        customer_features["transaction_frequency"] = customer_features["transaction_frequency"].fillna(0.0)

        return customer_features[
            [
                "customer_id",
                "average_transaction_amount",
                "median_transaction_amount",
                "std_transaction_amount",
                "maximum_transaction_amount",
                "minimum_transaction_amount",
                "total_transactions",
                "average_balance",
                "average_daily_spending",
                "days_active",
                "transaction_frequency",
                "preferred_transaction_hour",
                "preferred_weekday",
                "preferred_time",
            ]
        ]

    def _add_risk_features(self, frame: pd.DataFrame) -> pd.DataFrame:
        working = frame.sort_values(["customer_id", "transaction_timestamp"]).copy()

        large_threshold = working["transaction_amount"].quantile(0.90)
        very_large_threshold = working["transaction_amount"].quantile(0.98)
        low_balance_threshold = working["account_balance"].quantile(0.20)

        previous_transaction = working.groupby("customer_id")["transaction_timestamp"].shift(1)
        previous_gap = (working["transaction_timestamp"] - previous_transaction).dt.total_seconds().div(60)

        working["large_transaction_flag"] = (working["transaction_amount"] >= large_threshold).astype(int)
        working["very_large_transaction_flag"] = (working["transaction_amount"] >= very_large_threshold).astype(int)
        working["rapid_transaction_flag"] = previous_gap.le(60).fillna(False).astype(int)
        working["new_customer_flag"] = (working["total_transactions"] <= 3).astype(int)
        working["low_balance_flag"] = ((working["account_balance"] <= low_balance_threshold) | (working["balance_after_transaction"] <= 0)).astype(int)
        working["high_spending_flag"] = (
            (working["transaction_amount"] >= working["average_transaction_amount"] * 2.0)
            | (working["transaction_balance_ratio"] >= 0.40)
        ).astype(int)
        working["dormant_customer_flag"] = previous_gap.ge(90 * 24 * 60).fillna(False).astype(int)
        return working

    @staticmethod
    def _calculate_age(dob: pd.Series, transaction_date: pd.Series) -> pd.Series:
        years = (transaction_date - dob).dt.days / 365.25
        years = years.where((years >= 0) & (years <= 120))
        median_age = years.dropna().median()
        if pd.isna(median_age):
            median_age = 0.0
        return years.fillna(median_age).round(2)

    @staticmethod
    def _age_group(age: float) -> str:
        if pd.isna(age):
            return "Unknown"
        age = float(age)
        if age < 18:
            return "Under 18"
        if age < 26:
            return "18-25"
        if age < 36:
            return "26-35"
        if age < 46:
            return "36-45"
        if age < 61:
            return "46-60"
        return "60+"

    @staticmethod
    def _time_of_day(hour: object) -> str:
        hour_int = int(hour)
        if 5 <= hour_int < 12:
            return "Morning"
        if 12 <= hour_int < 17:
            return "Afternoon"
        if 17 <= hour_int < 21:
            return "Evening"
        return "Night"

    @staticmethod
    def _mode_value(series: pd.Series):
        non_null = series.dropna()
        if non_null.empty:
            return None
        modes = non_null.mode()
        if modes.empty:
            return non_null.iloc[0]
        return modes.iloc[0]
