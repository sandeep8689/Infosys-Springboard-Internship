"""Treatment recommendations by disease category, risk level, and reported symptoms."""

from __future__ import annotations

RISK_FOLLOW_UP = {
    "Low": "Schedule a routine primary-care visit within 2–4 weeks if symptoms persist.",
    "Medium": "Book a clinician appointment within 7 days; log symptom changes daily.",
    "High": "Seek urgent medical evaluation within 24–48 hours.",
    "Critical": "Go to emergency care now or call your local emergency number.",
}

# Category rules: first matching category wins (order matters — specific before general).
CATEGORY_RULES: list[dict] = [
    {
        "name": "cardiac",
        "match": (
            "heart attack",
            "heart failure",
            "angina",
            "hypertensive heart",
            "palpitation",
            "sinus bradycardia",
        ),
        "preventive": [
            "Monitor blood pressure and heart rate if you have a home cuff or wearable.",
            "Avoid heavy exertion until a clinician clears you.",
            "Do not ignore chest pressure, arm pain, or sudden sweating.",
        ],
        "lifestyle": [
            "Follow a heart-healthy diet: less salt, less fried food, more vegetables.",
            "Avoid tobacco and limit alcohol.",
            "Light walking only if you feel stable; stop if chest symptoms return.",
        ],
        "follow_up": [
            "Cardiology or emergency evaluation is often needed for chest-related diagnoses.",
            "Bring a list of symptoms and when they started to your visit.",
        ],
    },
    {
        "name": "respiratory",
        "match": (
            "asthma",
            "copd",
            "bronch",
            "pneumonia",
            "sinusitis",
            "common cold",
            "croup",
            "apnea",
            "hay fever",
            "allerg",
        ),
        "preventive": [
            "Avoid smoke, dust, and strong fumes that trigger breathing symptoms.",
            "Stay up to date on flu and pneumonia vaccines as your doctor recommends.",
            "Use a humidifier or steam if dry air worsens cough (unless contraindicated).",
        ],
        "lifestyle": [
            "Drink fluids to keep mucus thin; rest while acutely ill.",
            "Practice slow deep breathing if you feel short of breath at rest.",
            "Wear a mask in crowded places while recovering from respiratory illness.",
        ],
        "follow_up": [
            "See a clinician if breathing worsens, lips turn blue, or fever lasts >3 days.",
            "Pulmonology follow-up may help for chronic lung conditions.",
        ],
    },
    {
        "name": "infection",
        "match": (
            "sepsis",
            "uti",
            "urinary tract",
            "pneumonia",
            "strep",
            "otitis",
            "conjunctivitis",
            "gastroenteritis",
            "pyogenic",
            "pelvic inflammatory",
            "cystitis",
            "sinusitis",
        ),
        "preventive": [
            "Finish all antibiotics if a doctor prescribes them; do not stop early.",
            "Wash hands often; avoid sharing towels or utensils while symptomatic.",
            "Keep wounds clean and covered until healed.",
        ],
        "lifestyle": [
            "Rest and hydrate; eat bland foods if nausea or diarrhea is present.",
            "Avoid sexual activity until pelvic or UTI symptoms clear (if applicable).",
            "Use warm compresses for sinus or ear discomfort if comfortable.",
        ],
        "follow_up": [
            "Return immediately if fever spikes, confusion, or rapid heart rate occurs.",
            "Recheck with clinician if symptoms do not improve within 48–72 hours.",
        ],
    },
    {
        "name": "mental_health",
        "match": (
            "anxiety",
            "depression",
            "panic",
            "schizophrenia",
            "personality disorder",
            "marijuana abuse",
            "drug",
        ),
        "preventive": [
            "Maintain regular sleep and meal times to stabilize mood.",
            "Limit caffeine and alcohol, which can worsen anxiety or sleep.",
            "Reach out to a trusted person if you feel unsafe or overwhelmed.",
        ],
        "lifestyle": [
            "Daily 20–30 minute walks or gentle yoga can support mood.",
            "Try structured breathing: inhale 4s, hold 4s, exhale 6s, repeat 5 times.",
            "Reduce screen time before bed to improve sleep quality.",
        ],
        "follow_up": [
            "Consider counseling or psychiatry; many conditions respond well to therapy ± medication.",
            "If you have thoughts of self-harm, contact emergency services or a crisis line immediately.",
        ],
    },
    {
        "name": "musculoskeletal",
        "match": (
            "arthritis",
            "back pain",
            "herniated",
            "sprain",
            "bursitis",
            "carpal tunnel",
            "spinal",
            "spondylosis",
            "gout",
            "hip pain",
            "knee",
        ),
        "preventive": [
            "Use proper posture and ergonomic setup for desk work.",
            "Warm up before exercise; cool down and stretch afterward.",
            "Avoid lifting heavy loads with a rounded back.",
        ],
        "lifestyle": [
            "Apply ice for acute swelling; heat for stiff muscles after 48 hours if advised.",
            "Low-impact activity (swimming, cycling) often helps joint pain.",
            "Maintain healthy weight to reduce load on hips, knees, and spine.",
        ],
        "follow_up": [
            "Physical therapy can improve many spine and joint conditions.",
            "See a clinician if numbness, weakness, or bowel/bladder changes occur.",
        ],
    },
    {
        "name": "gi",
        "match": (
            "appendicitis",
            "pancreatitis",
            "cholecystitis",
            "gallstone",
            "hemorrhage",
            "esophagitis",
            "constipation",
            "diverticulitis",
            "hiatal",
            "hemorrhoid",
        ),
        "preventive": [
            "Eat regular meals; avoid very spicy or greasy foods if they trigger pain.",
            "Chew slowly; do not lie flat immediately after large meals.",
            "Stay hydrated to support digestion and prevent constipation.",
        ],
        "lifestyle": [
            "Increase fiber gradually (whole grains, fruits) if constipation is an issue.",
            "Limit NSAID use on an empty stomach unless your doctor directs otherwise.",
            "Track foods that worsen abdominal pain in a simple diary.",
        ],
        "follow_up": [
            "Severe or sudden abdominal pain needs urgent evaluation (possible surgical causes).",
            "Gastroenterology follow-up helps for reflux, gallbladder, or chronic GI issues.",
        ],
    },
    {
        "name": "skin",
        "match": (
            "eczema",
            "dermatitis",
            "psoriasis",
            "keratosis",
            "rash",
            "acne",
            "cyst",
            "polyp",
        ),
        "preventive": [
            "Use fragrance-free moisturizer after bathing.",
            "Patch-test new skin products on a small area first.",
            "Use SPF on sun-exposed areas to reduce actinic damage.",
        ],
        "lifestyle": [
            "Avoid scratching; keep nails short to reduce skin breaks.",
            "Wear loose cotton clothing over irritated areas.",
            "Identify and avoid personal triggers (detergents, metals, certain foods).",
        ],
        "follow_up": [
            "Dermatology visit if rash spreads rapidly, blisters, or does not improve in 2 weeks.",
            "Any changing mole needs professional skin exam.",
        ],
    },
    {
        "name": "pregnancy",
        "match": ("pregnancy", "gravidarum", "abortion", "menstruation", "vaginitis", "vulvodynia"),
        "preventive": [
            "Attend scheduled prenatal or well-woman visits as recommended.",
            "Take prenatal vitamins if pregnant or planning pregnancy (clinician guidance).",
            "Monitor for warning signs: heavy bleeding, severe pain, or reduced fetal movement.",
        ],
        "lifestyle": [
            "Stay hydrated; eat balanced meals with adequate protein and iron.",
            "Gentle activity (walking, prenatal yoga) unless restricted by your doctor.",
            "Avoid alcohol, smoking, and unapproved herbal supplements in pregnancy.",
        ],
        "follow_up": [
            "Contact OB/GYN for bleeding, severe cramps, or pregnancy-related concerns.",
            "Use telehealth or clinic follow-up for persistent pelvic or menstrual symptoms.",
        ],
    },
]

