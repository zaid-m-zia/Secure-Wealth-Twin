from __future__ import annotations

import json
import sys
from io import StringIO
from pathlib import Path

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ml.feature_engineering.engineer import FeatureEngineer
from ml.pipeline.preprocess_pipeline import CategoricalEncoder, PreprocessingPipeline, RobustFeatureScaler
from ml.preprocessing.cleaner import TransactionDataCleaner
from ml.preprocessing.loader import CSVTransactionLoader


def test_csv_loader_supports_chunks_and_schema_validation(tmp_path: Path) -> None:
    csv_path = tmp_path / "transactions.csv"
    csv_path.write_text(
        "TransactionID,CustomerID,CustomerDOB,CustGender,CustLocation,CustAccountBalance,TransactionDate,TransactionTime,TransactionAmount (INR)\n"
        "T1,C1,10/1/94,F,MUMBAI,1000,2/8/16,143207,25\n"
        "T2,C2,11/2/93,M,PUNE,2000,2/8/16,153207,50\n",
        encoding="utf-8",
    )

    loader = CSVTransactionLoader(csv_path, chunksize=1)
    assert loader.validate_schema() == [
        "TransactionID",
        "CustomerID",
        "CustomerDOB",
        "CustGender",
        "CustLocation",
        "CustAccountBalance",
        "TransactionDate",
        "TransactionTime",
        "TransactionAmount",
    ]

    chunks = list(loader.iter_chunks())
    assert len(chunks) == 2
    assert list(chunks[0].columns)[-1] == "TransactionAmount"


def test_cleaner_normalizes_invalid_and_duplicate_rows() -> None:
    raw_frame = pd.read_csv(
        StringIO(
            "TransactionID,CustomerID,CustomerDOB,CustGender,CustLocation,CustAccountBalance,TransactionDate,TransactionTime,TransactionAmount (INR)\n"
            "T1,C1,10/1/94, female ,  new delhi ,1000,2/8/16,143207,25\n"
            "T1,C1,10/1/94,female,new delhi,1000,2/8/16,143207,25\n"
            "T2,C2,not-a-date,M,mumbai,-10,2/8/16,143207,50\n"
        )
    )

    cleaned = TransactionDataCleaner().clean(raw_frame)
    assert len(cleaned) == 1
    assert cleaned.iloc[0]["gender"] == "F"
    assert cleaned.iloc[0]["location"] == "New Delhi"
    assert cleaned.iloc[0]["account_balance"] == 1000
    assert cleaned.iloc[0]["transaction_amount"] == 25
    assert cleaned.iloc[0]["transaction_hour"] == 14
    assert pd.notna(cleaned.iloc[0]["customer_dob"])


def test_feature_engineering_builds_customer_and_risk_features() -> None:
    cleaned_frame = pd.DataFrame(
        {
            "transaction_id": ["T1", "T2", "T3"],
            "customer_id": ["C1", "C1", "C2"],
            "customer_dob": pd.to_datetime(["1994-01-10", "1994-01-10", "1988-05-02"]),
            "gender": ["F", "F", "M"],
            "location": ["Mumbai", "Mumbai", "Pune"],
            "account_balance": [1000.0, 1200.0, 5000.0],
            "transaction_date": pd.to_datetime(["2016-08-02", "2016-08-03", "2016-08-02"]),
            "transaction_hour": [14, 15, 9],
            "transaction_minute": [32, 0, 15],
            "transaction_second": [7, 0, 0],
            "transaction_amount": [25.0, 75.0, 4000.0],
        }
    )

    result = FeatureEngineer().build(cleaned_frame)
    frame = result.dataframe
    assert "age" in frame.columns
    assert "average_transaction_amount" in frame.columns
    assert "large_transaction_flag" in frame.columns
    assert frame.loc[frame["transaction_id"] == "T3", "very_large_transaction_flag"].iloc[0] == 1
    assert frame.loc[frame["transaction_id"] == "T1", "time_of_day"].iloc[0] == "Afternoon"


