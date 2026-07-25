from __future__ import annotations

import numpy as np
import pandas as pd


class InvestmentReadinessAnalyzer:
    """Estimate investment readiness and risk tolerance."""

    def build(self, state: pd.DataFrame) -> pd.DataFrame:
        working = state.copy()
        wealth_score = working.get("wealth_score", 50.0)
        financial_stability = working.get("financial_stability", 50.0)
        debt_pressure = working.get("debt_pressure_estimate", 50.0)
        spending_volatility = working.get("spending_volatility_index", working.get("spending_volatility", 0.5))
        weekend_share = working.get("weekend_transaction_share", 0.0)
        fraud_exposure = working.get("customer_avg_fraud_score", 0.0)

        investment_readiness = np.clip(
            wealth_score * 0.35 + financial_stability * 0.35 + (100.0 - debt_pressure) * 0.30,
            0.0,
            100.0,
        )
        risk_tolerance = np.clip(
            spending_volatility.clip(0.0, 1.0) * 30.0
            + weekend_share.clip(0.0, 1.0) * 20.0
            + (100.0 - fraud_exposure) * 0.20
            + financial_stability * 0.30,
            0.0,
            100.0,
        )

        working["investment_readiness"] = np.round(investment_readiness, 2)
        working["risk_tolerance_estimate"] = np.round(risk_tolerance, 2)
        return working[["customer_id", "investment_readiness", "risk_tolerance_estimate"]]
