from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ml.pipeline.preprocess_pipeline import PreprocessingPipeline


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the SecureWealth AI preprocessing pipeline.")
    parser.add_argument(
        "--source",
        type=Path,
        default=None,
        help="Optional path to a custom bank transactions CSV.",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Process the full raw dataset at data/bank_transactions.csv instead of the sampled training dataset.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=REPO_ROOT / "ml" / "artifacts",
        help="Directory used to store the preprocessing artifacts.",
    )
    parser.add_argument(
        "--chunksize",
        type=int,
        default=50_000,
        help="Chunk size used by the CSV loader.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.source is not None:
        source_path = args.source
    elif args.full:
        source_path = REPO_ROOT / "data" / "bank_transactions.csv"
    else:
        source_path = REPO_ROOT / "data" / "bank_transactions_training.csv"

    pipeline = PreprocessingPipeline(
        source_path=source_path,
        output_dir=args.output_dir,
        chunksize=args.chunksize,
    )
    result = pipeline.run()
    customer_features_path = result.output_directory / "customer_features.parquet"
    customer_features = pd.read_parquet(customer_features_path)

    print(f"Original rows: {result.original_rows}")
    print(f"Processed rows: {result.processed_rows}")
    print(f"Number of customers: {result.customer_count}")
    print(f"Number of engineered features: {result.engineered_feature_count}")
    print(f"Memory usage (bytes): {result.memory_usage_bytes}")
    print(f"Missing values remaining: {result.missing_values_remaining}")
    print(f"Customers processed: {len(customer_features)}")
    print(f"Customer features created: {len(customer_features)}")
    print(f"Behaviour profiles created: {len(customer_features)}")
    behavioral_features_path = result.output_directory / "behavioral_intelligence_features.parquet"
    financial_fingerprints_path = result.output_directory / "financial_fingerprints.parquet"
    fraud_scores_path = result.output_directory / "fraud_scores.parquet"
    wealth_twins_path = result.output_directory / "digital_wealth_twins.parquet"
    recommendations_path = result.output_directory / "financial_recommendations.parquet"
    agentic_decisions_path = result.output_directory / "agentic_ai_decisions.parquet"
    print(f"Behavioral intelligence features saved to: {behavioral_features_path}")
    print(f"Financial fingerprints saved to: {financial_fingerprints_path}")
    print(f"Fraud scores saved to: {fraud_scores_path}")
    print(f"Digital Wealth Twins saved to: {wealth_twins_path}")
    print(f"Financial recommendations saved to: {recommendations_path}")
    print(f"Agentic AI decisions saved to: {agentic_decisions_path}")
    print(f"Artifacts saved to: {result.output_directory}")
    print(
        "Generated artifacts: "
        f"{customer_features_path}, {behavioral_features_path}, {financial_fingerprints_path}, "
        f"{fraud_scores_path}, {result.output_directory / 'fraud_features.parquet'}, "
        f"{result.output_directory / 'fraud_model.pkl'}, {result.output_directory / 'fraud_feature_columns.json'}, "
        f"{wealth_twins_path}, {result.output_directory / 'digital_wealth_twin_columns.json'}, "
        f"{recommendations_path}, {result.output_directory / 'financial_decision_intelligence_metadata.json'}, "
        f"{agentic_decisions_path}, {result.output_directory / 'agentic_ai_metadata.json'}, "
        f"{result.output_directory / 'processed_dataset.parquet'}, "
        f"{result.output_directory / 'processed_dataset.csv'}, "
        f"{result.output_directory / 'encoder.pkl'}, "
        f"{result.output_directory / 'scaler.pkl'}, "
        f"{result.output_directory / 'feature_columns.json'}, "
        f"{result.output_directory / 'behavioral_feature_columns.json'}, "
        f"{result.output_directory / 'behavioral_scaler.pkl'}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
