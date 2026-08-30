"""Model card endpoint."""
import json
from pathlib import Path

import pandas as pd
from fastapi import APIRouter

from services.explainability import load_global_shap_importance

OUTPUTS_DIR = Path(__file__).resolve().parents[1] / "outputs"
MODELS_DIR = Path(__file__).resolve().parents[1] / "models"

router = APIRouter(tags=["model-info"])


@router.get("/model-info")
async def get_model_info():
    with open(MODELS_DIR / "metadata.json", encoding="utf-8") as f:
        metadata = json.load(f)

    distribution = pd.read_csv(OUTPUTS_DIR / "class_distribution.csv")
    class_distribution = {
        row["class_label"]: int(row["count"]) for _, row in distribution.iterrows()
    }

    return {
        "intended_use": (
            "Outil d'aide à la modération de contenu à des fins éducatives et de recherche. "
            "Il signale les messages potentiellement problématiques pour qu'un modérateur humain les examine."
        ),
        "not_intended_for": [
            "Modération entièrement automatique sans supervision humaine.",
            "Détection de dialecte ou d'origine démographique.",
            "Jugement légal ou décision de sanction définitive.",
        ],
        "known_limitations": [
            "Dataset américain annoté dans un contexte culturel spécifique ; généralisation limitée.",
            "Déséquilibre des classes : la classe hate_speech est minoritaire et son rappel est faible.",
            "Le proxy AAE est une approximation lexicale grossière, pas un classifieur de dialecte validé.",
            "Risque de faux positifs sur des marqueurs dialectaux, du sarcasme ou des citations.",
        ],
        "human_role": (
            "Toute action restrictive (suppression, bannissement) doit être validée par un modérateur humain "
            "et offrir un recours à l'utilisateur."
        ),
        "training_data_summary": {
            "source": "Hate Speech and Offensive Language Dataset (Davidson et al.)",
            "size": metadata["train_size"] + metadata["test_size"],
            "class_distribution": class_distribution,
        },
        "global_shap_features": load_global_shap_importance(top_n=10),
    }
