from __future__ import annotations

from pathlib import Path

import pandas as pd

from ml.customer_behavior.aggregator import CustomerBehaviourAggregator
from ml.customer_behavior.feature_generator import BehaviourFeatureGenerator
from ml.customer_behavior.profile_builder import BehaviourProfileBuilder


class CustomerBehaviourEngine:
    """Orchestrate customer behaviour aggregation, feature generation, and profiling."""

    def __init__(self) -> None:
        self.aggregator = CustomerBehaviourAggregator()
        self.feature_generator = BehaviourFeatureGenerator()
        self.profile_builder = BehaviourProfileBuilder()

    def build(self, frame: pd.DataFrame, output_dir: str | Path) -> pd.DataFrame:
        aggregation_result = self.aggregator.build(frame)
        customer_frame = aggregation_result.dataframe
        customer_frame = self.feature_generator.build(customer_frame)
        customer_frame = self.profile_builder.build(customer_frame)

        output_path = Path(output_dir) / "customer_features.parquet"
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        customer_frame.to_parquet(output_path, index=False)
        return customer_frame