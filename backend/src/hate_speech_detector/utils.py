"""Utilities for translation, cleaning and prediction used by the dashboard."""
from typing import Tuple

import joblib
import numpy as np
from deep_translator import GoogleTranslator
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException

from hate_speech_detector.config import CLASS_LABELS, MODELS_DIR
from hate_speech_detector.data import clean_text, count_aae_markers


def translate_if_needed(text: str) -> Tuple[str, bool, str]:
    """Detect language and translate to English if necessary.

    Returns (translated_text, was_translated, detected_language).
    Falls back to original text on translation failure.
    """
    try:
        detected = detect(text)
    except LangDetectException:
        detected = "unknown"

    if detected != "en" and len(text.strip()) > 0:
        try:
            translated = GoogleTranslator(source="auto", target="en").translate(text)
            return translated, True, detected
        except Exception:
            return text, False, detected
    return text, False, detected


def predict_text(text: str, model_name: str = "random_forest") -> dict:
    """Clean, optionally translate, and classify a single text."""
    vectorizer = joblib.load(MODELS_DIR / "tfidf_vectorizer.joblib")
    lr = joblib.load(MODELS_DIR / "logistic_regression.joblib")
    rf = joblib.load(MODELS_DIR / "random_forest.joblib")

    translated, was_translated, detected_lang = translate_if_needed(text)
    cleaned = clean_text(translated)

    X = vectorizer.transform([cleaned])
    if model_name == "logistic_regression":
        model = lr
        probs = model.predict_proba(X)[0]
    else:
        model = rf
        probs = model.predict_proba(X.toarray())[0]

    pred_class = int(np.argmax(probs))
    aae_count = count_aae_markers(cleaned)

    return {
        "original_text": text,
        "detected_language": detected_lang,
        "was_translated": was_translated,
        "translated_text": translated,
        "cleaned_text": cleaned,
        "model_used": model_name,
        "predicted_class": CLASS_LABELS[pred_class],
        "confidence": round(float(probs[pred_class]), 4),
        "probabilities": {
            label: round(float(p), 4) for label, p in zip(CLASS_LABELS, probs)
        },
        "aae_marker_count": aae_count,
    }
