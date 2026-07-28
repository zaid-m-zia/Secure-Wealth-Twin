"""Runtime-only fraud inference using the persisted Isolation Forest artifact.

This service never invokes the training pipeline or writes ML artifacts.
"""
from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.models.behavior_profile import BehaviorProfile
from app.models.fraud import FraudAnalysis
from app.models.transaction import Transaction
from app.models.digital_wealth_twin import DigitalWealthTwin
from app.models.recommendation import Recommendation
from app.models.agent_memory import AgentMemory
from ml.fraud_intelligence.explainability import FraudExplainabilityEngine
from ml.fraud_intelligence.risk_score import BehaviorDeviationCalculator, FraudScoreFusion, RiskLevelClassifier
from ml.fraud_intelligence.rule_engine import RuleBasedFraudEngine
from ml.digital_wealth_twin.savings_behavior import SavingsBehaviorAnalyzer
from ml.digital_wealth_twin.wealth_metrics import WealthMetricsCalculator
from ml.digital_wealth_twin.financial_health import FinancialHealthAnalyzer
from ml.digital_wealth_twin.investment_readiness import InvestmentReadinessAnalyzer
from ml.digital_wealth_twin.financial_personality import FinancialPersonalityAnalyzer
from ml.financial_decision_intelligence.budgeting_engine import BudgetingEngine
from ml.financial_decision_intelligence.savings_recommender import SavingsRecommender
from ml.financial_decision_intelligence.investment_recommender import InvestmentRecommender
from ml.financial_decision_intelligence.debt_optimizer import DebtOptimizer
from ml.financial_decision_intelligence.financial_priority_engine import FinancialPriorityEngine
from ml.financial_decision_intelligence.recommendation_ranker import RecommendationRanker
from ml.financial_decision_intelligence.explanation_engine import DecisionExplanationEngine
from ml.agentic_ai.engine import AgenticAIDecisionEngine

ARTIFACT_DIR = Path(__file__).resolve().parents[3] / "ml" / "artifacts"
LOGGER = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def load_fraud_model() -> dict[str, Any]:
    """Load the completed model once per application process."""
    return joblib.load(ARTIFACT_DIR / "fraud_model.pkl")


def warm_runtime() -> None:
    """Eagerly initialize the trained inference artifact during application startup."""
    try:
        load_fraud_model()
    except FileNotFoundError:
        LOGGER.warning("Runtime fraud artifact is unavailable; inference will remain disabled until artifacts are mounted.")


