"""
Train the same RandomForest pipeline as the Colab notebook and save webapp artifacts.

1. Download Diseases_and_Symptoms_dataset.csv (Kaggle: SymptomChecker dataset)
2. Save to webapp/data/Diseases_and_Symptoms_dataset.csv
3. From webapp/: python scripts/train_model.py
"""
from __future__ import annotations

import argparse
import csv
import json
import random
import sys
from collections import Counter
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

WEBAPP_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(WEBAPP_ROOT))


def load_csv(path: Path, sample: int = 0) -> tuple[np.ndarray, np.ndarray, list[str]]:
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader)
        if header[0] != "diseases":
            raise ValueError("Expected first column to be 'diseases'")
        feature_names = header[1:]
        rows: list[list[int]] = []
        labels: list[str] = []
        for row in reader:
            labels.append(row[0])
            rows.append([int(x) for x in row[1:]])

    if sample and sample < len(rows):
        idx = random.Random(42).sample(range(len(rows)), sample)
        rows = [rows[i] for i in idx]
        labels = [labels[i] for i in idx]

    return np.array(rows, dtype=np.float32), np.array(labels), feature_names


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--csv",
        type=Path,
        default=WEBAPP_ROOT / "data" / "Diseases_and_Symptoms_dataset.csv",
    )
    parser.add_argument("--sample", type=int, default=0, help="Use N random rows for quick dev train")
    parser.add_argument("--trees", type=int, default=200, help="n_estimators (use 50 for cloud deploy)")
    parser.add_argument("--max-depth", type=int, default=None, help="Max tree depth (20 for deploy)")
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Output directory (default: webapp/artifacts)",
    )
    args = parser.parse_args()

    if not args.csv.is_file():
        print(f"CSV not found: {args.csv}")
        print("Download from Kaggle and place the file in webapp/data/")
        sys.exit(1)

    X, y, feature_names = load_csv(args.csv, sample=args.sample)

    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )

    kwargs: dict = {"n_estimators": args.trees, "random_state": 42, "n_jobs": -1}
    if args.max_depth is not None:
        kwargs["max_depth"] = args.max_depth
    model = RandomForestClassifier(**kwargs)
    print(f"Training on {X_train.shape[0]} samples, {len(feature_names)} features...")
    model.fit(X_train, y_train)
    acc = model.score(X_test, y_test)
    print(f"Hold-out accuracy: {acc:.4f}")

    out = args.out_dir or (WEBAPP_ROOT / "artifacts")
    out.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, out / "model.joblib")
    joblib.dump(label_encoder, out / "label_encoder.joblib")
    with open(out / "feature_names.json", "w", encoding="utf-8") as f:
        json.dump(feature_names, f)

    disease_counts = Counter(y).most_common(25)
    col_sums = X.sum(axis=0)
    top_idx = np.argsort(col_sums)[::-1][:20]
    top_symptoms = {feature_names[i]: int(col_sums[i]) for i in top_idx}

    with open(out / "dataset_stats.json", "w", encoding="utf-8") as f:
        json.dump(
            {"disease_counts": dict(disease_counts), "top_symptoms": top_symptoms},
            f,
            indent=2,
        )

    print(f"Saved artifacts to {out}")


if __name__ == "__main__":
    main()
