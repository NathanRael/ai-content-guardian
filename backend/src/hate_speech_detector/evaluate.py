"""Evaluation protocol: metrics, confusion matrix and documented edge cases."""
import json

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
)

from hate_speech_detector.config import CLASS_LABELS, MODELS_DIR, OUTPUTS_DIR


def evaluate_model(model, X, y, model_name: str, vectorizer=None):
    """Return metrics dict and predictions."""
    if hasattr(model, "predict_proba"):
        probs = model.predict_proba(X)
    else:
        probs = None
    y_pred = model.predict(X)

    report = classification_report(
        y, y_pred, target_names=CLASS_LABELS, output_dict=True, zero_division=0
    )
    accuracy = accuracy_score(y, y_pred)
    cm = confusion_matrix(y, y_pred, labels=list(range(len(CLASS_LABELS))))

    result = {
        "model": model_name,
        "accuracy": round(accuracy, 4),
        "per_class": {
            label: {
                "precision": round(report[label]["precision"], 4),
                "recall": round(report[label]["recall"], 4),
                "f1_score": round(report[label]["f1-score"], 4),
                "support": int(report[label]["support"]),
            }
            for label in CLASS_LABELS
        },
        "macro_avg": {
            "precision": round(report["macro avg"]["precision"], 4),
            "recall": round(report["macro avg"]["recall"], 4),
            "f1_score": round(report["macro avg"]["f1-score"], 4),
        },
        "confusion_matrix": cm.tolist(),
        "predictions": y_pred,
        "probabilities": probs,
    }
    return result


def find_edge_cases(df_test, y_test, preds, probs, model_name):
    """Return a DataFrame of three documented edge cases."""
    cases = []

    # Case 1: AAE markers present, true label neither but predicted offensive/hate
    mask_aae = (df_test["aae_marker_count"] >= 2) & (df_test["class"] == 2)
    mask_misclass = (preds != y_test) & ((preds == 1) | (preds == 0))
    candidates = df_test[mask_aae & mask_misclass]
    if not candidates.empty:
        idx = candidates.index[0]
        cases.append(build_case(df_test, idx, y_test, preds, probs, model_name, "AAE marker false positive"))

    # Case 2: True hate speech correctly predicted as hate speech
    mask_correct_hate = (y_test == 0) & (preds == 0)
    candidates = df_test[mask_correct_hate]
    if not candidates.empty:
        idx = candidates.index[0]
        cases.append(build_case(df_test, idx, y_test, preds, probs, model_name, "Correct hate speech"))

    # Case 3: True offensive predicted as neither (borderline)
    mask_border = (y_test == 1) & (preds == 2)
    candidates = df_test[mask_border]
    if not candidates.empty:
        idx = candidates.index[0]
        cases.append(build_case(df_test, idx, y_test, preds, probs, model_name, "Offensive/neither borderline"))

    return pd.DataFrame(cases)


def build_case(df_test, idx, y_test, preds, probs, model_name, case_type):
    row = df_test.loc[idx]
    return {
        "model": model_name,
        "case_type": case_type,
        "index": int(idx),
        "tweet": row["tweet"],
        "tweet_clean": row["tweet_clean"],
        "true_label": CLASS_LABELS[int(y_test.loc[idx])],
        "predicted_label": CLASS_LABELS[int(preds[df_test.index.get_loc(idx)])],
        "hate_speech_prob": round(float(probs[df_test.index.get_loc(idx), 0]), 4),
        "offensive_prob": round(float(probs[df_test.index.get_loc(idx), 1]), 4),
        "neither_prob": round(float(probs[df_test.index.get_loc(idx), 2]), 4),
        "aae_marker_count": int(row["aae_marker_count"]),
        "aae_score": round(float(row["aae_score"]), 4),
    }


def main():
    df = pd.read_csv(OUTPUTS_DIR / "data_clean.csv")
    test_idx = joblib.load(OUTPUTS_DIR / "idx_test.joblib")
    df_test = df.loc[test_idx].copy()
    y_test = df_test["class"].astype(int)

    vectorizer = joblib.load(MODELS_DIR / "tfidf_vectorizer.joblib")
    lr = joblib.load(MODELS_DIR / "logistic_regression.joblib")
    rf = joblib.load(MODELS_DIR / "random_forest.joblib")

    X_test = vectorizer.transform(df_test["tweet_clean"].astype(str))

    lr_results = evaluate_model(lr, X_test, y_test, "logistic_regression")
    rf_results = evaluate_model(rf, X_test.toarray(), y_test, "random_forest")

    metrics = {
        "logistic_regression": {
            k: v for k, v in lr_results.items()
            if k not in ("predictions", "probabilities")
        },
        "random_forest": {
            k: v for k, v in rf_results.items()
            if k not in ("predictions", "probabilities")
        },
    }
    with open(OUTPUTS_DIR / "metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)

    # Confusion matrices
    for name, cm in [("logistic_regression", lr_results["confusion_matrix"]),
                     ("random_forest", rf_results["confusion_matrix"])]:
        cm_df = pd.DataFrame(
            cm,
            index=[f"true_{l}" for l in CLASS_LABELS],
            columns=[f"pred_{l}" for l in CLASS_LABELS],
        )
        cm_df.to_csv(OUTPUTS_DIR / f"confusion_matrix_{name}.csv")

    # Edge cases
    lr_cases = find_edge_cases(df_test, y_test, lr_results["predictions"], lr_results["probabilities"], "logistic_regression")
    rf_cases = find_edge_cases(df_test, y_test, rf_results["predictions"], rf_results["probabilities"], "random_forest")
    edge_cases = pd.concat([lr_cases, rf_cases], ignore_index=True)
    edge_cases.to_csv(OUTPUTS_DIR / "edge_cases.csv", index=False)

    print("Evaluation results")
    print("=" * 40)
    for model_name in ["logistic_regression", "random_forest"]:
        m = metrics[model_name]
        print(f"\n{model_name}: accuracy={m['accuracy']}, macro-F1={m['macro_avg']['f1_score']}")
        for label, scores in m["per_class"].items():
            print(f"  {label}: P={scores['precision']} R={scores['recall']} F1={scores['f1_score']}")
    print(f"\nSaved metrics, confusion matrices and {len(edge_cases)} edge cases to {OUTPUTS_DIR}")


if __name__ == "__main__":
    main()
