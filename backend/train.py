"""Standalone training and evaluation script for AI Content Guardian.

Run from the backend folder:
    uv run python train.py
"""
from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import shap
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

from services.dialect_proxy import compute_dialect_score
from services.ml_pipeline import (
    CLASS_LABELS,
    load_data,
    train_and_save,
)
from services.preprocessing import clean_text

OUTPUTS_DIR = Path("outputs")
MODELS_DIR = Path("models")
DIALECT_THRESHOLD = 0.15

EDGE_CASE_TEXTS = [
    {
        "case_type": "sarcasm",
        "example_text": "Oh great, another genius opinion. I am so lucky to read this.",
        "note": (
            "Sarcasme : le texte semble poli mais exprime du mépris. "
            "Le modèle peut le classer à tort comme neutre."
        ),
    },
    {
        "case_type": "neutral_insult_object",
        "example_text": "This printer is a stupid piece of junk.",
        "note": (
            "Insulte dirigée vers un objet, pas une personne. "
            "Le modèle peut réagir aux mots offensants sans voir l'absence de cible humaine."
        ),
    },
    {
        "case_type": "dialect_variation",
        "example_text": "Imma be real witchu, that movie ain't it.",
        "note": (
            "Variante dialectale avec marqueurs AAE. "
            "Le modèle risque de surestimer la toxicité à cause du proxy lexical."
        ),
    },
]

DEMO_PAIRS = [
    {
        "standard": "I am going to the store right now.",
        "dialect_variant": "Imma run to the store right quick.",
    },
    {
        "standard": "I do not want to do this homework.",
        "dialect_variant": "I ain't tryna do this homework tho.",
    },
    {
        "standard": "We are definitely going to win this game.",
        "dialect_variant": "We finna win this game, y'all watch.",
    },
]


def _label_map(label: str) -> str:
    return {"hate_speech": "hate_speech", "offensive_language": "offensive", "neither": "neutral"}[label]


def evaluate_model(model, X, y, model_name: str):
    y_pred = model.predict(X)
    report = classification_report(
        y, y_pred, target_names=CLASS_LABELS, output_dict=True, zero_division=0
    )
    return {
        "accuracy": round(accuracy_score(y, y_pred), 4),
        "per_class": {
            label: {
                "precision": round(report[label]["precision"], 4),
                "recall": round(report[label]["recall"], 4),
                "f1_score": round(report[label]["f1-score"], 4),
                "support": int(report[label]["support"]),
            }
            for label in CLASS_LABELS
        },
        "confusion_matrix": confusion_matrix(y, y_pred, labels=list(range(len(CLASS_LABELS)))).tolist(),
    }


def build_edge_cases(vectorizer, lr, rf):
    records = []
    for case in EDGE_CASE_TEXTS:
        cleaned = clean_text(case["example_text"])
        X = vectorizer.transform([cleaned])
        lr_prob = lr.predict_proba(X)[0]
        rf_prob = rf.predict_proba(X.toarray())[0]
        records.append({
            "case_type": case["case_type"],
            "example_text": case["example_text"],
            "prediction": {
                "logistic_regression": {
                    "label": _label_map(CLASS_LABELS[int(np.argmax(lr_prob))]),
                    "confidence": round(float(lr_prob[np.argmax(lr_prob)]), 4),
                },
                "random_forest": {
                    "label": _label_map(CLASS_LABELS[int(np.argmax(rf_prob))]),
                    "confidence": round(float(rf_prob[np.argmax(rf_prob)]), 4),
                },
            },
            "note": case["note"],
        })
    return records


