from __future__ import annotations

import json

import pandas as pd


class UnifiedCustomerContextBuilder:
    """Join upstream intelligence artifacts into one customer-level decision context."""

    required_frames = {
        "customer_features": {"customer_id"},
        "behavioral_features": {"customer_id"},
        "fraud_scores": {"customer_id", "fraud_score"},
        "wealth_twins": {"customer_id"},
        "financial_recommendations": {"customer_id", "recommendation", "confidence_score", "priority", "rank"},
    }

    def build(
        self,
        customer_features: pd.DataFrame,
        behavioral_features: pd.DataFrame,
        fraud_scores: pd.DataFrame,
        wealth_twins: pd.DataFrame,
        financial_recommendations: pd.DataFrame,
    ) -> pd.DataFrame:
        frames = {
            "customer_features": customer_features,
            "behavioral_features": behavioral_features,
            "fraud_scores": fraud_scores,
            "wealth_twins": wealth_twins,
            "financial_recommendations": financial_recommendations,
        }
        self._validate(frames)

        context = customer_features.copy()
        context = self._merge_new_columns(context, behavioral_features)
        context = self._merge_new_columns(context, wealth_twins)
        context = self._merge_new_columns(context, self._summarize_fraud(fraud_scores))
        context = context.merge(self._group_recommendations(financial_recommendations), on="customer_id", how="left")
        return context.fillna(0.0)

    @classmethod
    def _validate(cls, frames: dict[str, pd.DataFrame]) -> None:
        for name, required_columns in cls.required_frames.items():
            missing = required_columns.difference(frames[name].columns)
            if missing:
                raise ValueError(f"{name} is missing required columns: {sorted(missing)}")

    @staticmethod
    def _merge_new_columns(context: pd.DataFrame, incoming: pd.DataFrame) -> pd.DataFrame:
        columns = [column for column in incoming.columns if column != "customer_id" and column not in context.columns]
        if not columns:
            return context
        return context.merge(incoming[["customer_id", *columns]], on="customer_id", how="left")

    @staticmethod
    def _summarize_fraud(fraud_scores: pd.DataFrame) -> pd.DataFrame:
        summary = fraud_scores.groupby("customer_id", sort=False).agg(
            agentic_average_fraud_score=("fraud_score", "mean"),
            agentic_maximum_fraud_score=("fraud_score", "max"),
            agentic_transaction_count=("fraud_score", "count"),
        ).reset_index()
        if "is_flagged" in fraud_scores.columns:
            flagged = fraud_scores.groupby("customer_id", sort=False)["is_flagged"].sum().rename("agentic_flagged_transactions")
            summary = summary.merge(flagged, on="customer_id", how="left")
        else:
            summary["agentic_flagged_transactions"] = 0
        return summary

    @staticmethod
    def _group_recommendations(recommendations: pd.DataFrame) -> pd.DataFrame:
        ordered = recommendations.sort_values(["customer_id", "rank"], kind="stable")
        records: list[dict[str, object]] = []
        for customer_id, group in ordered.groupby("customer_id", sort=False):
            actions = []
            for _, row in group.iterrows():
                metrics = row.get("supporting_metrics", "{}")
                try:
                    supporting_metrics = json.loads(str(metrics))
                except json.JSONDecodeError:
                    supporting_metrics = {}
                actions.append(
                    {
                        "recommendation_type": str(row.get("recommendation_type", "financial_action")),
                        "recommendation": str(row["recommendation"]),
                        "priority": str(row.get("priority", "Low")),
                        "confidence_score": float(row.get("confidence_score", 0.0)),
                        "rank": int(row.get("rank", 0)),
                        "supporting_metrics": supporting_metrics,
                    }
                )
            records.append({"customer_id": customer_id, "agentic_recommendations": actions})
        return pd.DataFrame(records)

