from __future__ import annotations

import numpy as np
import pandas as pd

from ml.customer_behavior.statistics import BehaviourStatistics


class TransactionTimingAnalyzer:
    """Analyze transaction timing behavior across hours and day parts."""

    time_of_day_order = ["Morning", "Afternoon", "Evening", "Night"]

    def __init__(self, statistics: BehaviourStatistics | None = None) -> None:
        self.statistics = statistics or BehaviourStatistics()

    def build(self, frame: pd.DataFrame) -> pd.DataFrame:
        grouped = frame.groupby("customer_id", sort=False)
        features = grouped.agg(
            timing_average_hour=("transaction_hour", "mean"),
            timing_hour_std=("transaction_hour", lambda series: self.statistics.safe_std(series)),
            timing_peak_hour=("transaction_hour", lambda series: self.statistics.safe_mode(series)),
            timing_gap_mean_minutes=("transaction_timestamp", lambda series: self._average_gap_minutes(series)),
            timing_gap_std_minutes=("transaction_timestamp", lambda series: self._gap_std_minutes(series)),
        ).reset_index()

        time_of_day_shares = self._time_of_day_shares(frame)
        features = features.merge(time_of_day_shares, on="customer_id", how="left")
        features["timing_peak_concentration"] = features[
            ["timing_share_morning", "timing_share_afternoon", "timing_share_evening", "timing_share_night"]
        ].max(axis=1)
        features["timing_entropy"] = features.apply(self._timing_entropy, axis=1)
        features["timing_night_activity_score"] = features["timing_share_night"]
        return features

    def _time_of_day_shares(self, frame: pd.DataFrame) -> pd.DataFrame:
        counts = (
            frame.groupby(["customer_id", "time_of_day"], sort=False)
            .size()
            .unstack(fill_value=0)
            .reset_index()
        )
        for label in self.time_of_day_order:
            if label not in counts.columns:
                counts[label] = 0
        total = counts[self.time_of_day_order].sum(axis=1).replace(0, 1)
        for label in self.time_of_day_order:
            counts[f"timing_share_{label.lower()}"] = (counts[label] / total).round(4)
        share_columns = [f"timing_share_{label.lower()}" for label in self.time_of_day_order]
        return counts[["customer_id", *share_columns]]

    @staticmethod
    def _average_gap_minutes(timestamps: pd.Series) -> float:
        ordered = pd.to_datetime(timestamps, errors="coerce").dropna().sort_values()
        if len(ordered) <= 1:
            return 0.0
        gaps = ordered.diff().dt.total_seconds().div(60).dropna()
        if gaps.empty:
            return 0.0
        return float(round(gaps.mean(), 4))

    @staticmethod
    def _gap_std_minutes(timestamps: pd.Series) -> float:
        ordered = pd.to_datetime(timestamps, errors="coerce").dropna().sort_values()
        if len(ordered) <= 1:
            return 0.0
        gaps = ordered.diff().dt.total_seconds().div(60).dropna()
        if gaps.empty:
            return 0.0
        return float(round(gaps.std(ddof=0), 4))

    @staticmethod
    def _timing_entropy(row: pd.Series) -> float:
        shares = np.array(
            [
                row.get("timing_share_morning", 0.0),
                row.get("timing_share_afternoon", 0.0),
                row.get("timing_share_evening", 0.0),
                row.get("timing_share_night", 0.0),
            ],
            dtype=float,
        )
        shares = shares[shares > 0]
        if shares.size == 0:
            return 0.0
        return float(round(-(shares * np.log(shares)).sum(), 4))
