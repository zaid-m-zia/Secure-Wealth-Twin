from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class RuleEvaluationResult:
    scores: np.ndarray
    normalized_scores: np.ndarray
    triggered_rules: pd.Series


class RuleBasedFraudEngine:
    """Evaluate deterministic banking-style fraud indicators."""

    rule_weights = {
        "very_large_transaction_flag": 25.0,
        "large_transaction_flag": 15.0,
        "rapid_transaction_flag": 20.0,
        "low_balance_flag": 15.0,
        "high_spending_flag": 15.0,
        "new_customer_flag": 10.0,
        "dormant_customer_flag": 10.0,
        "night_activity": 10.0,
        "weekend_high_amount": 10.0,
        "extreme_balance_ratio": 20.0,
    }

    def evaluate(self, frame: pd.DataFrame) -> RuleEvaluationResult:
        working = frame.copy()
        scores = np.zeros(len(working), dtype=float)
        triggered_rules: list[list[str]] = [[] for _ in range(len(working))]

        flag_columns = [
            "very_large_transaction_flag",
            "large_transaction_flag",
            "rapid_transaction_flag",
            "low_balance_flag",
            "high_spending_flag",
            "new_customer_flag",
            "dormant_customer_flag",
        ]
        for flag_column in flag_columns:
            if flag_column not in working.columns:
                continue
            active = working[flag_column].fillna(0).astype(int) == 1
            scores[active.to_numpy()] += self.rule_weights[flag_column]
            for index in working.index[active]:
                triggered_rules[index].append(flag_column)

        night_activity = (working["transaction_hour"] >= 22) | (working["transaction_hour"] <= 4)
        scores[night_activity.to_numpy()] += self.rule_weights["night_activity"]
        for index in working.index[night_activity]:
            triggered_rules[index].append("night_activity")

        weekend_high_amount = (
            working.get("weekend_flag", pd.Series(0, index=working.index)).fillna(0).astype(int) == 1
        ) & (
            working["transaction_amount"]
            >= working["average_transaction_amount"].fillna(0.0) * 2.0
        )
        scores[weekend_high_amount.to_numpy()] += self.rule_weights["weekend_high_amount"]
        for index in working.index[weekend_high_amount]:
            triggered_rules[index].append("weekend_high_amount")

        extreme_balance_ratio = working.get("transaction_balance_ratio", pd.Series(0.0, index=working.index)).fillna(0.0) >= 0.75
        scores[extreme_balance_ratio.to_numpy()] += self.rule_weights["extreme_balance_ratio"]
        for index in working.index[extreme_balance_ratio]:
            triggered_rules[index].append("extreme_balance_ratio")

        normalized_scores = np.clip(scores, 0.0, 100.0)
        return RuleEvaluationResult(
            scores=scores,
            normalized_scores=normalized_scores,
            triggered_rules=pd.Series(triggered_rules),
        )
