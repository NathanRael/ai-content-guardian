"""SHAP and LIME explanations for the random forest model."""
import json

import joblib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap
from lime.lime_text import LimeTextExplainer

from hate_speech_detector.config import CLASS_LABELS, MODELS_DIR, OUTPUTS_DIR


def rf_predict_proba(texts):
    """Prediction function for LIME wrapping the RF pipeline."""
    vectorizer = joblib.load(MODELS_DIR / "tfidf_vectorizer.joblib")
    rf = joblib.load(MODELS_DIR / "random_forest.joblib")
    X = vectorizer.transform(texts)
    return rf.predict_proba(X.toarray())


def main():
    df = pd.read_csv(OUTPUTS_DIR / "data_clean.csv")
    test_idx = joblib.load(OUTPUTS_DIR / "idx_test.joblib")
    df_test = df.loc[test_idx].copy().reset_index(drop=True)

    vectorizer = joblib.load(MODELS_DIR / "tfidf_vectorizer.joblib")
    rf = joblib.load(MODELS_DIR / "random_forest.joblib")

    feature_names = vectorizer.get_feature_names_out()
    X_test = vectorizer.transform(df_test["tweet_clean"].astype(str))

    # Subsample for global SHAP summary (keep it fast and readable)
    sample_size = min(200, X_test.shape[0])
    sample_idx = np.random.RandomState(42).choice(X_test.shape[0], sample_size, replace=False)
    X_sample = X_test[sample_idx].toarray()

    explainer = shap.TreeExplainer(rf)
    raw_shap = explainer.shap_values(X_sample)  # list of (n_features, n_classes) per sample
    # Convert to (n_samples, n_features, n_classes)
    shap_array = np.stack(raw_shap, axis=0)

    # Global feature importance: mean |SHAP| per class
    importance_records = []
    for cls_idx, cls_name in enumerate(CLASS_LABELS):
        vals = np.abs(shap_array[..., cls_idx]).mean(axis=0)
        for feat, val in zip(feature_names, vals):
            importance_records.append({
                "class": cls_name,
                "feature": feat,
                "mean_abs_shap": round(float(val), 6),
            })
    importance_df = pd.DataFrame(importance_records)
    importance_df = importance_df.sort_values(["class", "mean_abs_shap"], ascending=[True, False])
    importance_df.to_csv(OUTPUTS_DIR / "shap_importance.csv", index=False)

    # Summary plot for class 0 (hate speech)
    plt.figure()
    shap.summary_plot(
        shap_array[..., 0],
        X_sample,
        feature_names=feature_names,
        show=False,
        max_display=15,
    )
    plt.tight_layout()
    plt.savefig(OUTPUTS_DIR / "shap_summary_hate_speech.png", dpi=150, bbox_inches="tight")
    plt.close()

    # Summary plot for class 1 (offensive language)
    plt.figure()
    shap.summary_plot(
        shap_array[..., 1],
        X_sample,
        feature_names=feature_names,
        show=False,
        max_display=15,
    )
    plt.tight_layout()
    plt.savefig(OUTPUTS_DIR / "shap_summary_offensive_language.png", dpi=150, bbox_inches="tight")
    plt.close()

    # SHAP + LIME on the documented edge cases
    edge_cases = pd.read_csv(OUTPUTS_DIR / "edge_cases.csv")
    lime_explainer = LimeTextExplainer(class_names=CLASS_LABELS)
    lime_results = []

    for _, row in edge_cases.iterrows():
        if row["model"] != "random_forest":
            continue
        text = str(row["tweet_clean"])
        exp = lime_explainer.explain_instance(text, rf_predict_proba, num_features=8, top_labels=1)
        label = exp.available_labels()[0]
        lime_features = exp.as_list(label=label)

        # SHAP values for this instance
        X_inst = vectorizer.transform([text]).toarray()
        inst_shap = explainer.shap_values(X_inst)  # list of (n_features, n_classes)
        inst_array = np.stack(inst_shap, axis=0)   # (1, n_features, n_classes)
        pred_cls = CLASS_LABELS.index(row["predicted_label"])
        sv = inst_array[0, :, pred_cls]
        top_shap = sorted(zip(feature_names, sv), key=lambda x: abs(x[1]), reverse=True)[:8]

        lime_results.append({
            "case_type": row["case_type"],
            "tweet": text,
            "true_label": row["true_label"],
            "predicted_label": row["predicted_label"],
            "aae_marker_count": int(row["aae_marker_count"]),
            "lime_features": lime_features,
            "top_shap_features": [(f, round(float(v), 4)) for f, v in top_shap],
        })

    with open(OUTPUTS_DIR / "lime_edge_cases.json", "w", encoding="utf-8") as f:
        json.dump(lime_results, f, indent=2, ensure_ascii=False)

    print(f"Saved SHAP summary plots, shap_importance.csv and {len(lime_results)} LIME edge-case explanations to {OUTPUTS_DIR}")


if __name__ == "__main__":
    main()
