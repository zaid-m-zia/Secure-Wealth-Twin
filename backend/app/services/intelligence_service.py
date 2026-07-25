"""Read-only adapters that expose completed ML artifacts through the API layer."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Optional

import pandas as pd


ARTIFACT_DIR = Path(__file__).resolve().parents[3] / "ml" / "artifacts"


@lru_cache(maxsize=None)
def _artifact(name: str) -> pd.DataFrame:
    path = ARTIFACT_DIR / name
    if not path.exists():
        raise FileNotFoundError(f"Required intelligence artifact is unavailable: {name}")
    return pd.read_parquet(path)


def _json_value(value: Any) -> Any:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    if hasattr(value, "item"):
        value = value.item()
    if isinstance(value, str) and value[:1] in {"{", "["}:
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value
    return value


def _record(frame: pd.DataFrame, customer_id: str, *, key: str = "customer_id") -> Optional[dict[str, Any]]:
    rows = frame.loc[frame[key].astype(str) == customer_id]
    if rows.empty:
        return None
    return {column: _json_value(value) for column, value in rows.iloc[0].to_dict().items()}


def _records(frame: pd.DataFrame, customer_id: str, *, key: str = "customer_id") -> list[dict[str, Any]]:
    rows = frame.loc[frame[key].astype(str) == customer_id]
    return [{column: _json_value(value) for column, value in row.items()} for row in rows.to_dict("records")]


class IntelligenceService:
    """Single service boundary for the immutable outputs of completed ML phases."""

    def customer_behavior(self, customer_id: str) -> Optional[dict[str, Any]]:
        return _record(_artifact("customer_features.parquet"), customer_id)

    def behavioral_intelligence(self, customer_id: str) -> Optional[dict[str, Any]]:
        return _record(_artifact("behavioral_intelligence_features.parquet"), customer_id)

    def wealth_twin(self, customer_id: str) -> Optional[dict[str, Any]]:
        return _record(_artifact("digital_wealth_twins.parquet"), customer_id)

    def fraud_score(self, transaction_id: str) -> Optional[dict[str, Any]]:
        return _record(_artifact("fraud_scores.parquet"), transaction_id, key="transaction_id")

    def fraud_history(self, customer_id: str) -> list[dict[str, Any]]:
        return _records(_artifact("fraud_scores.parquet"), customer_id)

    def recommendations(self, customer_id: str) -> list[dict[str, Any]]:
        return _records(_artifact("financial_recommendations.parquet"), customer_id)

    def decision(self, customer_id: str) -> Optional[dict[str, Any]]:
        return _record(_artifact("agentic_ai_decisions.parquet"), customer_id)

    def customer_intelligence(self, customer_id: str) -> Optional[dict[str, Any]]:
        behavior = self.customer_behavior(customer_id)
        if behavior is None:
            return None
        return {
            "customer_id": customer_id,
            "behavior": behavior,
            "behavioral_intelligence": self.behavioral_intelligence(customer_id),
            "wealth_twin": self.wealth_twin(customer_id),
            "recommendations": self.recommendations(customer_id),
            "agentic_decision": self.decision(customer_id),
        }

    def fraud_analytics(self, customer_id: Optional[str] = None) -> dict[str, Any]:
        frame = _artifact("fraud_scores.parquet")
        if customer_id:
            frame = frame.loc[frame.customer_id.astype(str) == customer_id]
        if frame.empty:
            return {"transactions_analyzed": 0, "flagged_transactions": 0, "average_fraud_score": 0.0, "risk_levels": {}}
        return {
            "transactions_analyzed": len(frame),
            "flagged_transactions": int(frame["is_flagged"].sum()),
            "average_fraud_score": round(float(frame["fraud_score"].mean()), 2),
            "maximum_fraud_score": round(float(frame["fraud_score"].max()), 2),
            "risk_levels": {str(key): int(value) for key, value in frame["risk_level"].value_counts().items()},
        }

    def wealth_analytics(self) -> dict[str, Any]:
        frame = _artifact("digital_wealth_twins.parquet")
        return {
            "customers": len(frame),
            "average_financial_health_score": round(float(frame["financial_health_score"].mean()), 2),
            "average_wealth_score": round(float(frame["wealth_score"].mean()), 2),
            "lifestyle_distribution": {str(key): int(value) for key, value in frame["lifestyle_category"].value_counts().items()},
        }

    def behavior_analytics(self) -> dict[str, Any]:
        frame = _artifact("behavioral_intelligence_features.parquet")
        return {
            "customers": len(frame),
            "average_spending_velocity": round(float(frame["spending_velocity"].mean()), 4),
            "average_income_stability_score": round(float(frame["income_stability_score"].mean()), 4),
        }

    def recommendation_analytics(self) -> dict[str, Any]:
        frame = _artifact("financial_recommendations.parquet")
        return {
            "recommendations": len(frame),
            "customers": int(frame["customer_id"].nunique()),
            "priority_distribution": {str(key): int(value) for key, value in frame["priority"].value_counts().items()},
            "type_distribution": {str(key): int(value) for key, value in frame["recommendation_type"].value_counts().items()},
        }

    def transaction_analytics(self) -> dict[str, Any]:
        frame = _artifact("fraud_features.parquet")
        return {
            "transactions": len(frame),
            "customers": int(frame["customer_id"].nunique()),
            "total_transaction_amount": round(float(frame["transaction_amount"].sum()), 2),
            "average_transaction_amount": round(float(frame["transaction_amount"].mean()), 2),
        }

    def dashboard(self, customer_id: str) -> Optional[dict[str, Any]]:
        twin = self.wealth_twin(customer_id)
        decision = self.decision(customer_id)
        behavior = self.customer_behavior(customer_id)
        if twin is None or behavior is None:
            return None
        fraud = self.fraud_analytics(customer_id)
        return {
            "customer_id": customer_id,
            "cards": {
                "financial_health_score": twin.get("financial_health_score"),
                "wealth_score": twin.get("wealth_score"),
                "fraud_risk": fraud["average_fraud_score"],
                "total_transactions": behavior.get("total_transactions"),
            },
            "kpis": {"fraud": fraud, "financial_health": twin.get("financial_health_score"), "decision_confidence": decision.get("confidence_score") if decision else None},
            "charts": {"spending": behavior, "risk": fraud, "lifestyle": twin.get("lifestyle_category")},
            "recommendations": self.recommendations(customer_id),
            "decision": decision,
        }

    def report(self, customer_id: str) -> Optional[dict[str, Any]]:
        intelligence = self.customer_intelligence(customer_id)
        if intelligence is None:
            return None
        intelligence["fraud_summary"] = self.fraud_analytics(customer_id)
        intelligence["report_format"] = "structured_json_v1"
        return intelligence
