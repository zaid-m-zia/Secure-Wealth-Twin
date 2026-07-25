from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from ml.digital_wealth_twin.financial_health import FinancialHealthAnalyzer
from ml.digital_wealth_twin.financial_personality import FinancialPersonalityAnalyzer
from ml.digital_wealth_twin.investment_readiness import InvestmentReadinessAnalyzer
from ml.digital_wealth_twin.lifestyle_analyzer import LifestyleAnalyzer
from ml.digital_wealth_twin.profile_builder import WealthTwinProfileBuilder
from ml.digital_wealth_twin.savings_behavior import SavingsBehaviorAnalyzer
from ml.digital_wealth_twin.spending_capacity import SpendingCapacityAnalyzer
from ml.digital_wealth_twin.wealth_metrics import WealthMetricsCalculator
from ml.digital_wealth_twin.wealth_state import WealthStateBuilder


@dataclass(frozen=True)
class DigitalWealthTwinResult:
    twins: pd.DataFrame
    twin_columns: list[str]
    metric_columns: list[str]
    customer_count: int
    output_directory: Path


class DigitalWealthTwinEngine:
    """Orchestrate Digital Wealth Twin construction for every customer."""

    def __init__(self) -> None:
        self.wealth_state_builder = WealthStateBuilder()
        self.spending_capacity_analyzer = SpendingCapacityAnalyzer()
        self.savings_behavior_analyzer = SavingsBehaviorAnalyzer()
        self.wealth_metrics_calculator = WealthMetricsCalculator()
        self.financial_health_analyzer = FinancialHealthAnalyzer()
        self.investment_readiness_analyzer = InvestmentReadinessAnalyzer()
        self.lifestyle_analyzer = LifestyleAnalyzer()
        self.financial_personality_analyzer = FinancialPersonalityAnalyzer()
        self.profile_builder = WealthTwinProfileBuilder()

    def build(
        self,
        customer_features: pd.DataFrame,
        behavioral_features: pd.DataFrame,
        financial_fingerprints: pd.DataFrame,
        fraud_scores: pd.DataFrame,
        output_dir: str | Path,
    ) -> DigitalWealthTwinResult:
        fraud_summary = self.wealth_state_builder.aggregate_fraud_scores(fraud_scores)
        state = self.wealth_state_builder.build(
            customer_features=customer_features,
            behavioral_features=behavioral_features,
            financial_fingerprints=financial_fingerprints,
            fraud_customer_summary=fraud_summary,
        )

        state = self._merge_metric_frame(state, self.spending_capacity_analyzer.build(state))
        state = self._merge_metric_frame(state, self.savings_behavior_analyzer.build(state))
        state = self._merge_metric_frame(state, self.profile_builder.build(state))
        state = self._merge_metric_frame(state, self.wealth_metrics_calculator.build(state))
        state = self._merge_metric_frame(state, self.financial_health_analyzer.build(state))
        state = self._merge_metric_frame(state, self.investment_readiness_analyzer.build(state))
        state = self._merge_metric_frame(state, self.lifestyle_analyzer.build(state))
        state = self._merge_metric_frame(state, self.financial_personality_analyzer.build(state))

        twin_columns = self.profile_builder.select_twin_columns(state)
        twins = state[twin_columns].copy()

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        twins_path = output_path / "digital_wealth_twins.parquet"
        twin_columns_path = output_path / "digital_wealth_twin_columns.json"

        twins.to_parquet(twins_path, index=False)
        metric_columns = [column for column in self.profile_builder.twin_metric_columns if column in twins.columns]
        with twin_columns_path.open("w", encoding="utf-8") as file_handle:
            json.dump(
                {
                    "twin_columns": twin_columns,
                    "metric_columns": metric_columns,
                    "profile_columns": [column for column in twin_columns if column not in metric_columns],
                },
                file_handle,
                indent=2,
                sort_keys=True,
            )

        return DigitalWealthTwinResult(
            twins=twins,
            twin_columns=twin_columns,
            metric_columns=metric_columns,
            customer_count=int(twins["customer_id"].nunique()),
            output_directory=output_path,
        )

    @staticmethod
    def _merge_metric_frame(state: pd.DataFrame, metric_frame: pd.DataFrame) -> pd.DataFrame:
        merge_columns = [column for column in metric_frame.columns if column != "customer_id"]
        if not merge_columns:
            return state
        updated = state.drop(columns=[column for column in merge_columns if column in state.columns], errors="ignore")
        return updated.merge(metric_frame, on="customer_id", how="left")
