"""Combine PaySim fraud and AML laundering scores for backend risk decisions."""
from app.config import HIGH_RISK_THRESHOLD, MEDIUM_RISK_THRESHOLD

ML_WEIGHT = 0.6
AML_WEIGHT = 0.4


def combine_scores(ml_score: float | None, aml_score: float | None) -> float:
    """
    Use the higher score if either component is LOW; otherwise use the weighted
    average of the PaySim and AML scores.
    """
    if ml_score is None and aml_score is None:
        return 0.0
    if ml_score is None:
        return round(max(0.0, min(1.0, float(aml_score))), 8)
    if aml_score is None:
        return round(max(0.0, min(1.0, float(ml_score))), 8)

    ml_score = max(0.0, min(1.0, float(ml_score)))
    aml_score = max(0.0, min(1.0, float(aml_score)))

    if ml_score < MEDIUM_RISK_THRESHOLD or aml_score < MEDIUM_RISK_THRESHOLD:
        score = max(ml_score, aml_score)
    else:
        score = ML_WEIGHT * ml_score + AML_WEIGHT * aml_score

    return round(score, 8)


def risk_level(score: float) -> str:
    if score >= HIGH_RISK_THRESHOLD:
        return "HIGH"
    if score >= MEDIUM_RISK_THRESHOLD:
        return "MEDIUM"
    return "LOW"
