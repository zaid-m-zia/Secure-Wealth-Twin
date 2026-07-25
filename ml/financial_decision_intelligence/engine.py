from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from ml.financial_decision_intelligence.budgeting_engine import BudgetingEngine
from ml.financial_decision_intelligence.debt_optimizer import DebtOptimizer
from ml.financial_decision_intelligence.explanation_engine import DecisionExplanationEngine
from ml.financial_decision_intelligence.financial_goal_analyzer import FinancialGoalAnalyzer
from ml.financial_decision_intelligence.financial_priority_engine import FinancialPriorityEngine
from ml.financial_decision_intelligence.investment_recommender import InvestmentRecommender
from ml.financial_decision_intelligence.recommendation_ranker import RecommendationRanker
from ml.financial_decision_intelligence.savings_recommender import SavingsRecommender

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class FinancialDecisionIntelligenceResult:
    """Persisted output of the Financial Decision Intelligence Engine."""

    recommendations: pd.DataFrame
    customer_count: int
    recommendation_count: int
    output_directory: Path


class FinancialDecisionIntelligenceEngine:
    """Generate ranked financial actions from the four upstream intelligence engines."""

    required_customer_column = "customer_id"

    def __init__(self) -> None:
        self.goal_analyzer = FinancialGoalAnalyzer()
        self.budgeting_engine = BudgetingEngine()
        self.savings_recommender = SavingsRecommender()
        self.investment_recommender = InvestmentRecommender()
        self.debt_optimizer = DebtOptimizer()
        self.priority_engine = FinancialPriorityEngine()
        self.ranker = RecommendationRanker()
        self.explanation_engine = DecisionExplanationEngine()

    def build(
        self,
        customer_features: pd.DataFrame,
        behavioral_features: pd.DataFrame,
        fraud_scores: pd.DataFrame,
        wealth_twins: pd.DataFrame,
        output_dir: str | Path,
    ) -> FinancialDecisionIntelligenceResult:
        """Build recommendations and persist new Sprint 4B-only artifacts."""
        state = self._build_customer_state(customer_features, behavioral_features, fraud_scores, wealth_twins)
        records: list[dict[str, Any]] = []
        for _, customer in state.iterrows():
            drafts = self._recommend_for_customer(customer)
            for draft in drafts:
                finalized = self.explanation_engine.finalize(draft)
                records.append(
                    {
                        "customer_id": str(customer["customer_id"]),
                        "recommendation_type": finalized["recommendation_type"],
                        "recommendation": finalized["recommendation"],
                        "confidence_score": finalized["confidence_score"],
                        "priority": finalized["priority"],
                        "priority_score": finalized["priority_score"],
                        "rank": finalized["rank"],
                        "explanation": finalized["explanation"],
                        "supporting_metrics": json.dumps(finalized["supporting_metrics"], sort_keys=True),
                    }
                )

        recommendations = pd.DataFrame(records)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        recommendations.to_parquet(output_path / "financial_recommendations.parquet", index=False)
        with (output_path / "financial_decision_intelligence_metadata.json").open("w", encoding="utf-8") as file_handle:
            json.dump(
                {
                    "artifact": "financial_recommendations.parquet",
                    "customer_count": int(state["customer_id"].nunique()),
                    "recommendation_count": len(recommendations),
                    "required_recommendation_fields": sorted(DecisionExplanationEngine.required_fields),
                    "input_sources": [
                        "customer_behaviour",
                        "behavioral_intelligence",
                        "fraud_intelligence",
                        "digital_wealth_twin",
                    ],
                },
                file_handle,
                indent=2,
                sort_keys=True,
            )
        LOGGER.info("Generated %s financial recommendations for %s customers", len(recommendations), len(state))
        return FinancialDecisionIntelligenceResult(
            recommendations=recommendations,
            customer_count=int(state["customer_id"].nunique()),
            recommendation_count=len(recommendations),
            output_directory=output_path,
        )

    def _recommend_for_customer(self, customer: pd.Series) -> list[dict[str, Any]]:
        drafts = (
            self.goal_analyzer.analyze(customer)
            + self.budgeting_engine.recommend(customer)
            + self.savings_recommender.recommend(customer)
            + self.investment_recommender.recommend(customer)
            + self.debt_optimizer.recommend(customer)
        )
        return self.ranker.rank(self.priority_engine.prioritize(drafts))

    def _build_customer_state(
        self,
        customer_features: pd.DataFrame,
        behavioral_features: pd.DataFrame,
        fraud_scores: pd.DataFrame,
        wealth_twins: pd.DataFrame,
    ) -> pd.DataFrame:
        frames = {
            "customer_features": customer_features,
            "behavioral_features": behavioral_features,
            "fraud_scores": fraud_scores,
            "wealth_twins": wealth_twins,
        }
        for name, frame in frames.items():
            if self.required_customer_column not in frame.columns:
                raise ValueError(f"{name} must contain customer_id")

        state = customer_features.copy()
        behavioral = behavioral_features.drop(columns=["financial_fingerprint_vector", "financial_fingerprint_signature"], errors="ignore")
        state = self._merge_new_columns(state, behavioral)
        fraud_summary = self._summarize_fraud(fraud_scores)
        state = self._merge_new_columns(state, fraud_summary)
        state = self._merge_new_columns(state, wealth_twins)
        return state.fillna(0.0)

    @staticmethod
    def _merge_new_columns(state: pd.DataFrame, incoming: pd.DataFrame) -> pd.DataFrame:
        new_columns = [column for column in incoming.columns if column != "customer_id" and column not in state.columns]
        if not new_columns:
            return state
        return state.merge(incoming[["customer_id", *new_columns]], on="customer_id", how="left")

    @staticmethod
    def _summarize_fraud(fraud_scores: pd.DataFrame) -> pd.DataFrame:
        required_columns = {"customer_id", "fraud_score"}
        missing = required_columns.difference(fraud_scores.columns)
        if missing:
            raise ValueError(f"fraud_scores is missing required columns: {sorted(missing)}")
        return fraud_scores.groupby("customer_id", sort=False).agg(
            average_fraud_score=("fraud_score", "mean"),
            maximum_fraud_score=("fraud_score", "max"),
        ).reset_index()
