from __future__ import annotations

import re
from dataclasses import dataclass

import numpy as np
import pandas as pd

RAW_TO_CANONICAL_COLUMNS = {
    "TransactionID": "transaction_id",
    "CustomerID": "customer_id",
    "CustomerDOB": "customer_dob",
    "CustGender": "gender",
    "CustLocation": "location",
    "CustAccountBalance": "account_balance",
    "TransactionDate": "transaction_date",
    "TransactionTime": "transaction_time",
    "TransactionAmount": "transaction_amount",
}

RAW_COLUMN_ALIASES = {
    "TransactionAmount (INR)": "TransactionAmount",
}

REQUIRED_COLUMNS = set(RAW_TO_CANONICAL_COLUMNS.values())


@dataclass(frozen=True)
class CleaningStats:
    rows_in: int
    rows_out: int
    duplicate_rows_removed: int
    invalid_rows_removed: int


class TransactionDataCleaner:
    """Clean bank transactions for downstream feature engineering."""

    def clean(self, frame: pd.DataFrame) -> pd.DataFrame:
        """Return a cleaned, canonical dataframe ready for feature engineering."""

        cleaned = frame.copy()
        cleaned = cleaned.rename(columns=self._normalize_source_columns)
        cleaned = cleaned.rename(columns=RAW_COLUMN_ALIASES)
        cleaned = cleaned.rename(columns=RAW_TO_CANONICAL_COLUMNS)
        self._validate_required_columns(cleaned)

        cleaned = cleaned.drop_duplicates().reset_index(drop=True)

        for column in ("transaction_id", "customer_id", "gender", "location", "transaction_time"):
            cleaned[column] = self._normalize_text_series(cleaned[column])

        cleaned["transaction_id"] = cleaned["transaction_id"].str.strip()
        cleaned["customer_id"] = cleaned["customer_id"].str.strip()
        cleaned = cleaned[(cleaned["transaction_id"].notna()) & (cleaned["transaction_id"] != "")]
        cleaned = cleaned[(cleaned["customer_id"].notna()) & (cleaned["customer_id"] != "")]

        cleaned["customer_dob"] = pd.to_datetime(
            cleaned["customer_dob"],
            errors="coerce",
            dayfirst=True,
        )
        cleaned["transaction_date"] = pd.to_datetime(
            cleaned["transaction_date"],
            errors="coerce",
            dayfirst=True,
        )

        cleaned["account_balance"] = pd.to_numeric(cleaned["account_balance"], errors="coerce")
        cleaned["transaction_amount"] = pd.to_numeric(cleaned["transaction_amount"], errors="coerce")

        time_components = cleaned["transaction_time"].apply(self._parse_transaction_time)
        cleaned[["transaction_hour", "transaction_minute", "transaction_second"]] = pd.DataFrame(
            time_components.tolist(),
            index=cleaned.index,
        )

        cleaned["transaction_hour"] = pd.to_numeric(cleaned["transaction_hour"], errors="coerce")
        cleaned["transaction_minute"] = pd.to_numeric(cleaned["transaction_minute"], errors="coerce")
        cleaned["transaction_second"] = pd.to_numeric(cleaned["transaction_second"], errors="coerce")

        cleaned = cleaned[
            cleaned["transaction_date"].notna()
            & cleaned["transaction_hour"].notna()
            & cleaned["transaction_minute"].notna()
            & cleaned["transaction_second"].notna()
        ]

        cleaned = cleaned[cleaned["account_balance"].notna() & (cleaned["account_balance"] >= 0)]
        cleaned = cleaned[cleaned["transaction_amount"].notna() & (cleaned["transaction_amount"] > 0)]

        cleaned["gender"] = cleaned["gender"].apply(self._standardize_gender)
        cleaned["location"] = cleaned["location"].apply(self._normalize_location)

        invalid_dob_mask = cleaned["customer_dob"].isna() | (cleaned["customer_dob"] > cleaned["transaction_date"])
        invalid_dob_mask |= (
            (cleaned["transaction_date"] - cleaned["customer_dob"]).dt.days.div(365.25) > 120
        )
        valid_dobs = cleaned.loc[~invalid_dob_mask, "customer_dob"].dropna()
        if not valid_dobs.empty:
            cleaned.loc[invalid_dob_mask, "customer_dob"] = valid_dobs.median()

        cleaned = cleaned.drop_duplicates(subset=["transaction_id"], keep="first")
        cleaned = cleaned.reset_index(drop=True)
        return cleaned[
            [
                "transaction_id",
                "customer_id",
                "customer_dob",
                "gender",
                "location",
                "account_balance",
                "transaction_date",
                "transaction_hour",
                "transaction_minute",
                "transaction_second",
                "transaction_amount",
            ]
        ]

    @staticmethod
    def _normalize_source_columns(column_name: str) -> str:
        return column_name.strip()

    @staticmethod
    def _validate_required_columns(frame: pd.DataFrame) -> None:
        missing_columns = REQUIRED_COLUMNS - set(frame.columns)
        if missing_columns:
            raise ValueError(
                "Missing required columns after loading: "
                f"{', '.join(sorted(missing_columns))}."
            )

    @staticmethod
    def _normalize_text_series(series: pd.Series) -> pd.Series:
        return series.astype("string").str.replace(r"\s+", " ", regex=True).str.strip()

    @staticmethod
    def _parse_transaction_time(raw_value: object) -> tuple[int | None, int | None, int | None]:
        if raw_value is None or (isinstance(raw_value, float) and np.isnan(raw_value)):
            return None, None, None

        value = str(raw_value).strip()
        if not value:
            return None, None, None

        if value.endswith(".0"):
            value = value[:-2]

        digits = re.sub(r"\D", "", value)
        if not digits:
            return None, None, None

        digits = digits.zfill(6)[-6:]
        try:
            hour = int(digits[:2])
            minute = int(digits[2:4])
            second = int(digits[4:6])
        except ValueError:
            return None, None, None

        if hour > 23 or minute > 59 or second > 59:
            return None, None, None
        return hour, minute, second

    @staticmethod
    def _standardize_gender(raw_value: object) -> str:
        value = str(raw_value).strip().upper()
        mapping = {
            "F": "F",
            "FEMALE": "F",
            "M": "M",
            "MALE": "M",
            "O": "O",
            "OTHER": "O",
            "UNKNOWN": "Unknown",
            "": "Unknown",
            "<NA>": "Unknown",
            "NAN": "Unknown",
        }
        return mapping.get(value, "Unknown")

    @staticmethod
    def _normalize_location(raw_value: object) -> str:
        value = str(raw_value).strip()
        if not value or value.lower() in {"<na>", "nan", "none"}:
            return "Unknown"
        normalized = re.sub(r"\s+", " ", value)
        return normalized.title()
