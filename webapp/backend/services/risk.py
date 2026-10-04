CRITICAL_DISEASES = {
    "heart attack",
    "sepsis",
    "appendicitis",
    "acute pancreatitis",
    "acute kidney injury",
    "heart failure",
    "pneumonia",
    "gastrointestinal hemorrhage",
    "concussion",
    "sickle cell crisis",
}

HIGH_DISEASES = {
    "angina",
    "asthma",
    "chronic obstructive pulmonary disease (copd)",
    "hypertensive heart disease",
    "liver disease",
    "multiple sclerosis",
    "obstructive sleep apnea (osa)",
    "pelvic inflammatory disease",
    "urinary tract infection",
    "cholecystitis",
}


def compute_risk_level(
    disease: str,
    confidence: float,
    symptom_count: int,
    age: int | None,
) -> str:
    d = disease.lower().strip()
    score = 0.0

    if d in CRITICAL_DISEASES:
        score += 3.0
    elif d in HIGH_DISEASES:
        score += 2.0
    else:
        score += 1.0

    if confidence >= 0.85:
        score += 1.5
    elif confidence >= 0.65:
        score += 1.0
    else:
        score += 0.5

    if symptom_count >= 8:
        score += 1.5
    elif symptom_count >= 5:
        score += 1.0
    elif symptom_count >= 3:
        score += 0.5

    if age is not None:
        if age >= 65:
            score += 1.0
        elif age >= 45:
            score += 0.5

    if score >= 5.5:
        return "Critical"
    if score >= 4.0:
        return "High"
    if score >= 2.5:
        return "Medium"
    return "Low"
