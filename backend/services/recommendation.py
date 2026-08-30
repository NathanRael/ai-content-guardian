"""Human-review recommendation logic shared by all analyse endpoints."""

# Decision thresholds documented for the report.
CONFIDENCE_THRESHOLD = 0.65
DIALECT_SCORE_THRESHOLD = 0.15


def build_recommendation(
    lr_label: str,
    rf_label: str,
    max_confidence: float,
    dialect_score: float,
) -> tuple[str, str]:
    """Return (recommendation, French reason)."""
    if lr_label != rf_label:
        return (
            "human_review_required",
            "Les deux modèles ne sont pas d'accord sur la classification.",
        )
    if max_confidence < CONFIDENCE_THRESHOLD:
        return (
            "human_review_required",
            "Confiance du modèle trop faible.",
        )
    if dialect_score > DIALECT_SCORE_THRESHOLD and lr_label != "neutral":
        return (
            "human_review_required",
            "Des marqueurs linguistiques dialectaux ont été détectés, vérification manuelle recommandée pour éviter un biais.",
        )
    return (
        "auto_flag_possible",
        "Prédiction cohérente entre les deux modèles avec une confiance suffisante.",
    )