def build_bias_audit(df_test, lr, rf, vectorizer):
    df_test = df_test.copy()
    df_test["dialect_score"] = df_test["tweet_clean"].apply(compute_dialect_score)
    df_test["lr_pred"] = np.argmax(lr.predict_proba(vectorizer.transform(df_test["tweet_clean"].astype(str))), axis=1)
    df_test["rf_pred"] = np.argmax(rf.predict_proba(vectorizer.transform(df_test["tweet_clean"].astype(str)).toarray()), axis=1)

    high = df_test[df_test["dialect_score"] > DIALECT_THRESHOLD]
    low = df_test[df_test["dialect_score"] <= DIALECT_THRESHOLD]

    def flag_rate(subdf):
        flagged_lr = ((subdf["lr_pred"] == 0) | (subdf["lr_pred"] == 1)).mean()
        flagged_rf = ((subdf["rf_pred"] == 0) | (subdf["rf_pred"] == 1)).mean()
        return round(float((flagged_lr + flagged_rf) / 2), 4)

    high_rate = flag_rate(high)
    low_rate = flag_rate(low)

    example_pairs = []
    for pair in DEMO_PAIRS:
        X_std = vectorizer.transform([pair["standard"]])
        X_var = vectorizer.transform([pair["dialect_variant"]])
        lr_std = lr.predict_proba(X_std)[0]
        lr_var = lr.predict_proba(X_var)[0]
        rf_std = rf.predict_proba(X_std.toarray())[0]
        rf_var = rf.predict_proba(X_var.toarray())[0]
        example_pairs.append({
            "standard": pair["standard"],
            "dialect_variant": pair["dialect_variant"],
            "prediction_standard": {
                "logistic_regression": {
                    "label": _label_map(CLASS_LABELS[int(np.argmax(lr_std))]),
                    "confidence": round(float(lr_std[np.argmax(lr_std)]), 4),
                },
                "random_forest": {
                    "label": _label_map(CLASS_LABELS[int(np.argmax(rf_std))]),
                    "confidence": round(float(rf_std[np.argmax(rf_std)]), 4),
                },
            },
            "prediction_variant": {
                "logistic_regression": {
                    "label": _label_map(CLASS_LABELS[int(np.argmax(lr_var))]),
                    "confidence": round(float(lr_var[np.argmax(lr_var)]), 4),
                },
                "random_forest": {
                    "label": _label_map(CLASS_LABELS[int(np.argmax(rf_var))]),
                    "confidence": round(float(rf_var[np.argmax(rf_var)]), 4),
                },
            },
        })

    return {
        "methodology_note": (
            "Cet audit utilise un proxy lexical de marqueurs AAE, pas un classifieur de dialecte validé. "
            "Il mesure le taux de signalement sur des textes à fort score dialectal par rapport à d'autres, "
            "afin de détecter un risque de biais. Les paires standard/variante illustrent des formulations "
            "sémantiquement proches avec des marqueurs différents."
        ),
        "flag_rate_high_dialect_markers": high_rate,
        "flag_rate_low_dialect_markers": low_rate,
        "gap": round(high_rate - low_rate, 4),
        "example_pairs": example_pairs,
    }


def compute_global_shap(vectorizer, rf, df_test):
    feature_names = vectorizer.get_feature_names_out()
    X_test = vectorizer.transform(df_test["tweet_clean"].astype(str))
    sample_size = min(200, X_test.shape[0])
    rng = np.random.RandomState(42)
    sample_idx = rng.choice(X_test.shape[0], sample_size, replace=False)
    X_sample = X_test[sample_idx].toarray()

    explainer = shap.TreeExplainer(rf)
    raw = explainer.shap_values(X_sample)
    shap_array = np.stack(raw, axis=0)

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
    with open(OUTPUTS_DIR / "shap_global.json", "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)


def main():
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    vectorizer, lr, rf, df, train_idx, test_idx = train_and_save()

    df_test = df.loc[test_idx].copy().reset_index(drop=True)
    X_test = vectorizer.transform(df_test["tweet_clean"].astype(str))

    lr_results = evaluate_model(lr, X_test, df_test["class"].astype(int), "logistic_regression")
    rf_results = evaluate_model(rf, X_test.toarray(), df_test["class"].astype(int), "random_forest")

    metrics = {
        "logistic_regression": {
            k: v for k, v in lr_results.items() if k != "predictions"
        },
        "random_forest": {
            k: v for k, v in rf_results.items() if k != "predictions"
        },
    }
    with open(OUTPUTS_DIR / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)

    # class distribution
    distribution = df["class_label"].value_counts().reset_index()
    distribution.columns = ["class_label", "count"]
    distribution.to_csv(OUTPUTS_DIR / "class_distribution.csv", index=False)

    # edge cases
    edge_cases = build_edge_cases(vectorizer, lr, rf)
    with open(OUTPUTS_DIR / "edge_cases.json", "w", encoding="utf-8") as f:
        json.dump(edge_cases, f, indent=2, ensure_ascii=False)

    # bias audit
    audit = build_bias_audit(df_test, lr, rf, vectorizer)
    with open(OUTPUTS_DIR / "bias_audit.json", "w", encoding="utf-8") as f:
        json.dump(audit, f, indent=2, ensure_ascii=False)

    # global SHAP
    compute_global_shap(vectorizer, rf, df_test)

    print("Training complete.")
    print(f"  Accuracy LR={lr_results['accuracy']} RF={rf_results['accuracy']}")
    print(f"  High-dialect flag rate: {audit['flag_rate_high_dialect_markers']}")
    print(f"  Low-dialect flag rate:  {audit['flag_rate_low_dialect_markers']}")
    print(f"  Gap: {audit['gap']}")


if __name__ == "__main__":
    main()