def test_encoding_and_scaling_round_trip() -> None:
    frame = pd.DataFrame(
        {
            "transaction_id": ["T1", "T2", "T3", "T4"],
            "customer_id": ["C1", "C1", "C2", "C2"],
            "customer_dob": pd.to_datetime(["1994-01-10", "1994-01-10", "1988-05-02", "1988-05-02"]),
            "gender": ["F", "F", "M", "M"],
            "location": ["Mumbai", "Mumbai", "Pune", "Pune"],
            "account_balance": [1000.0, 1200.0, 5000.0, 4800.0],
            "transaction_date": pd.to_datetime(["2016-08-02", "2016-08-03", "2016-08-02", "2016-08-03"]),
            "transaction_hour": [14, 15, 9, 10],
            "transaction_minute": [32, 0, 15, 0],
            "transaction_second": [7, 0, 0, 0],
            "transaction_amount": [25.0, 75.0, 4000.0, 120.0],
        }
    )

    engineered = FeatureEngineer().build(frame).dataframe
    encoder = CategoricalEncoder()
    encoded = encoder.fit_transform(engineered)
    assert encoder.feature_names_
    assert any(column.startswith("gender_") for column in encoded.columns)

    combined = pd.concat([engineered.reset_index(drop=True), encoded.reset_index(drop=True)], axis=1)

    numeric_columns = [
        column
        for column in combined.columns
        if column not in {"transaction_id", "customer_id", "customer_dob", "transaction_date", "transaction_timestamp"}
        and pd.api.types.is_numeric_dtype(combined[column])
        and not column.endswith("_flag")
    ]
    scaler = RobustFeatureScaler(numeric_columns)
    scaled = scaler.fit_transform(combined)
    assert set(numeric_columns).issubset(set(scaled.columns))


def test_pipeline_persists_artifacts(tmp_path: Path) -> None:
    source_path = tmp_path / "transactions.csv"
    source_path.write_text(
        "TransactionID,CustomerID,CustomerDOB,CustGender,CustLocation,CustAccountBalance,TransactionDate,TransactionTime,TransactionAmount (INR)\n"
        "T1,C1,10/1/94,F,MUMBAI,1000,2/8/16,143207,25\n"
        "T2,C1,10/1/94,F,MUMBAI,1200,2/8/16,153207,75\n"
        "T3,C2,2/5/88,M,PUNE,5000,2/8/16,093015,4000\n",
        encoding="utf-8",
    )

    pipeline = PreprocessingPipeline(source_path=source_path, output_dir=tmp_path / "artifacts", chunksize=2)
    result = pipeline.run()
    assert result.original_rows == 3
    assert result.processed_rows == 3
    assert result.customer_count == 2
    assert result.missing_values_remaining == 0

    artifact_dir = tmp_path / "artifacts"
    for artifact_name in [
        "processed_dataset.parquet",
        "processed_dataset.csv",
        "encoder.pkl",
        "scaler.pkl",
        "feature_columns.json",
        "customer_features.parquet",
        "behavioral_intelligence_features.parquet",
        "behavioral_intelligence_features_raw.parquet",
        "financial_fingerprints.parquet",
        "behavioral_feature_columns.json",
        "behavioral_scaler.pkl",
        "fraud_features.parquet",
        "fraud_scores.parquet",
        "fraud_model.pkl",
        "fraud_feature_columns.json",
        "digital_wealth_twins.parquet",
        "digital_wealth_twin_columns.json",
        "financial_recommendations.parquet",
        "financial_decision_intelligence_metadata.json",
        "agentic_ai_decisions.parquet",
        "agentic_ai_metadata.json",
    ]:
        assert (artifact_dir / artifact_name).exists()

    feature_columns = json.loads((artifact_dir / "feature_columns.json").read_text(encoding="utf-8"))
    assert feature_columns["feature_columns"]


def test_pipeline_writes_customer_features_artifact(tmp_path: Path) -> None:
    source_path = tmp_path / "transactions.csv"
    source_path.write_text(
        "TransactionID,CustomerID,CustomerDOB,CustGender,CustLocation,CustAccountBalance,TransactionDate,TransactionTime,TransactionAmount (INR)\n"
        "T1,C1,10/1/94,F,MUMBAI,1000,2/8/16,143207,25\n"
        "T2,C1,10/1/94,F,MUMBAI,1200,2/8/16,153207,75\n"
        "T3,C2,2/5/88,M,PUNE,5000,2/8/16,093015,4000\n",
        encoding="utf-8",
    )

    pipeline = PreprocessingPipeline(source_path=source_path, output_dir=tmp_path / "artifacts", chunksize=2)
    pipeline.run()

    customer_features = pd.read_parquet(tmp_path / "artifacts" / "customer_features.parquet")
    assert len(customer_features) == 2
    assert {"behaviour_profile", "behaviour_profile_reason"}.issubset(set(customer_features.columns))
