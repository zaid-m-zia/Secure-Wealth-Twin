from __future__ import annotations

import numpy as np
import pandas as pd

from ml.customer_behavior.statistics import BehaviourStatistics


class CategoryFrequencyAnalyzer:
    """Analyze location and amount-category frequency patterns."""

    def __init__(self, statistics: BehaviourStatistics | None = None) -> None:
        self.statistics = statistics or BehaviourStatistics()

    def build(self, frame: pd.DataFrame) -> pd.DataFrame:
        location_features = self._location_frequency(frame)
        amount_category_features = self._amount_category_frequency(frame)
        return location_features.merge(amount_category_features, on="customer_id", how="outer")

    def _location_frequency(self, frame: pd.DataFrame) -> pd.DataFrame:
        location_counts = (
            frame.groupby(["customer_id", "location"], sort=False)
            .size()
            .reset_index(name="location_count")
        )
        totals = location_counts.groupby("customer_id", sort=False)["location_count"].transform("sum").replace(0, 1)
        location_counts["location_share"] = location_counts["location_count"] / totals

        grouped = location_counts.groupby("customer_id", sort=False)
        features = grouped.agg(
            category_unique_locations=("location", "nunique"),
            category_top_location_share=("location_share", "max"),
            category_location_entropy=("location_share", lambda series: self._entropy(series)),
        ).reset_index()
        switch_rates = self._location_switch_rates(frame)
        features = features.merge(switch_rates, on="customer_id", how="left")
        return features

    def _amount_category_frequency(self, frame: pd.DataFrame) -> pd.DataFrame:
        category_counts = (
            frame.groupby(["customer_id", "amount_category"], sort=False)
            .size()
            .reset_index(name="category_count")
        )
        totals = category_counts.groupby("customer_id", sort=False)["category_count"].transform("sum").replace(0, 1)
        category_counts["category_share"] = category_counts["category_count"] / totals

        grouped = category_counts.groupby("customer_id", sort=False)
        features = grouped.agg(
            category_unique_amount_buckets=("amount_category", "nunique"),
            category_top_amount_bucket_share=("category_share", "max"),
            category_amount_entropy=("category_share", lambda series: self._entropy(series)),
        ).reset_index()
        return features

    @staticmethod
    def _entropy(shares: pd.Series) -> float:
        values = pd.to_numeric(shares, errors="coerce").dropna()
        values = values[values > 0]
        if values.empty:
            return 0.0
        return float(round(-(values * np.log(values)).sum(), 4))

    def _location_switch_rates(self, frame: pd.DataFrame) -> pd.DataFrame:
        ordered = frame.sort_values(["customer_id", "transaction_timestamp"])
        switch_flags = ordered.groupby("customer_id", sort=False)["location"].apply(self._switch_rate)
        return switch_flags.reset_index(name="category_location_switch_rate")

    @staticmethod
    def _switch_rate(locations: pd.Series) -> float:
        values = locations.astype("string").fillna("Unknown")
        if len(values) <= 1:
            return 0.0
        switches = (values != values.shift(1)).sum() - 1
        return float(round(max(switches, 0) / max(len(values) - 1, 1), 4))
