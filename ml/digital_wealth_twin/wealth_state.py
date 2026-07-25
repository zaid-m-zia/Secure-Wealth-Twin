from __future__ import annotations

import pandas as pd


class WealthStateBuilder:
    """Merge upstream intelligence sources into a unified customer wealth state."""

    fingerprint_drop_columns = {"financial_fingerprint_vector", "financial_fingerprint_signature"}

    def build(
        self,
        customer_features: pd.DataFrame,
        behavioral_features: pd.DataFrame,
        financial_fingerprints: pd.DataFrame,
        fraud_customer_summary: pd.DataFrame,
    ) -> pd.DataFrame:
        state = customer_features.copy()

        behavioral = behavioral_features.drop(columns=list(self.fingerprint_drop_columns), errors="ignore")
        behavioral_merge_columns = [
            column for column in behavioral.columns if column != "customer_id" and column not in state.columns
        ]
        if behavioral_merge_columns:
            state = state.merge(behavioral[["customer_id", *behavioral_merge_columns]], on="customer_id", how="left")

        fingerprint_merge_columns = [
            column
            for column in financial_fingerprints.columns
            if column != "customer_id" and column not in state.columns
        ]
        if fingerprint_merge_columns:
            state = state.merge(
                financial_fingerprints[["customer_id", *fingerprint_merge_columns]],
                on="customer_id",
                how="left",
            )

        state = state.merge(fraud_customer_summary, on="customer_id", how="left")
        return state.fillna(0.0)

    @staticmethod
    def aggregate_fraud_scores(fraud_scores: pd.DataFrame) -> pd.DataFrame:
        grouped = fraud_scores.groupby("customer_id", sort=False)
        summary = grouped.agg(
            customer_avg_fraud_score=("fraud_score", "mean"),
            customer_max_fraud_score=("fraud_score", "max"),
            customer_flagged_transactions=("is_flagged", "sum"),
            customer_transaction_count=("transaction_id", "count"),
        ).reset_index()
        summary["customer_flagged_share"] = (
            summary["customer_flagged_transactions"] / summary["customer_transaction_count"].replace(0, 1)
        ).round(4)
        return summary