# Exact disease name (lowercase) overrides when category match is weak.
EXACT_DISEASE: dict[str, dict[str, list[str]]] = {
    "sepsis": {
        "preventive": [
            "Treat sepsis as a medical emergency until a clinician rules it out.",
            "Do not wait at home if you have fever plus confusion or very fast breathing.",
        ],
        "lifestyle": [
            "Rest flat with legs slightly elevated only if conscious and not breathless.",
            "Avoid food or drink if vomiting or drowsy until emergency staff advise.",
        ],
        "follow_up": [
            "Emergency department evaluation and blood cultures are standard for suspected sepsis.",
            "Hospital monitoring may include IV fluids, antibiotics, and vital sign tracking.",
        ],
    },
    "common cold": {
        "preventive": [
            "Cover coughs and sneezes; use tissues and wash hands often.",
            "Avoid close contact with infants and elderly while symptomatic.",
        ],
        "lifestyle": [
            "Warm fluids, honey-lemon drinks (not for infants under 1 year), and rest.",
            "Saline nasal rinses can ease congestion for many adults.",
        ],
        "follow_up": [
            "See a clinician if symptoms worsen after day 5 or fever exceeds 38.5°C for >3 days.",
        ],
    },
    "urinary tract infection": {
        "preventive": [
            "Drink water regularly; urinate after intercourse if prone to UTIs.",
            "Wipe front to back; avoid holding urine for long periods.",
        ],
        "lifestyle": [
            "Avoid caffeine and alcohol temporarily if they irritate the bladder.",
            "Use a heating pad on lower abdomen for comfort if not contraindicated.",
        ],
        "follow_up": [
            "Clinic visit for urinalysis and antibiotics if bacterial UTI is confirmed.",
            "Return if fever, flank pain, or blood in urine develops.",
        ],
    },
    "diabetes": {
        "preventive": [
            "Check blood glucose as directed; keep a log for your clinician.",
            "Inspect feet daily for cuts or numbness.",
        ],
        "lifestyle": [
            "Balanced meals with controlled carbohydrates and portion sizes.",
            "Daily walking or approved exercise to improve insulin sensitivity.",
        ],
        "follow_up": [
            "HbA1c and eye exam on schedule with primary care or endocrinology.",
        ],
    },
}

