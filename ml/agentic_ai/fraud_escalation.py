from __future__ import annotations

from typing import Any

import pandas as pd


class FraudEscalationPolicy:
    """Convert fraud intelligence into customer-safety escalation actions."""

    def evaluate(self, customer: pd.Series) -> dict[str, Any]:
        maximum = float(customer.get("agentic_maximum_fraud_score", 0.0))
        average = float(customer.get("agentic_average_fraud_score", 0.0))
        flagged = int(customer.get("agentic_flagged_transactions", 0))
        if maximum >= 81.0:
            return {
                "escalated": True,
                "priority": "Critical",
                "final_decision": "Escalate fraud investigation and protect the account",
                "reason": f"A critical fraud score of {maximum:.1f}/100 requires immediate customer verification.",
                "actions": ["Verify recent transactions immediately", "Temporarily protect high-risk account activity"],
                "confidence": 0.96,
            }
        if maximum >= 61.0 or average >= 45.0:
            return {
                "escalated": True,
                "priority": "High",
                "final_decision": "Review fraud risk before progressing financial actions",
                "reason": f"Fraud risk is elevated (maximum {maximum:.1f}/100; average {average:.1f}/100).",
                "actions": ["Review flagged transactions", "Confirm account activity with the customer"],
                "confidence": 0.88,
            }
        return {
            "escalated": False,
            "priority": "Low",
            "final_decision": "Proceed with the highest-priority financial actions",
            "reason": f"Fraud risk is within the monitored range (maximum {maximum:.1f}/100 across {flagged} flagged transactions).",
            "actions": [],
            "confidence": 0.72,
        }
