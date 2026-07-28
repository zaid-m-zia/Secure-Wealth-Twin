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
from ml.fraud_intelligence.explainability import FraudExplainabilityEngine
from ml.fraud_intelligence.risk_score import BehaviorDeviationCalculator, FraudScoreFusion, RiskLevelClassifier
from ml.fraud_intelligence.rule_engine import RuleBasedFraudEngine

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
        return analysis