DEFAULT = {
    "preventive": [
        "Track symptoms daily (severity 1–10) to share with a clinician.",
        "Stay current on routine screenings appropriate for your age.",
        "Wash hands before meals and after using the restroom.",
    ],
    "lifestyle": [
        "Aim for 7–9 hours of sleep and balanced meals with vegetables and protein.",
        "150 minutes per week of moderate activity unless your doctor advises otherwise.",
        "Manage stress with short walks, journaling, or guided relaxation.",
    ],
    "follow_up": [
        "This tool is educational — confirm any diagnosis with a licensed clinician.",
        "Seek emergency care for chest pain, trouble breathing, stroke signs, or severe confusion.",
    ],
}

SYMPTOM_TIPS: dict[str, dict[str, str]] = {
    "fever": {
        "preventive": "Monitor temperature every 4–6 hours while febrile.",
        "follow_up": "See a doctor if fever is >39°C, lasts >3 days, or you feel very unwell.",
    },
    "cough": {
        "lifestyle": "Honey in warm water may soothe cough (not for infants under 1 year).",
        "follow_up": "Persistent cough >3 weeks warrants medical review.",
    },
    "shortness of breath": {
        "preventive": "Sit upright and loosen tight clothing if breathless.",
        "follow_up": "Call emergency services if breathing is rapidly worsening.",
    },
    "chest tightness": {
        "follow_up": "Treat sudden chest tightness as urgent until a clinician evaluates you.",
    },
    "vomiting": {
        "lifestyle": "Sip oral rehydration fluids in small amounts after vomiting settles.",
    },
    "headache": {
        "lifestyle": "Rest in a dark, quiet room; stay hydrated.",
        "follow_up": "Sudden worst-ever headache needs emergency evaluation.",
    },
}


def _category_for(disease: str) -> dict | None:
    d = disease.lower()
    for rule in CATEGORY_RULES:
        if any(token in d for token in rule["match"]):
            return rule
    return None


def _symptom_extras(symptoms: list[str]) -> dict[str, list[str]]:
    prev, life, follow = [], [], []
    for s in symptoms:
        key = s.strip().lower()
        tips = SYMPTOM_TIPS.get(key)
        if not tips:
            for tip_key, tip_val in SYMPTOM_TIPS.items():
                if tip_key in key or key in tip_key:
                    tips = tip_val
                    break
        if not tips:
            for word in key.split():
                if word in SYMPTOM_TIPS:
                    tips = SYMPTOM_TIPS[word]
                    break
        if not tips:
            continue
        if tips.get("preventive"):
            prev.append(tips["preventive"])
        if tips.get("lifestyle"):
            life.append(tips["lifestyle"])
        if tips.get("follow_up"):
            follow.append(tips["follow_up"])
    return {"preventive": prev, "lifestyle": life, "follow_up": follow}


def _pad(items: list[str], fallback: list[str], minimum: int = 4) -> list[str]:
    out = list(items)
    for line in fallback:
        if len(out) >= minimum:
            break
        if line not in out:
            out.append(line)
    return out


def build_recommendations(
    disease: str,
    risk_level: str,
    symptoms: list[str] | None = None,
) -> dict:
    symptoms = symptoms or []
    cat = _category_for(disease)
    extras = _symptom_extras(symptoms)
    exact = EXACT_DISEASE.get(disease.lower().strip())

    if exact:
        preventive = list(exact.get("preventive", [])) + extras["preventive"]
        lifestyle = list(exact.get("lifestyle", [])) + extras["lifestyle"]
        follow_up = list(exact.get("follow_up", [])) + extras["follow_up"]
    elif cat:
        preventive = list(cat["preventive"]) + extras["preventive"]
        lifestyle = list(cat["lifestyle"]) + extras["lifestyle"]
        follow_up = list(cat["follow_up"]) + extras["follow_up"]
    else:
        preventive = list(DEFAULT["preventive"]) + extras["preventive"]
        lifestyle = list(DEFAULT["lifestyle"]) + extras["lifestyle"]
        follow_up = list(DEFAULT["follow_up"]) + extras["follow_up"]

    preventive = _pad(preventive, DEFAULT["preventive"])
    lifestyle = _pad(lifestyle, DEFAULT["lifestyle"])
    follow_up = _pad(follow_up, DEFAULT["follow_up"])

    follow_up.insert(0, RISK_FOLLOW_UP.get(risk_level, RISK_FOLLOW_UP["Medium"]))
    follow_up.insert(
        1,
        f"Predicted condition context: {disease} — use clinical exam and tests to confirm.",
    )

    # De-duplicate while preserving order
    def dedupe(items: list[str]) -> list[str]:
        seen: set[str] = set()
        out: list[str] = []
        for item in items:
            if item not in seen:
                seen.add(item)
                out.append(item)
        return out[:8]

    return {
        "preventive_care": dedupe(preventive),
        "lifestyle_advice": dedupe(lifestyle),
        "follow_up_guidance": dedupe(follow_up),
        "llm_summary": None,
    }
