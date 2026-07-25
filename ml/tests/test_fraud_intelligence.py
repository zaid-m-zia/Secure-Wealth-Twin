from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ml.behavioral_intelligence.engine import BehavioralIntelligenceEngine
from ml.feature_engineering.engineer import FeatureEngineer
from ml.fraud_intelligence.anomaly_detector import AnomalyDetector
from ml.fraud_intelligence.engine import FraudIntelligenceEngine
from ml.fraud_intelligence.explainability import FraudExplainabilityEngine
from ml.fraud_intelligence.feature_selector import FraudFeatureSelector
from ml.fraud_intelligence.isolation_forest import IsolationForestDetector
from ml.fraud_intelligence.risk_score import FraudScoreFusion, RiskLevelClassifier
from ml.fraud_intelligence.rule_engine import RuleBasedFraudEngine
from ml.fraud_intelligence.statistical_detector import StatisticalAnomalyDetector


def _build_clean_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "transaction_id": ["T1", "T2", "T3", "T4", "T5", "T6"],
            "customer_id": ["C1", "C1", "C1", "C2", "C2", "C2"],
            "customer_dob": pd.to_datetime(["1990-01-10"] * 3 + ["1985-05-05"] * 3),
            "gender": ["F", "F", "F", "M", "M", "M"],
            "location": ["Mumbai", "Mumbai", "Pune", "Delhi", "Delhi", "Delhi"],
            "account_balance": [1000.0, 1100.0, 1200.0, 5000.0, 4800.0, 100.0],
            "transaction_date": pd.to_datetime(
                ["2016-08-01", "2016-08-02", "2016-08-04", "2016-08-01", "2016-08-03", "2016-08-07"]
            ),
            "transaction_hour": [9, 10, 18, 14, 16, 2],
            "transaction_minute": [0, 15, 45, 5, 20, 10],
            "transaction_second": [0, 0, 0, 0, 0, 0],
            "transaction_amount": [50.0, 60.0, 100.0, 800.0, 850.0, 9500.0],
        }
    )


def test_fraud_feature_selector_uses_transaction_and_behavioral_columns(tmp_path: Path) -> None:
    clean_frame = _build_clean_frame()
    engineered = FeatureEngineer().build(clean_frame).dataframe
    behavioral = BehavioralIntelligenceEngine().build(
        clean_frame,
        output_dir=tmp_path / "behavioral",
    ).normalized_features
    merged = engineered.merge(
        behavioral.drop(columns=["financial_fingerprint_vector", "financial_fingerprint_signature"], errors="ignore"),
        on="customer_id",
        how="left",
        suffixes=("", "_behavior"),
    )
    selection = FraudFeatureSelector(max_features=20).select(merged)
    assert selection.feature_columns
    assert any(column in selection.transaction_columns for column in ["transaction_amount", "transaction_hour"])
    assert selection.behavioral_columns


def test_isolation_forest_detector_returns_normalized_scores() -> None:
    matrix = pd.DataFrame(
        {
            "a": [1.0, 1.1, 0.9, 1.0, 20.0],
            "b": [2.0, 2.1, 1.9, 2.0, 30.0],
        }
    )
    result = IsolationForestDetector(n_estimators=50, random_state=42).fit_predict(matrix)
    assert len(result.normalized_scores) == 5
    assert result.normalized_scores.max() <= 100.0
    assert result.normalized_scores.argmax() == 4


def test_statistical_detector_flags_outlier_rows() -> None:
    matrix = pd.DataFrame({"amount": [10.0, 11.0, 9.0, 10.5, 100.0]})
    result = StatisticalAnomalyDetector().detect(matrix)
    assert result.normalized_scores.argmax() == 4


def test_rule_engine_detects_extreme_balance_ratio() -> None:
    engineered = FeatureEngineer().build(_build_clean_frame()).dataframe
    result = RuleBasedFraudEngine().evaluate(engineered)
    assert result.normalized_scores.max() > 0
    assert any("extreme_balance_ratio" in rules for rules in result.triggered_rules)


def test_fraud_score_fusion_and_risk_classifier() -> None:
    components = pd.DataFrame(
        {
            "isolation_forest_score": [90.0, 20.0, 50.0, 85.0],
            "behavior_deviation_score": [80.0, 10.0, 40.0, 70.0],
            "financial_dna_distance_score": [70.0, 15.0, 35.0, 75.0],
            "rule_based_score": [60.0, 5.0, 25.0, 55.0],
            "statistical_outlier_score": [75.0, 12.0, 30.0, 65.0],
        }
    )
    fused = FraudScoreFusion().fuse(components)
    risk_levels = RiskLevelClassifier().classify(fused.fraud_scores)
    assert fused.fraud_scores[0] > fused.fraud_scores[1]
    assert set(risk_levels).issubset({"Low", "Medium", "High", "Critical"})


def test_explainability_includes_reasons_for_flagged_transactions() -> None:
    engineered = FeatureEngineer().build(_build_clean_frame()).dataframe
    component_scores = pd.DataFrame(
        {
            "isolation_forest_score": [85.0] * len(engineered),
            "behavior_deviation_score": [70.0] * len(engineered),
            "financial_dna_distance_score": [65.0] * len(engineered),
            "rule_based_score": [55.0] * len(engineered),
            "statistical_outlier_score": [60.0] * len(engineered),
            "fraud_score": [78.0] * len(engineered),
            "risk_level": ["High"] * len(engineered),
        }
    )
    triggered_rules = RuleBasedFraudEngine().evaluate(engineered).triggered_rules
    explanations = FraudExplainabilityEngine().explain(engineered, component_scores, triggered_rules)
    assert "fraud_explanation" in explanations.columns
    assert explanations["is_flagged"].all()
    assert all(explanation for explanation in explanations["fraud_explanation"])


def test_fraud_intelligence_engine_persists_artifacts(tmp_path: Path) -> None:
    clean_frame = _build_clean_frame()
    engineered = FeatureEngineer().build(clean_frame).dataframe
    behavioral_result = BehavioralIntelligenceEngine().build(clean_frame, output_dir=tmp_path / "behavioral")

    result = FraudIntelligenceEngine().build(
        engineered,
        behavioral_result.normalized_features,
        output_dir=tmp_path / "fraud",
        behavioral_numeric_columns=behavioral_result.numeric_columns,
    )

    assert result.transaction_count == len(engineered)
    assert result.flagged_count >= 0
    for artifact_name in [
        "fraud_features.parquet",
        "fraud_scores.parquet",
        "fraud_model.pkl",
        "fraud_feature_columns.json",
    ]:
        assert (tmp_path / "fraud" / artifact_name).exists()

    metadata = json.loads((tmp_path / "fraud" / "fraud_feature_columns.json").read_text(encoding="utf-8"))
    scores = pd.read_parquet(tmp_path / "fraud" / "fraud_scores.parquet")
    assert metadata["feature_columns"]
    assert {"fraud_score", "risk_level", "fraud_explanation"}.issubset(set(scores.columns))


def test_anomaly_detector_coordinates_methods() -> None:
    matrix = pd.DataFrame({"a": [1.0, 1.1, 0.9, 1.0, 15.0], "b": [2.0, 2.2, 1.8, 2.1, 25.0]})
    result = AnomalyDetector().detect(matrix)
    assert len(result.isolation_forest.normalized_scores) == 5
    assert len(result.statistical.normalized_scores) == 5
