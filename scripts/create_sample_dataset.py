from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = REPO_ROOT / "data" / "bank_transactions.csv"
DEFAULT_OUTPUT = REPO_ROOT / "data" / "bank_transactions_training.csv"
DEFAULT_SAMPLE_SIZE = 50_000
DEFAULT_RANDOM_STATE = 42


def create_sample_dataset(
    source_path: str | Path = DEFAULT_SOURCE,
    output_path: str | Path = DEFAULT_OUTPUT,
    sample_size: int = DEFAULT_SAMPLE_SIZE,
    random_state: int = DEFAULT_RANDOM_STATE,
) -> Path:
    source = Path(source_path)
    output = Path(output_path)

    if not source.exists():
        raise FileNotFoundError(f"Source CSV not found: {source}")

    frame = pd.read_csv(source, low_memory=False)
    if len(frame) < sample_size:
        raise ValueError(
            f"Source dataset has {len(frame)} rows, which is smaller than the requested sample size of {sample_size}."
        )

    sampled_frame = frame.sample(n=sample_size, random_state=random_state).reset_index(drop=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    sampled_frame.to_csv(output, index=False)
    return output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create the SecureWealth AI development dataset sample.")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE, help="Path to the raw bank transactions CSV.")
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Path where the sampled training dataset will be written.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_path = create_sample_dataset(source_path=args.source, output_path=args.output)
    print(f"Saved sampled dataset to: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())