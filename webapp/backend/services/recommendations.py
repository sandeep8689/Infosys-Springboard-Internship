DISEASE_HINTS: dict[str, dict[str, list[str]]] = {
    "diabetes": {
        "preventive": ["Monitor blood glucose regularly", "Annual eye and foot exams"],
        "lifestyle": ["Balanced diet low in refined sugar", "30 minutes daily walking"],
        "follow_up": ["Endocrinologist if HbA1c stays elevated"],
    },
    "asthma": {
        "preventive": ["Avoid smoke and strong allergens", "Keep rescue inhaler accessible"],
        "lifestyle": ["Indoor air quality checks", "Warm-up before exercise"],
        "follow_up": ["Pulmonologist if wheezing worsens or night symptoms increase"],
    },
    "hypertension": {
        "preventive": ["Home BP monitoring", "Limit sodium intake"],
        "lifestyle": ["DASH-style diet", "Regular aerobic activity"],
        "follow_up": ["Physician review if BP > 140/90 on multiple readings"],
    },
}

DEFAULT = {
    "preventive": [
        "Maintain vaccination schedule (flu, COVID, etc. as advised)",
        "Track symptoms daily in a health diary",
        "Stay hydrated and get adequate sleep",
    ],
    "lifestyle": [
        "Eat whole foods; limit ultra-processed snacks",
        "150 minutes/week moderate activity unless contraindicated",
        "Manage stress with breathing exercises or mindfulness",
    ],
    "follow_up": [
        "Consult a licensed clinician for confirmation — this tool is educational only",
        "Seek emergency care for chest pain, breathing difficulty, or sudden confusion",
    ],
}

RISK_FOLLOW_UP = {
    "Low": ["Routine primary-care visit within 2–4 weeks if symptoms persist"],
    "Medium": ["Book a clinician appointment within 7 days; monitor symptom changes"],
    "High": ["Urgent medical evaluation within 24–48 hours"],
    "Critical": ["Seek emergency care immediately or call local emergency services"],
}


def _match_hints(disease: str) -> dict[str, list[str]]:
    d = disease.lower()
    for key, hints in DISEASE_HINTS.items():
        if key in d:
            return hints
    return {}


def build_recommendations(disease: str, risk_level: str) -> dict:
    hints = _match_hints(disease)
    preventive = list(hints.get("preventive", DEFAULT["preventive"]))
    lifestyle = list(hints.get("lifestyle", DEFAULT["lifestyle"]))
    follow_up = list(hints.get("follow_up", DEFAULT["follow_up"]))
    follow_up.append(RISK_FOLLOW_UP.get(risk_level, RISK_FOLLOW_UP["Medium"])[0])

    if "heart" in disease.lower() or "angina" in disease.lower():
        preventive.insert(0, "Know warning signs of cardiac events")
        lifestyle.insert(0, "Heart-healthy diet; avoid tobacco")
    if "infection" in disease.lower() or disease.lower() in {"pneumonia", "sepsis", "uti"}:
        preventive.insert(0, "Complete prescribed antibiotics if clinician orders them")
        follow_up.insert(0, "Return sooner if fever spikes or symptoms worsen")

    return {
        "preventive_care": preventive[:6],
        "lifestyle_advice": lifestyle[:6],
        "follow_up_guidance": follow_up[:6],
        "llm_summary": None,
    }
