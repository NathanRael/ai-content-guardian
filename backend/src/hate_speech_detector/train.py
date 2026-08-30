"""Train and save the two hate speech detection models."""
import json

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from hate_speech_detector.config import (
    CLASS_LABELS,
    MODELS_DIR,
    OUTPUTS_DIR,
    RANDOM_STATE,
    TFIDF_MAX_FEATURES,
    TFIDF_NGRAM_RANGE,
)


def main():
    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(OUTPUTS_DIR / "data_clean.csv")
    train_idx = joblib.load(OUTPUTS_DIR / "idx_train.joblib")
    test_idx = joblib.load(OUTPUTS_DIR / "idx_test.joblib")

    X_train_raw = df.loc[train_idx, "tweet_clean"].astype(str)
    X_test_raw = df.loc[test_idx, "tweet_clean"].astype(str)
    y_train = df.loc[train_idx, "class"].astype(int)
    y_test = df.loc[test_idx, "class"].astype(int)

    # TF-IDF fitted on training data only
    vectorizer = TfidfVectorizer(
        max_features=TFIDF_MAX_FEATURES,
        ngram_range=TFIDF_NGRAM_RANGE,
        lowercase=True,
        sublinear_tf=True,
    )
    X_train = vectorizer.fit_transform(X_train_raw)
    X_test = vectorizer.transform(X_test_raw)

    print(f"TF-IDF matrix: {X_train.shape[1]} features")

    # Model 1: interpretable multinomial logistic regression
    lr = LogisticRegression(
        solver="lbfgs",
        max_iter=1000,
        class_weight="balanced",
        random_state=RANDOM_STATE,
    )
    lr.fit(X_train, y_train)
    print("Trained logistic regression.")

    # Model 2: complex tree ensemble on TF-IDF features
    # RandomForest requires a dense matrix; with 3k features this is acceptable.
    X_train_dense = X_train.toarray()
    X_test_dense = X_test.toarray()
    rf = RandomForestClassifier(
        n_estimators=100,
        max_depth=25,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=RANDOM_STATE,
        n_jobs=5,
    )
    rf.fit(X_train_dense, y_train)
    print("Trained random forest.")

    # Save artefacts
    joblib.dump(vectorizer, MODELS_DIR / "tfidf_vectorizer.joblib")
    joblib.dump(lr, MODELS_DIR / "logistic_regression.joblib")
    joblib.dump(rf, MODELS_DIR / "random_forest.joblib")

    metadata = {
        "random_state": RANDOM_STATE,
        "test_size": 0.2,
        "tfidf_max_features": TFIDF_MAX_FEATURES,
        "tfidf_ngram_range": TFIDF_NGRAM_RANGE,
        "classes": CLASS_LABELS,
        "train_size": len(train_idx),
        "test_size": len(test_idx),
        "aae_proxy_not_used_as_feature": True,
    }
    with open(MODELS_DIR / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"Saved models and vectorizer to {MODELS_DIR}")


if __name__ == "__main__":
    main()
