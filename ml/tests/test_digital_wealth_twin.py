from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ml.behavioral_intelligence.engine import BehavioralIntelligenceEngine
from ml.customer_behavior.engine import CustomerBehaviourEngine
from ml.digital_wealth_twin.engine import DigitalWealthTwinEngine
from ml.feature_engineering.engineer import FeatureEngineer
from ml.fraud_intelligence.engine import FraudIntelligenceEngine


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


def _build_pipeline_inputs(tmp_path: Path) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    clean_frame = _build_clean_frame()
    customer_features = CustomerBehaviourEngine().build(clean_frame, tmp_path / "behavior")
    behavioral_result = BehavioralIntelligenceEngine().build(
        clean_frame,
        tmp_path / "behavioral",
        customer_features=customer_features,
    )
    engineered = FeatureEngineer().build(clean_frame).dataframe
    fraud_result = FraudIntelligenceEngine().build(
        engineered,
        behavioral_result.normalized_features,
        tmp_path / "fraud",
        behavioral_numeric_columns=behavioral_result.numeric_columns,
    )
    fingerprints = pd.read_parquet(tmp_path / "behavioral" / "financial_fingerprints.parquet")
    return customer_features, behavioral_result.normalized_features, fingerprints, fraud_result.fraud_scores


def test_digital_wealth_twin_generates_one_row_per_customer(tmp_path: Path) -> None:
    customer_features, behavioral_features, fingerprints, fraud_scores = _build_pipeline_inputs(tmp_path)
    result = DigitalWealthTwinEngine().build(
        customer_features=customer_features,
        behavioral_features=behavioral_features,
        financial_fingerprints=fingerprints,
        fraud_scores=fraud_scores,
        output_dir=tmp_path / "twins",
    )

    assert result.customer_count == 2
    assert len(result.twins) == 2
    assert set(result.twins["customer_id"]) == {"C1", "C2"}


def test_digital_wealth_twin_includes_required_metrics(tmp_path: Path) -> None:
    customer_features, behavioral_features, fingerprints, fraud_scores = _build_pipeline_inputs(tmp_path)
    result = DigitalWealthTwinEngine().build(
        customer_features=customer_features,
        behavioral_features=behavioral_features,
        financial_fingerprints=fingerprints,
        fraud_scores=fraud_scores,
        output_dir=tmp_path / "twins",
    )

    required_metrics = {
        "spending_capacity",
        "savings_tendency",
        "financial_stability",
        "wealth_score",
        "financial_health_score",
        "investment_readiness",
        "debt_pressure_estimate",
        "spending_discipline",
        "risk_tolerance_estimate",
        "income_consistency",
        "emergency_preparedness",
        "lifestyle_category",
        "financial_personality",
    }
    assert required_metrics.issubset(set(result.twins.columns))


def test_digital_wealth_twin_is_deterministic(tmp_path: Path) -> None:
    customer_features, behavioral_features, fingerprints, fraud_scores = _build_pipeline_inputs(tmp_path)
    engine = DigitalWealthTwinEngine()
    first = engine.build(
        customer_features,
        behavioral_features,
        fingerprints,
        fraud_scores,
        tmp_path / "twins-a",
    )
    second = engine.build(
        customer_features,
        behavioral_features,
        fingerprints,
        fraud_scores,
        tmp_path / "twins-b",
    )
    pd.testing.assert_frame_equal(
        first.twins.sort_values("customer_id").reset_index(drop=True),
        second.twins.sort_values("customer_id").reset_index(drop=True),
    )


def test_digital_wealth_twin_persists_artifacts(tmp_path: Path) -> None:
    customer_features, behavioral_features, fingerprints, fraud_scores = _build_pipeline_inputs(tmp_path)
    DigitalWealthTwinEngine().build(
        customer_features,
        behavioral_features,
        fingerprints,
        fraud_scores,
        tmp_path / "twins",
    )

    assert (tmp_path / "twins" / "digital_wealth_twins.parquet").exists()
    metadata = json.loads((tmp_path / "twins" / "digital_wealth_twin_columns.json").read_text(encoding="utf-8"))
    assert metadata["twin_columns"]
    assert metadata["metric_columns"]
