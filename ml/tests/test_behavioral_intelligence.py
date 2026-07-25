from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from ml.behavioral_intelligence.engine import BehavioralIntelligenceEngine
from ml.behavioral_intelligence.feature_service import BehavioralFeatureService
from ml.behavioral_intelligence.financial_fingerprint import FinancialFingerprintBuilder
from ml.behavioral_intelligence.normalization import BehavioralFeatureNormalizer
from ml.behavioral_intelligence.spending_patterns import SpendingPatternAnalyzer
from ml.behavioral_intelligence.transaction_context import TransactionContextBuilder
from ml.behavioral_intelligence.transaction_timing import TransactionTimingAnalyzer
from ml.customer_behavior.aggregator import CustomerBehaviourAggregator
from ml.customer_behavior.feature_generator import BehaviourFeatureGenerator


def _build_clean_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "transaction_id": ["T1", "T2", "T3", "T4", "T5", "T6", "T7", "T8"],
            "customer_id": ["C1", "C1", "C1", "C1", "C2", "C2", "C2", "C2"],
            "customer_dob": pd.to_datetime(["1990-01-10"] * 4 + ["1985-05-05"] * 4),
            "gender": ["F", "F", "F", "F", "M", "M", "M", "M"],
            "location": ["Mumbai", "Mumbai", "Pune", "Mumbai", "Delhi", "Delhi", "Gurgaon", "Delhi"],
            "account_balance": [1000.0, 1100.0, 1200.0, 1300.0, 5000.0, 4800.0, 4700.0, 4600.0],
            "transaction_date": pd.to_datetime(
                [
                    "2016-08-01",
                    "2016-08-02",
                    "2016-08-04",
                    "2016-08-06",
                    "2016-08-01",
                    "2016-08-03",
                    "2016-08-05",
                    "2016-08-07",
                ]
            ),
            "transaction_hour": [9, 10, 18, 22, 14, 16, 20, 11],
            "transaction_minute": [0, 15, 45, 30, 5, 20, 10, 0],
            "transaction_second": [0, 0, 0, 0, 0, 0, 0, 0],
            "transaction_amount": [50.0, 60.0, 100.0, 250.0, 800.0, 850.0, 120.0, 300.0],
        }
    )


def _build_customer_features() -> pd.DataFrame:
    aggregated = CustomerBehaviourAggregator().build(_build_clean_frame()).dataframe
    return BehaviourFeatureGenerator().build(aggregated)


def test_spending_pattern_analyzer_adds_velocity_features() -> None:
    context = TransactionContextBuilder().build(_build_clean_frame())
    features = SpendingPatternAnalyzer().build(context)
    assert "spending_velocity" in features.columns
    assert "spending_volatility_index" in features.columns
    assert len(features) == 2


def test_transaction_timing_analyzer_adds_timing_features() -> None:
    context = TransactionContextBuilder().build(_build_clean_frame())
    features = TransactionTimingAnalyzer().build(context)
    assert "timing_share_morning" in features.columns
    assert "timing_night_activity_score" in features.columns
    assert features.loc[features["customer_id"] == "C1", "timing_share_morning"].iloc[0] > 0


def test_financial_fingerprint_builder_creates_signature(tmp_path: Path) -> None:
    engine = BehavioralIntelligenceEngine()
    result = engine.build(_build_clean_frame(), output_dir=tmp_path)
    fingerprints = FinancialFingerprintBuilder().build(result.raw_features)

    assert "financial_fingerprint_signature" in fingerprints.dataframe.columns
    assert len(fingerprints.dataframe["financial_fingerprint_signature"].iloc[0]) == 64


def test_behavioral_feature_normalizer_scales_numeric_columns(tmp_path: Path) -> None:
    engine = BehavioralIntelligenceEngine()
    result = engine.build(_build_clean_frame(), output_dir=tmp_path)
    normalizer = BehavioralFeatureNormalizer()
    normalized = normalizer.fit_transform(result.raw_features)

    for column in normalized.numeric_columns[:3]:
        assert normalized.normalized_frame[column].abs().max() <= 10


def test_behavioral_intelligence_engine_persists_artifacts(tmp_path: Path) -> None:
    customer_features = _build_customer_features()
    result = BehavioralIntelligenceEngine().build(
        _build_clean_frame(),
        output_dir=tmp_path,
        customer_features=customer_features,
    )

    assert result.customer_count == 2
    for artifact_name in [
        "behavioral_intelligence_features.parquet",
        "behavioral_intelligence_features_raw.parquet",
        "financial_fingerprints.parquet",
        "behavioral_feature_columns.json",
        "behavioral_scaler.pkl",
    ]:
        assert (tmp_path / artifact_name).exists()

    metadata = json.loads((tmp_path / "behavioral_feature_columns.json").read_text(encoding="utf-8"))
    assert metadata["feature_columns"]
    assert metadata["numeric_columns"]
    assert metadata["fingerprint_columns"]


def test_behavioral_feature_service_loads_customer_features(tmp_path: Path) -> None:
    BehavioralIntelligenceEngine().build(_build_clean_frame(), output_dir=tmp_path)
    service = BehavioralFeatureService(tmp_path)

    customer_features = service.get_customer_features("C1")
    fingerprint = service.get_customer_fingerprint("C1")

    assert customer_features is not None
    assert fingerprint is not None
    assert customer_features["customer_id"] == "C1"
    assert fingerprint["financial_fingerprint_signature"]
