"""Train, persist and load the two ML classifiers.

Model 1: multinomial LogisticRegression (interpretable baseline).
Model 2: RandomForestClassifier (complex ensemble).
Both use the same TF-IDF vectorizer fitted on the training set only.
"""
from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "labeled_data.csv"
MODELS_DIR = PROJECT_ROOT / "models"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

RANDOM_STATE = 42
TEST_SIZE = 0.2
CLASS_LABELS = ["hate_speech", "offensive_language", "neither"]
CLASS_INDEX = {name: i for i, name in enumerate(CLASS_LABELS)}
TFIDF_MAX_FEATURES = 3000
TFIDF_NGRAM_RANGE = (1, 2)

_vectorizer: TfidfVectorizer | None = None
_lr: LogisticRegression | None = None
_rf: RandomForestClassifier | None = None


def load_data() -> pd.DataFrame:
    """Load CSV and add a string class label column."""
    df = pd.read_csv(DATA_PATH)
    required = {"tweet", "class", "count", "hate_speech", "offensive_language", "neither"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns in {DATA_PATH}: {missing}")
    df["class_label"] = df["class"].astype(int).map(lambda c: CLASS_LABELS[c])
    return df


def train_and_save():
    """Full training pipeline: split, vectorize, train, persist artefacts."""
    from services.preprocessing import clean_text

    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    df = load_data()
    df["tweet_clean"] = df["tweet"].astype(str).apply(clean_text)
    df = df[df["tweet_clean"].str.len() > 0].reset_index(drop=True)

    train_idx, test_idx = train_test_split(
        np.arange(len(df)),
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=df["class"],
    )

    X_train_raw = df.loc[train_idx, "tweet_clean"].astype(str)
    X_test_raw = df.loc[test_idx, "tweet_clean"].astype(str)
    y_train = df.loc[train_idx, "class"].astype(int)
    y_test = df.loc[test_idx, "class"].astype(int)

    vectorizer = TfidfVectorizer(
        max_features=TFIDF_MAX_FEATURES,
        ngram_range=TFIDF_NGRAM_RANGE,
        lowercase=True,
        sublinear_tf=True,
    )
    X_train = vectorizer.fit_transform(X_train_raw)
    X_test = vectorizer.transform(X_test_raw)

    lr = LogisticRegression(
        solver="lbfgs",
        max_iter=1000,
        class_weight="balanced",
        random_state=RANDOM_STATE,
    )
    lr.fit(X_train, y_train)

    X_train_dense = X_train.toarray()
    rf = RandomForestClassifier(
        n_estimators=100,
        max_depth=25,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=RANDOM_STATE,
        n_jobs=5,
    )
    rf.fit(X_train_dense, y_train)

    joblib.dump(vectorizer, MODELS_DIR / "tfidf_vectorizer.joblib")
    joblib.dump(lr, MODELS_DIR / "logistic_regression.joblib")
    joblib.dump(rf, MODELS_DIR / "random_forest.joblib")

    metadata = {
        "random_state": RANDOM_STATE,
        "test_size": TEST_SIZE,
        "tfidf_max_features": TFIDF_MAX_FEATURES,
        "tfidf_ngram_range": TFIDF_NGRAM_RANGE,
        "classes": CLASS_LABELS,
        "train_size": int(len(train_idx)),
        "test_size": int(len(test_idx)),
    }
    with open(MODELS_DIR / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    # Persist indices for reproducible evaluation
    joblib.dump(train_idx, OUTPUTS_DIR / "idx_train.joblib")
    joblib.dump(test_idx, OUTPUTS_DIR / "idx_test.joblib")

    return vectorizer, lr, rf, df, train_idx, test_idx


def load_models():
    """Load persisted artefacts into module-level cache."""
    global _vectorizer, _lr, _rf
    _vectorizer = joblib.load(MODELS_DIR / "tfidf_vectorizer.joblib")
    _lr = joblib.load(MODELS_DIR / "logistic_regression.joblib")
    _rf = joblib.load(MODELS_DIR / "random_forest.joblib")


def get_models():
    """Return loaded vectorizer and classifiers."""
    if _vectorizer is None or _lr is None or _rf is None:
        load_models()
    return _vectorizer, _lr, _rf


def predict(text: str, model_name: str) -> dict:
    """Classify cleaned text with one model.

    Returns {"label": str, "confidence": float, "probabilities": [float, ...]}.
    """
    vectorizer, lr, rf = get_models()
    model = lr if model_name == "logistic_regression" else rf
    X = vectorizer.transform([text])
    if model_name == "random_forest":
        X = X.toarray()
    probs = model.predict_proba(X)[0]
    pred_idx = int(np.argmax(probs))
    return {
        "label": CLASS_LABELS[pred_idx],
        "confidence": round(float(probs[pred_idx]), 4),
        "probabilities": [round(float(p), 4) for p in probs],
    }


def predict_proba_for_lime(texts: list[str]) -> np.ndarray:
    """Prediction function used by LIME (works on the random forest)."""
    vectorizer, _, rf = get_models()
    X = vectorizer.transform(texts).toarray()
    return rf.predict_proba(X)


def predict_proba_for_logistic(texts: list[str]) -> np.ndarray:
    """Prediction function used by LIME (works on logistic regression)."""
    vectorizer, lr, _ = get_models()
    X = vectorizer.transform(texts)
    return lr.predict_proba(X)
