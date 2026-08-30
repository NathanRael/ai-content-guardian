"""Local (LIME) and global (SHAP) explainability helpers."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import shap
from lime.lime_text import LimeTextExplainer

from services.ml_pipeline import CLASS_LABELS, get_models

OUTPUTS_DIR = Path(__file__).resolve().parents[1] / "outputs"
SHAP_CACHE = OUTPUTS_DIR / "shap_global.json"

_explainer: LimeTextExplainer | None = None


def _get_lime_explainer() -> LimeTextExplainer:
    global _explainer
    if _explainer is None:
        _explainer = LimeTextExplainer(class_names=CLASS_LABELS)
    return _explainer


def explain_with_lime(text: str, pred_idx: int, top_n: int = 10) -> list[dict]:
    """Return the top signed LIME features for the predicted class."""
    from services.ml_pipeline import predict_proba_for_lime

    exp = _get_lime_explainer().explain_instance(text, predict_proba_for_lime, num_features=top_n, top_labels=1)
    label = exp.available_labels()[0]
    features = exp.as_list(label=label)
    return [{"word": word, "weight": round(float(weight), 4)} for word, weight in features]


def compute_global_shap(sample_texts: list[str]) -> list[dict]:
    """Compute mean |SHAP| per feature per class on a sample and cache it."""
    vectorizer, _, rf = get_models()
    X = vectorizer.transform(sample_texts).toarray()
    feature_names = vectorizer.get_feature_names_out()

    explainer = shap.TreeExplainer(rf)
    raw = explainer.shap_values(X)
    shap_array = np.stack(raw, axis=0)  # (n_samples, n_features, n_classes)

    records = []
    for cls_idx, cls_name in enumerate(CLASS_LABELS):
        vals = np.abs(shap_array[..., cls_idx]).mean(axis=0)
        for feat, val in zip(feature_names, vals):
            records.append({
                "class": cls_name,
                "feature": feat,
                "mean_abs_shap": round(float(val), 6),
            })

    records = sorted(records, key=lambda r: (r["class"], -r["mean_abs_shap"]))
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(SHAP_CACHE, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)
    return records


def load_global_shap_importance(top_n: int = 20) -> dict:
    """Return the cached global SHAP top features per class."""
    if not SHAP_CACHE.exists():
        return {}
    with open(SHAP_CACHE, encoding="utf-8") as f:
        records = json.load(f)
    grouped: dict[str, list[dict]] = {cls: [] for cls in CLASS_LABELS}
    for r in records:
        grouped.setdefault(r["class"], []).append(r)
    return {
        cls: [{"feature": r["feature"], "mean_abs_shap": r["mean_abs_shap"]} for r in items[:top_n]]
        for cls, items in grouped.items()
    }
