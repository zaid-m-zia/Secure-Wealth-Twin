from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ml.agentic_ai.engine import AgenticAIDecisionEngine


def _inputs() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    customers = pd.DataFrame({"customer_id": ["C1", "C2"], "behaviour_profile": ["Volatile", "Stable"]})
    behavioral = pd.DataFrame({"customer_id": ["C1", "C2"], "income_stability_score": [0.25, 0.90]})
    fraud = pd.DataFrame(
        {"customer_id": ["C1", "C1", "C2"], "fraud_score": [92.0, 55.0, 8.0], "is_flagged": [True, True, False]}
    )
    twins = pd.DataFrame(
        {
            "customer_id": ["C1", "C2"], "financial_health_score": [30.0, 80.0],
            "emergency_preparedness": [10.0, 100.0], "debt_pressure_estimate": [82.0, 18.0],
            "investment_readiness": [30.0, 82.0], "spending_capacity": [12.0, 76.0],
        }
    )
    recommendations = pd.DataFrame(
        {
            "customer_id": ["C1", "C1", "C1", "C2", "C2"],
            "recommendation_type": ["investment_readiness", "emergency_fund", "debt_reduction", "investment_readiness", "budget_allocation"],
            "recommendation": ["Start investing", "Build emergency fund", "Reduce debt", "Start diversified investing", "Adopt a budget"],
            "confidence_score": [0.80, 0.95, 0.90, 0.85, 0.70],
            "priority": ["Medium", "Critical", "Critical", "Medium", "Low"],
            "rank": [3, 1, 2, 1, 2],
            "supporting_metrics": ["{}"] * 5,
        }
    )
    return customers, behavioral, fraud, twins, recommendations


def test_agentic_engine_generates_required_decision_contract_and_artifacts(tmp_path: Path) -> None:
    result = AgenticAIDecisionEngine().build(*_inputs(), output_dir=tmp_path)

    required = {
        "customer_id", "final_decision", "decision_priority", "confidence_score", "reasoning_chain",
        "supporting_evidence", "recommended_actions", "risk_summary", "financial_summary", "timestamp",
    }
    assert result.customer_count == 2
    assert result.escalated_count == 1
    assert required.issubset(result.decisions.columns)
    assert result.decisions["confidence_score"].between(0.0, 1.0).all()
    assert (tmp_path / "agentic_ai_decisions.parquet").exists()
    metadata = json.loads((tmp_path / "agentic_ai_metadata.json").read_text(encoding="utf-8"))
    assert "financial_decision_intelligence" in metadata["input_sources"]


def test_critical_fraud_escalation_prevents_investment_action(tmp_path: Path) -> None:
    result = AgenticAIDecisionEngine().build(*_inputs(), output_dir=tmp_path)
    c1 = result.decisions.set_index("customer_id").loc["C1"]

    actions = json.loads(c1["recommended_actions"])
    risk = json.loads(c1["risk_summary"])
    assert c1["decision_priority"] == "Critical"
    assert risk["escalated"] is True
    assert "Start investing" not in actions
    assert "Verify recent transactions immediately" in actions


def test_agentic_engine_rejects_recommendations_without_ranking(tmp_path: Path) -> None:
    customers, behavioral, fraud, twins, recommendations = _inputs()
    try:
        AgenticAIDecisionEngine().build(customers, behavioral, fraud, twins, recommendations.drop(columns=["rank"]), tmp_path)
    except ValueError as error:
        assert "rank" in str(error)
    else:
        raise AssertionError("Expected missing recommendation ranking validation error")
