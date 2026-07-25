from __future__ import annotations

import json
from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class FraudExplanation:
    transaction_id: str
    fraud_score: float
    risk_level: str
    is_flagged: bool
    reasons: list[str]
    contributing_features: dict[str, float]


class FraudExplainabilityEngine:
    """Generate human-readable explanations for fraud scoring outputs."""

    score_threshold = 31.0
    component_labels = {
        "isolation_forest_score": "Isolation Forest anomaly signal",
        "behavior_deviation_score": "Behavior deviation from customer baseline",
        "financial_dna_distance_score": "Financial DNA distance",
        "rule_based_score": "Rule-based banking risk indicators",
        "statistical_outlier_score": "Statistical outlier signal",
    }

    rule_labels = {
        "very_large_transaction_flag": "Transaction amount is in the top 2% of all transactions",
        "large_transaction_flag": "Transaction amount exceeds the large transaction threshold",
        "rapid_transaction_flag": "Transaction occurred within 60 minutes of the previous transaction",
        "low_balance_flag": "Account balance is low relative to the transaction amount",
        "high_spending_flag": "Spending intensity exceeds the customer's normal pattern",
        "new_customer_flag": "Customer has very limited transaction history",
        "dormant_customer_flag": "Customer resumed activity after a long dormancy period",
        "night_activity": "Transaction occurred during late-night hours",
        "weekend_high_amount": "Weekend transaction amount is unusually high for this customer",
        "extreme_balance_ratio": "Transaction consumes a large share of the account balance",
    }

    def explain(
        self,
        frame: pd.DataFrame,
        component_scores: pd.DataFrame,
        triggered_rules: pd.Series,
    ) -> pd.DataFrame:
        explanations: list[dict[str, object]] = []

        for index, row in frame.iterrows():
            transaction_id = str(row["transaction_id"])
            component_row = component_scores.loc[index]
            fraud_score = float(component_row.get("fraud_score", 0.0))
            risk_level = str(component_row.get("risk_level", "Low"))
            is_flagged = fraud_score >= self.score_threshold
            reasons = self._build_reasons(component_row, triggered_rules.loc[index], is_flagged)
            contributing_features = self._top_contributors(component_row)

            explanations.append(
                {
                    "transaction_id": transaction_id,
                    "fraud_score": round(fraud_score, 2),
                    "risk_level": risk_level,
                    "is_flagged": is_flagged,
                    "fraud_explanation": "; ".join(reasons) if reasons else "No significant fraud indicators detected.",
                    "fraud_reasons_json": json.dumps(reasons, sort_keys=True),
                    "contributing_features_json": json.dumps(contributing_features, sort_keys=True),
                }
            )

        return pd.DataFrame(explanations)

    def _build_reasons(self, component_row: pd.Series, triggered_rules: list[str], is_flagged: bool) -> list[str]:
        if not is_flagged:
            return []

        reasons: list[str] = []
        for column, label in self.component_labels.items():
            score = float(component_row.get(column, 0.0))
            if score >= 50.0:
                reasons.append(f"{label} elevated ({score:.1f}/100).")

        for rule in triggered_rules:
            reason = self.rule_labels.get(rule)
            if reason and reason not in reasons:
                reasons.append(reason)

        if not reasons:
            reasons.append("Combined anomaly signals exceeded the medium-risk threshold.")
        return reasons

    def _top_contributors(self, component_row: pd.Series) -> dict[str, float]:
        contributors = {
            column: round(float(component_row.get(column, 0.0)), 2)
            for column in self.component_labels
            if column in component_row.index
        }
        return dict(sorted(contributors.items(), key=lambda item: item[1], reverse=True)[:5])
