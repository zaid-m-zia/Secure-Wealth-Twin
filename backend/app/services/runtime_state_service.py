"""Read projections for the intelligence state persisted by runtime inference.

Dashboard and analytics deliberately read these database records instead of the
immutable training artifacts.  RuntimeInferenceService remains the only place
that calculates and persists customer intelligence.
"""
from __future__ import annotations

import json
from collections import Counter
from typing import Any, Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.agent_memory import AgentMemory
from app.models.behavior_profile import BehaviorProfile
from app.models.customer import Customer
from app.models.digital_wealth_twin import DigitalWealthTwin
from app.models.fraud import FraudAnalysis
from app.models.recommendation import Recommendation
from app.models.transaction import Transaction


class RuntimeStateService:
    """Project the current persisted customer intelligence for API consumers."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def dashboard(self, customer_id: str) -> Optional[dict[str, Any]]:
        customer = self.session.get(Customer, customer_id)
        if customer is None:
            return None

        behavior = self.session.get(BehaviorProfile, customer_id)
        twin = self.session.get(DigitalWealthTwin, customer_id)
        fraud = self.fraud_analytics(customer_id)
        recommendations = self._recommendations(customer_id)
        decision = self._decision(customer_id)
        financial_dna = twin.financial_dna_json if twin and twin.financial_dna_json else {}
        transaction_count = self._transaction_count(customer_id)

        return {
            "customer_id": customer_id,
            "cards": {
                "financial_health_score": twin.health_score_placeholder if twin else None,
                "wealth_score": financial_dna.get("wealth_score"),
                "fraud_risk": fraud["average_fraud_score"],
                "total_transactions": transaction_count,
                "account_balance": customer.account_balance,
            },
            "kpis": {
                "fraud": fraud,
                "financial_health": twin.health_score_placeholder if twin else None,
                "decision_confidence": decision.get("confidence_score") if decision else None,
            },
            "charts": {
                "spending": financial_dna,
                "risk": fraud,
                "lifestyle": twin.wealth_summary if twin else None,
            },
            "behavior": self._behavior(customer_id, behavior),
            "recommendations": recommendations,
            "decision": decision,
        }

    def behavior_analytics(self, customer_id: Optional[str] = None) -> dict[str, Any]:
        if customer_id:
            customer = self.session.get(Customer, customer_id)
            if customer is None:
                return self._empty_behavior(customer_id)
            return self._behavior(customer_id, self.session.get(BehaviorProfile, customer_id))

        profiles = self.session.execute(select(BehaviorProfile)).scalars().all()
        averages = [profile.avg_transaction_amount for profile in profiles if profile.avg_transaction_amount is not None]
        frequencies = [profile.transaction_frequency for profile in profiles if profile.transaction_frequency is not None]
        return {
            "customers": len(profiles),
            "average_transaction_amount": round(sum(averages) / len(averages), 2) if averages else 0.0,
            "average_transaction_frequency": round(sum(frequencies) / len(frequencies), 2) if frequencies else 0.0,
        }

    def fraud_analytics(self, customer_id: Optional[str] = None) -> dict[str, Any]:
        statement = select(FraudAnalysis)
        if customer_id:
            statement = statement.where(FraudAnalysis.customer_id == customer_id)
        analyses = self.session.execute(statement).scalars().all()
        scores = [analysis.fraud_score_placeholder for analysis in analyses if analysis.fraud_score_placeholder is not None]
        levels = Counter(
            analysis.anomaly_reason_placeholder
            for analysis in analyses
            if analysis.anomaly_reason_placeholder
        )
        return {
            "transactions_analyzed": len(analyses),
            "flagged_transactions": sum(score >= 31 for score in scores),
            "average_fraud_score": round(sum(scores) / len(scores), 2) if scores else 0.0,
            "maximum_fraud_score": round(max(scores), 2) if scores else 0.0,
            "risk_levels": dict(levels),
        }

    def wealth_analytics(self, customer_id: Optional[str] = None) -> dict[str, Any]:
        if customer_id:
            customer = self.session.get(Customer, customer_id)
            twin = self.session.get(DigitalWealthTwin, customer_id)
            if customer is None:
                return {"customer_id": customer_id, "account_balance": None, "financial_health_score": None, "wealth_score": None, "financial_personality": None}
            financial_dna = twin.financial_dna_json if twin and twin.financial_dna_json else {}
            return {
                "customer_id": customer_id,
                "account_balance": customer.account_balance,
                "financial_health_score": twin.health_score_placeholder if twin else None,
                "wealth_score": financial_dna.get("wealth_score"),
                "financial_personality": twin.wealth_summary if twin else None,
                "financial_dna": financial_dna,
            }

        twins = self.session.execute(select(DigitalWealthTwin)).scalars().all()
        health_scores = [twin.health_score_placeholder for twin in twins if twin.health_score_placeholder is not None]
        wealth_scores = [float(twin.financial_dna_json["wealth_score"]) for twin in twins if twin.financial_dna_json and twin.financial_dna_json.get("wealth_score") is not None]
        return {
            "customers": len(twins),
            "average_financial_health_score": round(sum(health_scores) / len(health_scores), 2) if health_scores else 0.0,
            "average_wealth_score": round(sum(wealth_scores) / len(wealth_scores), 2) if wealth_scores else 0.0,
        }

    def transaction_analytics(self, customer_id: Optional[str] = None) -> dict[str, Any]:
        statement = select(Transaction)
        if customer_id:
            statement = statement.where(Transaction.customer_id == customer_id)
        transactions = self.session.execute(statement).scalars().all()
        income_types = {"deposit", "salary", "income", "refund"}
        income = sum(transaction.transaction_amount for transaction in transactions if transaction.transaction_type in income_types)
        expenses = sum(transaction.transaction_amount for transaction in transactions if transaction.transaction_type not in income_types)
        amounts = [transaction.transaction_amount for transaction in transactions]
        customer = self.session.get(Customer, customer_id) if customer_id else None
        return {
            "customer_id": customer_id,
            "account_balance": customer.account_balance if customer else None,
            "transactions": len(transactions),
            "total_transaction_amount": round(sum(amounts), 2),
            "average_transaction_amount": round(sum(amounts) / len(amounts), 2) if amounts else 0.0,
            "income": round(income, 2),
            "expenses": round(expenses, 2),
            "net_cashflow": round(income - expenses, 2),
            "by_category": dict(Counter(transaction.category for transaction in transactions)),
        }

    def recommendation_analytics(self, customer_id: Optional[str] = None) -> dict[str, Any]:
        statement = select(Recommendation)
        if customer_id:
            statement = statement.where(Recommendation.customer_id == customer_id)
        recommendations = self.session.execute(statement).scalars().all()
        return {
            "customer_id": customer_id,
            "recommendations": len(recommendations),
            "priority_distribution": dict(Counter(item.priority for item in recommendations)),
            "status_distribution": dict(Counter(item.status for item in recommendations)),
        }

    def _transaction_count(self, customer_id: str) -> int:
        return int(self.session.scalar(select(func.count(Transaction.transaction_id)).where(Transaction.customer_id == customer_id)) or 0)

    def _behavior(self, customer_id: str, behavior: Optional[BehaviorProfile]) -> dict[str, Any]:
        risk_flags = behavior.risk_flags_json if behavior and behavior.risk_flags_json else {}
        return {
            "customer_id": customer_id,
            "average_transaction_amount": behavior.avg_transaction_amount if behavior else None,
            "transaction_frequency": behavior.transaction_frequency if behavior else 0.0,
            "latest_risk": risk_flags.get("latest_risk"),
            "latest_fraud_score": risk_flags.get("latest_score"),
            "last_updated": behavior.last_updated if behavior else None,
        }

    def _empty_behavior(self, customer_id: str) -> dict[str, Any]:
        return {
            "customer_id": customer_id,
            "average_transaction_amount": None,
            "transaction_frequency": 0.0,
            "latest_risk": None,
            "latest_fraud_score": None,
            "last_updated": None,
        }

    def _recommendations(self, customer_id: str) -> list[dict[str, Any]]:
        recommendations = self.session.execute(
            select(Recommendation)
            .where(Recommendation.customer_id == customer_id)
            .order_by(Recommendation.updated_at.desc())
        ).scalars().all()
        return [
            {"recommendation": item.recommendation_text, "priority": item.priority, "status": item.status}
            for item in recommendations
        ]

    def _decision(self, customer_id: str) -> Optional[dict[str, Any]]:
        memory = self.session.execute(select(AgentMemory).where(AgentMemory.customer_id == customer_id)).scalars().first()
        if memory is None or not memory.conversation_memory:
            return None
        try:
            value = json.loads(memory.conversation_memory)
        except json.JSONDecodeError:
            return None
        return value if isinstance(value, dict) else None
