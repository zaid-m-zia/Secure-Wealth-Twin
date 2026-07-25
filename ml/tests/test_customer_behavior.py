from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ml.customer_behavior.aggregator import CustomerBehaviourAggregator
from ml.customer_behavior.feature_generator import BehaviourFeatureGenerator
from ml.customer_behavior.profile_builder import BehaviourProfileBuilder


def _build_clean_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "transaction_id": ["T1", "T2", "T3", "T4", "T5"],
            "customer_id": ["C1", "C1", "C1", "C2", "C2"],
            "customer_dob": pd.to_datetime(["1990-01-10", "1990-01-10", "1990-01-10", "1985-05-05", "1985-05-05"]),
            "gender": ["F", "F", "F", "M", "M"],
            "location": ["Mumbai", "Mumbai", "Pune", "Delhi", "Delhi"],
            "account_balance": [1000.0, 1100.0, 1200.0, 5000.0, 4800.0],
            "transaction_date": pd.to_datetime(["2016-08-01", "2016-08-02", "2016-08-04", "2016-08-01", "2016-08-03"]),
            "transaction_hour": [9, 10, 18, 14, 16],
            "transaction_minute": [0, 15, 45, 5, 20],
            "transaction_second": [0, 0, 0, 0, 0],
            "transaction_amount": [50.0, 60.0, 100.0, 800.0, 850.0],
        }
    )


def test_customer_behaviour_aggregator_creates_one_row_per_customer() -> None:
    result = CustomerBehaviourAggregator().build(_build_clean_frame())
    frame = result.dataframe

    assert result.customer_count == 2
    assert len(frame) == 2
    assert set(frame["customer_id"]) == {"C1", "C2"}
    assert frame.loc[frame["customer_id"] == "C1", "total_transactions"].iloc[0] == 3
    assert frame.loc[frame["customer_id"] == "C2", "location_consistency"].iloc[0] == 1.0


def test_behaviour_feature_generator_adds_expected_features() -> None:
    aggregated = CustomerBehaviourAggregator().build(_build_clean_frame()).dataframe
    features = BehaviourFeatureGenerator().build(aggregated)

    expected_columns = {
        "spending_volatility",
        "spending_consistency",
        "preferred_time_of_day",
        "weekday_transaction_share",
        "weekend_transaction_share",
        "weekday_vs_weekend_behavior",
        "estimated_monthly_salary",
        "expense_ratio",
        "balance_utilisation",
        "transaction_regularity",
    }
    assert expected_columns.issubset(set(features.columns))
    assert features.loc[features["customer_id"] == "C1", "preferred_time_of_day"].iloc[0] == "Morning"


def test_behaviour_profile_builder_is_deterministic() -> None:
    aggregated = CustomerBehaviourAggregator().build(_build_clean_frame()).dataframe
    features = BehaviourFeatureGenerator().build(aggregated)
    profiled = BehaviourProfileBuilder().build(features)

    assert "behaviour_profile" in profiled.columns
    assert "behaviour_profile_reason" in profiled.columns
    assert profiled.loc[profiled["customer_id"] == "C2", "behaviour_profile"].iloc[0] in {
        "Stable",
        "Moderate",
        "High Balance",
        "Aggressive",
        "Low Balance",
        "High Frequency",
        "Low Frequency",
        "Conservative",
        "Volatile",
    }
