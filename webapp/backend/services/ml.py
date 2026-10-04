import json

import joblib
import numpy as np

from backend.config import settings

_model = None
_label_encoder = None
_feature_names: list[str] | None = None


def artifacts_ready() -> bool:
    d = settings.artifacts_dir
    return (
        (d / "model.joblib").is_file()
        and (d / "label_encoder.joblib").is_file()
        and (d / "feature_names.json").is_file()
    )


def load_artifacts() -> None:
    global _model, _label_encoder, _feature_names
    if not artifacts_ready():
        return
    _model = joblib.load(settings.artifacts_dir / "model.joblib")
    _label_encoder = joblib.load(settings.artifacts_dir / "label_encoder.joblib")
    with open(settings.artifacts_dir / "feature_names.json", encoding="utf-8") as f:
        _feature_names = json.load(f)


def get_symptom_list() -> list[str]:
    if _feature_names is None:
        load_artifacts()
    return list(_feature_names or [])


def predict_from_symptoms(symptoms: list[str], top_k: int = 5) -> tuple[str, float, list[tuple[str, float]]]:
    if _model is None or _label_encoder is None or _feature_names is None:
        load_artifacts()
    if _model is None or _label_encoder is None or _feature_names is None:
        raise RuntimeError(
            "ML model not loaded. Place Diseases_and_Symptoms_dataset.csv in webapp/data/ "
            "and run: python scripts/train_model.py"
        )

    normalized = {s.strip().lower() for s in symptoms}
    row = np.array(
        [[1 if col.lower() in normalized else 0 for col in _feature_names]],
        dtype=np.float32,
    )

    proba = _model.predict_proba(row)[0]
    top_idx = np.argsort(proba)[::-1][:top_k]
    top_predictions = [
        (_label_encoder.classes_[i], float(proba[i])) for i in top_idx
    ]
    best_i = int(top_idx[0])
    return _label_encoder.classes_[best_i], float(proba[best_i]), top_predictions
