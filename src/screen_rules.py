import re

# ---------- FACTOR KEYWORDS ----------

FACTOR_KEYWORDS = {
    "QualitySleep": [
        "sleep", "insomnia", "sleep quality", "sleep duration",
        "sleep apnea", "psqi", "circadian"
    ],
    "PhysicalActivity": [
        "physical activity", "exercise", "aerobic", "fitness",
        "sedentary", "walking", "resistance training"
    ],
    "HealthyEating": [
        "diet", "nutrition", "mediterranean diet",
        "dash diet", "mind diet", "diet quality"
    ],
    "BloodSugarManagement": [
        "glucose", "hba1c", "diabetes", "glycemic",
        "insulin resistance"
    ],
    "BloodPressureControl": [
        "blood pressure", "hypertension"
    ],
    "LipidRegulation": [
        "cholesterol", "ldl", "hdl", "triglyceride",
        "dyslipidemia", "statin"
    ],
    "SmokingAvoidance": [
        "smoking", "tobacco", "cigarette", "nicotine"
    ],
    "StressManagement": [
        "stress", "cortisol", "mindfulness",
        "meditation", "psychological stress"
    ],
    "SocialMentalEngagement": [
        "social engagement", "loneliness",
        "social isolation", "cognitive training"
    ],
    "AbdominalCircumference": [
        "waist circumference", "abdominal obesity",
        "central obesity", "visceral fat"
    ]
}

OUTCOME_KEYWORDS = [
    "cognition", "cognitive", "dementia", "alzheimer",
    "brain health", "neuroimaging", "mri",
    "cognitive decline", "memory"
]


def normalize(text):
    return text.lower()


def find_hits(text, keywords):
    hits = []
    for k in keywords:
        if re.search(r"\b" + re.escape(k) + r"\b", text):
            hits.append(k)
    return hits


def rule_screen(title, abstract):
    text = normalize(title + " " + abstract)

    factor_hits = {}
    for factor, kws in FACTOR_KEYWORDS.items():
        hits = find_hits(text, kws)
        if hits:
            factor_hits[factor] = hits

    outcome_hits = find_hits(text, OUTCOME_KEYWORDS)

    if factor_hits and outcome_hits:
        decision = "include"
        reason = "Brain outcome and modifiable factor detected"
    elif factor_hits or outcome_hits:
        decision = "maybe"
        reason = "Partial match"
    else:
        decision = "exclude"
        reason = "No brain outcome or factor"

    evidence = ", ".join(list(factor_hits.keys()) + outcome_hits)

    return decision, list(factor_hits.keys()), outcome_hits, reason, evidence
