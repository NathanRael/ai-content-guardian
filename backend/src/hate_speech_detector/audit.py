"""Dialect bias stress test using the AAE lexical proxy.

This is an ETHICAL STRESS TEST, not a validated subgroup demographic audit.
The AAE proxy is a coarse lexical approximation (see data.py).
Reference for rigorous dialect identification:
Blodgett, S. L., Green, B., & O'Connor, B. (2016).
"""
import json

import joblib
import numpy as np
import pandas as pd

from hate_speech_detector.config import CLASS_LABELS, MODELS_DIR, OUTPUTS_DIR

# Demo pairs: semantically near-equivalent Standard American English (SAE) vs AAE.
DEMO_PAIRS = [
    {
        "pair_id": 1,
        "intent": "Neutral statement about going to the store",
        "sae": "I am going to the store right now.",
        "aae": "Imma run to the store right quick.",
    },
    {
        "pair_id": 2,
        "intent": "Mild complaint about school",
        "sae": "I do not want to do this homework.",
        "aae": "I ain't tryna do this homework tho.",
    },
    {
        "pair_id": 3,
        "intent": "Expression of determination",
        "sae": "We are definitely going to win this game.",
        "aae": "We finna win this game, y'all watch.",
    },
]


def predict_df(model, vectorizer, texts):
    X = vectorizer.transform(texts)
    if hasattr(model, "predict_proba"):
        if hasattr(model, "estimators_"):  # tree ensemble stored on dense matrix
            probs = model.predict_proba(X.toarray())
        else:
            probs = model.predict_proba(X)
    else:
        probs = None
    preds = np.argmax(probs, axis=1)
    return preds, probs


def main():
    df = pd.read_csv(OUTPUTS_DIR / "data_clean.csv")
    test_idx = joblib.load(OUTPUTS_DIR / "idx_test.joblib")
    df_test = df.loc[test_idx].copy()

    vectorizer = joblib.load(MODELS_DIR / "tfidf_vectorizer.joblib")
    lr = joblib.load(MODELS_DIR / "logistic_regression.joblib")
    rf = joblib.load(MODELS_DIR / "random_forest.joblib")

    X_test = vectorizer.transform(df_test["tweet_clean"].astype(str))
    lr_probs = lr.predict_proba(X_test)
    rf_probs = rf.predict_proba(X_test.toarray())
    df_test["lr_pred"] = np.argmax(lr_probs, axis=1)
    df_test["rf_pred"] = np.argmax(rf_probs, axis=1)

    def audit_rates(subdf):
        n = len(subdf)
        return {
            "n": int(n),
            "pred_hate_rate": round((subdf["lr_pred"] == 0).mean(), 4),
            "pred_offensive_rate": round((subdf["lr_pred"] == 1).mean(), 4),
            "pred_hate_rate_rf": round((subdf["rf_pred"] == 0).mean(), 4),
            "pred_offensive_rate_rf": round((subdf["rf_pred"] == 1).mean(), 4),
        }

    high = df_test[df_test["aae_proxy_high"] == 1]
    low = df_test[df_test["aae_proxy_high"] == 0]

    # Focus on truly neutral tweets to measure false alarms at comparable content.
    neutral_high = high[high["class"] == 2]
    neutral_low = low[low["class"] == 2]

    audit = {
        "note": "Ethical stress test only; AAE proxy is not a validated dialect label.",
        "citation": "Blodgett et al. (2016) for rigorous dialect identification.",
        "aae_high": audit_rates(high),
        "aae_low": audit_rates(low),
        "neutral_only_aae_high": audit_rates(neutral_high),
        "neutral_only_aae_low": audit_rates(neutral_low),
    }

    with open(OUTPUTS_DIR / "audit.json", "w", encoding="utf-8") as f:
        json.dump(audit, f, indent=2, ensure_ascii=False)

    # Demo pair predictions
    records = []
    for pair in DEMO_PAIRS:
        for variant, text in [("SAE", pair["sae"]), ("AAE", pair["aae"])]:
            X = vectorizer.transform([text])
            lr_prob = lr.predict_proba(X)[0]
            rf_prob = rf.predict_proba(X.toarray())[0]
            records.append({
                "pair_id": pair["pair_id"],
                "intent": pair["intent"],
                "variant": variant,
                "text": text,
                "lr_pred": CLASS_LABELS[int(np.argmax(lr_prob))],
                "lr_hate": round(float(lr_prob[0]), 4),
                "lr_offensive": round(float(lr_prob[1]), 4),
                "lr_neither": round(float(lr_prob[2]), 4),
                "rf_pred": CLASS_LABELS[int(np.argmax(rf_prob))],
                "rf_hate": round(float(rf_prob[0]), 4),
                "rf_offensive": round(float(rf_prob[1]), 4),
                "rf_neither": round(float(rf_prob[2]), 4),
            })
    demo_df = pd.DataFrame(records)
    demo_df.to_csv(OUTPUTS_DIR / "demo_pairs.csv", index=False)

    print("Dialect stress test results")
    print("=" * 40)
    print(f"AAE high  (n={audit['aae_high']['n']}): "
          f"LR hate={audit['aae_high']['pred_hate_rate']} "
          f"offensive={audit['aae_high']['pred_offensive_rate']}")
    print(f"AAE low   (n={audit['aae_low']['n']}): "
          f"LR hate={audit['aae_low']['pred_hate_rate']} "
          f"offensive={audit['aae_low']['pred_offensive_rate']}")
    print(f"Neutral + AAE high (n={audit['neutral_only_aae_high']['n']}): "
          f"LR hate={audit['neutral_only_aae_high']['pred_hate_rate']} "
          f"offensive={audit['neutral_only_aae_high']['pred_offensive_rate']}")
    print(f"Neutral + AAE low  (n={audit['neutral_only_aae_low']['n']}): "
          f"LR hate={audit['neutral_only_aae_low']['pred_hate_rate']} "
          f"offensive={audit['neutral_only_aae_low']['pred_offensive_rate']}")
    print(f"\nSaved audit.json and demo_pairs.csv to {OUTPUTS_DIR}")


if __name__ == "__main__":
    main()
