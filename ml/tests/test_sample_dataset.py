from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.create_sample_dataset import create_sample_dataset


def test_create_sample_dataset_writes_exact_sample(tmp_path: Path) -> None:
    source_path = tmp_path / "bank_transactions.csv"
    source_frame = pd.DataFrame(
        {
            "TransactionID": [f"T{i}" for i in range(100)],
            "CustomerID": [f"C{i % 10}" for i in range(100)],
            "CustomerDOB": ["10/1/94"] * 100,
            "CustGender": ["F"] * 100,
            "CustLocation": ["Mumbai"] * 100,
            "CustAccountBalance": list(range(100, 200)),
            "TransactionDate": ["2/8/16"] * 100,
            "TransactionTime": ["143207"] * 100,
            "TransactionAmount (INR)": list(range(1, 101)),
        }
    )
    source_frame.to_csv(source_path, index=False)

    output_path = tmp_path / "bank_transactions_training.csv"
    sampled_path = create_sample_dataset(source_path, output_path, sample_size=50, random_state=42)

    sampled_frame = pd.read_csv(sampled_path)
    assert len(sampled_frame) == 50
    assert list(sampled_frame.columns) == list(source_frame.columns)
    assert set(sampled_frame["TransactionID"]).issubset(set(source_frame["TransactionID"]))