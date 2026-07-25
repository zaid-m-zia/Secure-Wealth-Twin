from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class FinancialFingerprintResult:
    dataframe: pd.DataFrame
    fingerprint_columns: list[str]


class FinancialFingerprintBuilder:
    """Build compact financial fingerprints for downstream anomaly detection."""

    default_fingerprint_columns = [
        "spending_velocity",
        "spending_volatility_index",
        "income_stability_score",
        "cash_flow_volatility",
        "cash_flow_direction_score",
        "category_top_location_share",
        "category_amount_entropy",
        "timing_peak_concentration",
        "timing_night_activity_score",
        "weekday_weekend_amount_ratio",
        "monthly_spending_volatility",
        "monthly_trend_strength",
    ]

    def build(self, frame: pd.DataFrame, fingerprint_columns: list[str] | None = None) -> FinancialFingerprintResult:
        columns = fingerprint_columns or [
            column for column in self.default_fingerprint_columns if column in frame.columns
        ]
        if not columns:
            raise ValueError("No fingerprint columns available in the behavioral intelligence frame.")

        working = frame[["customer_id", *columns]].copy()
        matrix = working[columns].apply(pd.to_numeric, errors="coerce").fillna(0.0)
        row_norms = np.linalg.norm(matrix.to_numpy(dtype=float), axis=1)
        row_norms = np.where(row_norms == 0, 1.0, row_norms)
        normalized_matrix = matrix.to_numpy(dtype=float) / row_norms[:, None]

        working["financial_fingerprint_vector"] = [
            json.dumps([float(round(value, 6)) for value in vector], sort_keys=True)
            for vector in normalized_matrix
        ]
        working["financial_fingerprint_signature"] = [
            hashlib.sha256(vector_json.encode("utf-8")).hexdigest()
            for vector_json in working["financial_fingerprint_vector"]
        ]
        working["financial_fingerprint_magnitude"] = row_norms.round(6)
        return FinancialFingerprintResult(dataframe=working, fingerprint_columns=columns)
