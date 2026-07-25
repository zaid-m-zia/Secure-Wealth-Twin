from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ml.financial_decision_intelligence.engine import FinancialDecisionIntelligenceEngine


def _inputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    customer_features = pd.DataFrame(
        {
            "customer_id": ["C1", "C2"],
            "average_monthly_spending": [1000.0, 300.0],
            "estimated_monthly_salary": [1500.0, 1000.0],
            "average_account_balance": [500.0, 3000.0],
            "expense_ratio": [0.67, 0.30],
            "balance_utilisation": [0.80, 0.25],
        }
    )
    behavioral_features = pd.DataFrame(
        {
            "customer_id": ["C1", "C2"],
            "income_stability_score": [0.30, 0.90],
            "spending_volatility_index": [0.80, 0.10],
        }
    )
    fraud_scores = pd.DataFrame(
        {
            "transaction_id": ["T1", "T2", "T3", "T4"],
            "customer_id": ["C1", "C1", "C2", "C2"],
            "fraud_score": [70.0, 50.0, 5.0, 10.0],
        }
    )
    wealth_twins = pd.DataFrame(
        {
            "customer_id": ["C1", "C2"],
            "financial_health_score": [35.0, 82.0],
            "emergency_preparedness": [8.0, 100.0],
            "savings_tendency": [25.0, 80.0],
            "spending_capacity": [15.0, 70.0],
            "investment_readiness": [30.0, 80.0],
            "debt_pressure_estimate": [85.0, 20.0],
            "risk_tolerance_estimate": [45.0, 60.0],
        }
    )
    return customer_features, behavioral_features, fraud_scores, wealth_twins


def test_engine_generates_explainable_recommendations_and_artifacts(tmp_path: Path) -> None:
    result = FinancialDecisionIntelligenceEngine().build(*_inputs(), output_dir=tmp_path)

    assert result.customer_count == 2
    assert result.recommendation_count >= 8
    required = {"recommendation", "confidence_score", "priority", "explanation", "supporting_metrics"}
    assert required.issubset(result.recommendations.columns)
    assert result.recommendations["confidence_score"].between(0.0, 1.0).all()
    assert {"Build a six-month emergency fund", "Prioritize a debt reduction strategy"}.issubset(
        set(result.recommendations["recommendation"])
    )
    assert (tmp_path / "financial_recommendations.parquet").exists()
    metadata = json.loads((tmp_path / "financial_decision_intelligence_metadata.json").read_text(encoding="utf-8"))
    assert metadata["input_sources"] == [
        "customer_behaviour", "behavioral_intelligence", "fraud_intelligence", "digital_wealth_twin"
    ]


def test_engine_ranks_critical_actions_first_for_each_customer(tmp_path: Path) -> None:
    result = FinancialDecisionIntelligenceEngine().build(*_inputs(), output_dir=tmp_path)
    c1 = result.recommendations[result.recommendations["customer_id"] == "C1"].sort_values("rank")
    assert c1.iloc[0]["priority"] == "Critical"
    assert c1["rank"].tolist() == list(range(1, len(c1) + 1))


def test_engine_rejects_incomplete_fraud_input(tmp_path: Path) -> None:
    customer_features, behavioral_features, fraud_scores, wealth_twins = _inputs()
    try:
        FinancialDecisionIntelligenceEngine().build(
            customer_features,
            behavioral_features,
            fraud_scores.drop(columns=["fraud_score"]),
            wealth_twins,
            tmp_path,
        )
    except ValueError as error:
        assert "fraud_score" in str(error)
    else:
        raise AssertionError("Expected missing fraud_score validation error")
