from __future__ import annotations

import numpy as np
import pandas as pd


class SavingsBehaviorAnalyzer:
    """Estimate savings tendency from balance and spending behaviour."""

    def build(self, state: pd.DataFrame) -> pd.DataFrame:
        working = state.copy()
        balance_utilisation = working.get("balance_utilisation", 0.5)
        expense_ratio = working.get("expense_ratio", 0.5)
        income_stability = working.get("income_stability_score", working.get("spending_consistency", 0.5))

        savings_signal = (
            (1.0 - balance_utilisation.clip(0.0, 1.0)) * 0.35
            + (1.0 - expense_ratio.clip(0.0, 1.0)) * 0.35
            + income_stability.clip(0.0, 1.0) * 0.30
        )
        working["savings_tendency"] = np.round(np.clip(savings_signal * 100.0, 0.0, 100.0), 2)
        return working[["customer_id", "savings_tendency"]]
