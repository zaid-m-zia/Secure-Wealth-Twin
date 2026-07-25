from __future__ import annotations

from pathlib import Path
from typing import Iterator

import pandas as pd

EXPECTED_COLUMNS = {
    "TransactionID",
    "CustomerID",
    "CustomerDOB",
    "CustGender",
    "CustLocation",
    "CustAccountBalance",
    "TransactionDate",
    "TransactionTime",
    "TransactionAmount",
}

COLUMN_ALIASES = {
    "TransactionAmount (INR)": "TransactionAmount",
}


class CSVTransactionLoader:
    """Load the bank transactions CSV with schema validation and chunk support."""

    def __init__(self, file_path: str | Path, chunksize: int = 50_000) -> None:
        self.file_path = Path(file_path)
        self.chunksize = chunksize

    def validate_schema(self) -> list[str]:
        """Validate the CSV header and return normalized column names."""

        if not self.file_path.exists():
            raise FileNotFoundError(f"CSV file not found: {self.file_path}")

        header_frame = pd.read_csv(self.file_path, nrows=0)
        normalized_columns = [self._normalize_column_name(column) for column in header_frame.columns]
        normalized_columns = [column for column in normalized_columns if column]

        missing_columns = EXPECTED_COLUMNS - set(normalized_columns)
        if missing_columns:
            raise ValueError(
                "CSV schema is invalid. Missing columns: "
                f"{', '.join(sorted(missing_columns))}."
            )

        unexpected_columns = sorted(
            column for column in normalized_columns if column not in EXPECTED_COLUMNS
        )
        if unexpected_columns:
            raise ValueError(
                "CSV schema is invalid. Unexpected columns: "
                f"{', '.join(unexpected_columns)}."
            )

        return normalized_columns

    def iter_chunks(self) -> Iterator[pd.DataFrame]:
        """Yield CSV chunks as dataframes after normalizing headers."""

        self.validate_schema()

        for chunk in pd.read_csv(self.file_path, chunksize=self.chunksize):
            chunk = chunk.rename(columns=self._normalize_column_name)
            chunk = chunk.loc[:, [column for column in chunk.columns if column and not column.startswith("Unnamed")]]
            yield chunk

    def load(self) -> pd.DataFrame:
        """Load the full dataset by concatenating validated chunks."""

        frames = list(self.iter_chunks())
        if not frames:
            raise ValueError("CSV file is empty.")
        return pd.concat(frames, ignore_index=True)

    @staticmethod
    def _normalize_column_name(column_name: str) -> str:
        normalized = column_name.strip()
        return COLUMN_ALIASES.get(normalized, normalized)
