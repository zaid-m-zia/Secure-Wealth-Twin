from __future__ import annotations

import numpy as np
import pandas as pd


class TransactionContextBuilder:
    """Prepare transaction-level context used by behavioral intelligence analyzers."""

    amount_category_bins = [0.0, 100.0, 500.0, 2000.0, 10000.0, np.inf]
    amount_category_labels = ["Micro", "Small", "Medium", "Large", "VeryLarge"]

    def build(self, frame: pd.DataFrame) -> pd.DataFrame:
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
        working["transaction_month"] = working["transaction_date"].dt.to_period("M").astype(str)
        working["day_of_week"] = working["transaction_date"].dt.dayofweek
        working["is_weekend"] = working["day_of_week"].isin([5, 6]).astype(int)
        working["time_of_day"] = working["transaction_hour"].apply(self._hour_to_time_of_day)
        working["amount_category"] = pd.cut(
            working["transaction_amount"],
            bins=self.amount_category_bins,
            labels=self.amount_category_labels,
            include_lowest=True,
            right=False,
        ).astype("string")
        working["location"] = working["location"].astype("string").fillna("Unknown")
        working["balance_change"] = working.groupby("customer_id", sort=False)["account_balance"].diff()
        return working.sort_values(["customer_id", "transaction_timestamp"]).reset_index(drop=True)

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
