from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import joblib
import pandas as pd

from ml.fraud_intelligence.anomaly_detector import AnomalyDetector
from ml.fraud_intelligence.explainability import FraudExplainabilityEngine
from ml.fraud_intelligence.feature_selector import FraudFeatureSelector
from ml.fraud_intelligence.risk_score import (
    BehaviorDeviationCalculator,
    FinancialDnaDistanceCalculator,
    FraudScoreFusion,
    RiskLevelClassifier,
)
from ml.fraud_intelligence.rule_engine import RuleBasedFraudEngine


@dataclass(frozen=True)
class FraudIntelligenceResult:
    fraud_features: pd.DataFrame
    fraud_scores: pd.DataFrame
    feature_columns: list[str]
    transaction_count: int
    flagged_count: int
    output_directory: Path


class FraudIntelligenceEngine:
    """Orchestrate unsupervised fraud intelligence scoring."""

    def __init__(self) -> None:
        self.feature_selector = FraudFeatureSelector()
        self.anomaly_detector = AnomalyDetector()
        self.rule_engine = RuleBasedFraudEngine()
        self.behavior_deviation_calculator = BehaviorDeviationCalculator()
        self.financial_dna_calculator = FinancialDnaDistanceCalculator()
        self.score_fusion = FraudScoreFusion()
        self.risk_classifier = RiskLevelClassifier()
        self.explainability_engine = FraudExplainabilityEngine()

    def build(
        self,
        transaction_frame: pd.DataFrame,
        behavioral_features: pd.DataFrame,
        output_dir: str | Path,
        behavioral_numeric_columns: list[str] | None = None,
    ) -> FraudIntelligenceResult:
        merged = self._merge_features(transaction_frame, behavioral_features)
        selection = self.feature_selector.select(merged, behavioral_columns=behavioral_numeric_columns)
        feature_matrix = self.feature_selector.build_matrix(merged, selection.feature_columns)

        anomaly_result = self.anomaly_detector.detect(feature_matrix)
        rule_result = self.rule_engine.evaluate(merged)
        behavior_deviation = self.behavior_deviation_calculator.calculate(merged)
        financial_dna_distance = self.financial_dna_calculator.calculate(merged)

        component_scores = pd.DataFrame(
            {
                "isolation_forest_score": anomaly_result.isolation_forest.normalized_scores,
                "statistical_outlier_score": anomaly_result.statistical.normalized_scores,
                "rule_based_score": rule_result.normalized_scores,
                "behavior_deviation_score": behavior_deviation.normalized_scores,
                "financial_dna_distance_score": financial_dna_distance.normalized_scores,
            },
            index=merged.index,
        )
        fusion_result = self.score_fusion.fuse(component_scores)
        component_scores["fraud_score"] = fusion_result.fraud_scores
        component_scores["risk_level"] = self.risk_classifier.classify(fusion_result.fraud_scores).values

        explanations = self.explainability_engine.explain(
            merged,
            component_scores,
            rule_result.triggered_rules,
        )

        fraud_features = merged[
            ["transaction_id", "customer_id", *selection.feature_columns]
        ].copy()
        fraud_scores = merged[["transaction_id", "customer_id"]].copy()
        fraud_scores = fraud_scores.join(component_scores.reset_index(drop=True))
        explanation_columns = [
            "transaction_id",
            "fraud_explanation",
            "fraud_reasons_json",
            "contributing_features_json",
            "is_flagged",
        ]
        fraud_scores = fraud_scores.merge(
            explanations[explanation_columns],
            on="transaction_id",
            how="left",
        )

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        fraud_features_path = output_path / "fraud_features.parquet"
        fraud_scores_path = output_path / "fraud_scores.parquet"
        fraud_model_path = output_path / "fraud_model.pkl"
        fraud_feature_columns_path = output_path / "fraud_feature_columns.json"

        fraud_features.to_parquet(fraud_features_path, index=False)
        fraud_scores.to_parquet(fraud_scores_path, index=False)

        model_payload = {
            "isolation_forest": anomaly_result.isolation_forest.model,
            "feature_columns": selection.feature_columns,
            "score_weights": self.score_fusion.weights,
            "risk_bands": self.risk_classifier.bands,
        }
        joblib.dump(model_payload, fraud_model_path)

        with fraud_feature_columns_path.open("w", encoding="utf-8") as file_handle:
            json.dump(
                {
                    "feature_columns": selection.feature_columns,
                    "transaction_columns": selection.transaction_columns,
                    "behavioral_columns": selection.behavioral_columns,
                    "component_columns": list(self.score_fusion.weights.keys()),
                },
                file_handle,
                indent=2,
                sort_keys=True,
            )

        flagged_count = int((fraud_scores["fraud_score"] >= self.explainability_engine.score_threshold).sum())
        return FraudIntelligenceResult(
            fraud_features=fraud_features,
            fraud_scores=fraud_scores,
            feature_columns=selection.feature_columns,
            transaction_count=len(fraud_scores),
            flagged_count=flagged_count,
            output_directory=output_path,
        )

    @staticmethod
    def _merge_features(
        transaction_frame: pd.DataFrame,
        behavioral_features: pd.DataFrame,
    ) -> pd.DataFrame:
        behavioral = behavioral_features.drop(
            columns=[
                column
                for column in behavioral_features.columns
                if column in {"financial_fingerprint_vector", "financial_fingerprint_signature"}
            ],
            errors="ignore",
        )
        merge_columns = [
            column
            for column in behavioral.columns
            if column != "customer_id" and column not in transaction_frame.columns
        ]
        if not merge_columns:
            return transaction_frame.copy()
        return transaction_frame.merge(
            behavioral[["customer_id", *merge_columns]],
            on="customer_id",
            how="left",
        )
