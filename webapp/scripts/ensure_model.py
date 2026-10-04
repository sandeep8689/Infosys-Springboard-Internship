"""Train a compact model on cloud boot if artifacts are missing."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

WEBAPP_ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = WEBAPP_ROOT / "artifacts"
MODEL = ARTIFACTS / "model.joblib"


def main() -> None:
    if MODEL.is_file():
        print("Model artifacts found — skipping training.")
        return

    sample = WEBAPP_ROOT / "data" / "sample_dataset.csv"
    full = WEBAPP_ROOT / "data" / "Diseases_and_Symptoms_dataset.csv"
    csv = sample if sample.is_file() else full

    if not csv.is_file():
        print("No dataset found; prediction API will be unavailable until model is trained.")
        sys.exit(0)

    print(f"Training deploy model from {csv.name} …")
    subprocess.check_call(
        [
            sys.executable,
            str(WEBAPP_ROOT / "scripts" / "train_model.py"),
            "--csv",
            str(csv),
            "--trees",
            "50",
            "--max-depth",
            "20",
        ]
    )


if __name__ == "__main__":
    main()