class RuntimeInferenceService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.rules = RuleBasedFraudEngine()
        self.explainability = FraudExplainabilityEngine()
        self.deviation = BehaviorDeviationCalculator()
        self.fusion = FraudScoreFusion()
        self.risk_levels = RiskLevelClassifier()

    def assess_transaction(self, transaction: Transaction) -> FraudAnalysis:
        history = self.session.execute(select(Transaction).where(Transaction.customer_id == transaction.customer_id)).scalars().all()
        amounts = [item.transaction_amount for item in history]
        baseline = float(np.mean(amounts)) if amounts else transaction.transaction_amount
        standard_deviation = float(np.std(amounts)) if len(amounts) > 1 else 0.0
        balance = float(transaction.customer.account_balance) if transaction.customer else 0.0
        hour = transaction.transaction_time.hour
        frame = pd.DataFrame([{
            "transaction_id": transaction.transaction_id, "transaction_amount": transaction.transaction_amount,
            "average_transaction_amount": baseline, "std_transaction_amount": standard_deviation,
            "transaction_hour": hour, "transaction_balance_ratio": transaction.transaction_amount / max(balance, 1.0),
            "balance_after_transaction": balance - transaction.transaction_amount,
            "weekend_flag": int(transaction.transaction_date.weekday() >= 5),
            "large_transaction_flag": int(transaction.transaction_amount > baseline * 2),
            "very_large_transaction_flag": int(transaction.transaction_amount > baseline * 4),
            "rapid_transaction_flag": 0, "low_balance_flag": int(balance <= transaction.transaction_amount),
            "high_spending_flag": int(transaction.transaction_amount > baseline * 2),
            "new_customer_flag": int(len(history) <= 2), "dormant_customer_flag": 0,
        }])
        model_payload = load_fraud_model()
        columns = model_payload["feature_columns"]
        matrix = pd.DataFrame(0.0, index=frame.index, columns=columns)
        for column in columns:
            if column in frame:
                matrix[column] = pd.to_numeric(frame[column], errors="coerce").fillna(0.0)
        prediction = int(model_payload["isolation_forest"].predict(matrix)[0])
        isolation_signal = 100.0 if prediction == -1 else 0.0
        behavior_signal = float(self.deviation.calculate(frame).normalized_scores[0])
        rule_result = self.rules.evaluate(frame)
        components = pd.DataFrame([{
            "isolation_forest_score": isolation_signal,
            "behavior_deviation_score": behavior_signal,
            "financial_dna_distance_score": 0.0,
            "rule_based_score": float(rule_result.normalized_scores[0]),
            "statistical_outlier_score": 0.0,
        }])
        score = float(self.fusion.fuse(components).fraud_scores[0])
        components["fraud_score"] = score
        components["risk_level"] = self.risk_levels.classify(np.array([score])).iloc[0]
        explanation = self.explainability.explain(frame, components, rule_result.triggered_rules).iloc[0]
        analysis = self.session.execute(select(FraudAnalysis).where(FraudAnalysis.transaction_id == transaction.transaction_id)).scalars().first()
        if analysis is None:
            analysis = FraudAnalysis(customer_id=transaction.customer_id, transaction_id=transaction.transaction_id)
            self.session.add(analysis)
        analysis.fraud_score_placeholder = round(score, 2)
        analysis.anomaly_reason_placeholder = str(explanation["risk_level"])
        analysis.explanation_placeholder = str(explanation["fraud_explanation"])
        analysis.evidence_json = {"model_prediction": "anomalous" if prediction == -1 else "within learned pattern", "contributors": json.loads(explanation["contributing_features_json"]), "updated_at": datetime.now(timezone.utc).isoformat()}
        profile = self.session.get(BehaviorProfile, transaction.customer_id)
        if profile is not None:
            profile.avg_transaction_amount = baseline
            profile.transaction_frequency = float(len(history))
            profile.risk_flags_json = {"latest_risk": str(explanation["risk_level"]), "latest_score": round(score, 2)}
            profile.last_updated = datetime.now(timezone.utc)
        self.session.commit()
        self.session.refresh(analysis)
        self.refresh_customer_intelligence(transaction.customer_id)
        return analysis

    def refresh_customer_intelligence(self, customer_id: str) -> None:
        """Apply existing deterministic intelligence components to current DB state only."""
        transactions = self.session.execute(select(Transaction).where(Transaction.customer_id == customer_id)).scalars().all()
        account = transactions[0].customer if transactions else None
        if account is None:
            return
        amounts = np.array([item.transaction_amount for item in transactions], dtype=float)
        scores = [item.fraud_score_placeholder or 0.0 for item in self.session.execute(select(FraudAnalysis).where(FraudAnalysis.customer_id == customer_id)).scalars().all()]
        monthly = float(amounts.sum())
        state = pd.DataFrame([{"customer_id": customer_id, "average_account_balance": account.account_balance, "average_monthly_spending": monthly, "income_stability_score": 1.0 / (1.0 + float(amounts.std()) / max(float(amounts.mean()), 1.0)), "spending_consistency": 1.0 / (1.0 + float(amounts.std()) / max(float(amounts.mean()), 1.0)), "transaction_regularity": min(len(transactions) / 30.0, 1.0), "balance_utilisation": min(monthly / max(account.account_balance, 1.0), 1.0), "expense_ratio": min(monthly / max(account.account_balance + monthly, 1.0), 1.0), "debt_pressure_estimate": 0.0, "spending_capacity": max(account.account_balance - monthly, 0.0), "spending_volatility_index": min(float(amounts.std()) / max(float(amounts.mean()), 1.0), 1.0), "weekend_transaction_share": sum(item.transaction_date.weekday() >= 5 for item in transactions) / max(len(transactions), 1), "customer_avg_fraud_score": float(np.mean(scores)) if scores else 0.0, "agentic_average_fraud_score": float(np.mean(scores)) if scores else 0.0, "agentic_maximum_fraud_score": max(scores, default=0.0), "agentic_flagged_transactions": sum(score >= 31 for score in scores), "behaviour_profile": "Stable"}])
        for component in (SavingsBehaviorAnalyzer(), WealthMetricsCalculator(), FinancialHealthAnalyzer(), InvestmentReadinessAnalyzer()):
            state = state.merge(component.build(state), on="customer_id", how="left")
        personality = FinancialPersonalityAnalyzer().build(state).iloc[0]["financial_personality"]
        twin = self.session.get(DigitalWealthTwin, customer_id) or DigitalWealthTwin(customer_id=customer_id)
        self.session.add(twin); twin.health_score_placeholder = float(state.iloc[0]["financial_health_score"]); twin.financial_dna_json = {key: float(value) for key, value in state.iloc[0].items() if isinstance(value, (int, float, np.number))}; twin.wealth_summary = f"{personality} financial profile"
        drafts = BudgetingEngine().recommend(state.iloc[0]) + SavingsRecommender().recommend(state.iloc[0]) + InvestmentRecommender().recommend(state.iloc[0]) + DebtOptimizer().recommend(state.iloc[0])
        ranked = RecommendationRanker().rank(FinancialPriorityEngine().prioritize(drafts))
        self.session.query(Recommendation).filter(Recommendation.customer_id == customer_id).delete()
        for draft in ranked:
            item = DecisionExplanationEngine().finalize(draft); self.session.add(Recommendation(customer_id=customer_id, recommendation_text=item["explanation"], priority=item["priority"], status="active"))
        agent = AgenticAIDecisionEngine(); decision = agent._build_decision(state.iloc[0], datetime.now(timezone.utc).isoformat())
        memory = self.session.query(AgentMemory).filter(AgentMemory.customer_id == customer_id).first() or AgentMemory(customer_id=customer_id)
        self.session.add(memory); memory.summary = decision["final_decision"]; memory.conversation_memory = json.dumps(decision)
        self.session.commit()
