import json
from collections import Counter

from backend.database import list_consultations
from backend.services.ml import artifacts_ready

RISK_LEVELS = ("Low", "Medium", "High", "Critical")


async def dataset_stats() -> dict | None:
    from backend.config import settings

    path = settings.artifacts_dir / "dataset_stats.json"
    if not path.is_file():
        return None
    with open(path, encoding="utf-8") as f:
        return json.load(f)


async def build_analytics_summary() -> dict:
    rows = await list_consultations(500)
    disease_counts: Counter[str] = Counter()
    risk_counter: Counter[str] = Counter()
    symptom_counter: Counter[str] = Counter()

    for row in rows:
        disease_counts[row["predicted_disease"]] += 1
        risk_counter[row["risk_level"]] += 1
        for s in json.loads(row["symptoms_json"]):
            symptom_counter[s] += 1

    risk_distribution = {level: int(risk_counter.get(level, 0)) for level in RISK_LEVELS}

    symptom_trends = [
        {"symptom": k, "count": v} for k, v in symptom_counter.most_common(15)
    ]

    ds = await dataset_stats() or {}
    dataset_disease = ds.get("disease_counts") or {}
    dataset_symptoms = ds.get("top_symptoms") or {}

    return {
        "total_consultations": len(rows),
        "disease_counts": dict(disease_counts.most_common(15)),
        "risk_distribution": risk_distribution,
        "symptom_trends": symptom_trends,
        "model_ready": artifacts_ready(),
        "dataset_disease_stats": dataset_disease,
        "dataset_top_symptoms": dataset_symptoms,
    }
