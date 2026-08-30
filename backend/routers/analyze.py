"""Comment analysis endpoints: single and batch."""
from __future__ import annotations

import asyncio

from typing import Literal

from fastapi import APIRouter, HTTPException
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException
from pydantic import BaseModel, Field, field_validator

from services.dialect_proxy import compute_dialect_score
from services.explainability import explain_with_lime
from services.ml_pipeline import CLASS_INDEX, CLASS_LABELS, predict
from services.preprocessing import clean_text
from services.recommendation import build_recommendation
from services.translation import translate_if_needed

router = APIRouter(tags=["analysis"])

_LABEL_TO_API = {"hate_speech": "hate_speech", "offensive_language": "offensive", "neither": "neutral"}


class AnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=1)


class ModelPrediction(BaseModel):
    label: str
    confidence: float


class Explanation(BaseModel):
    method: str
    top_words: list[dict]


class AnalyzeResponse(BaseModel):
    original_text: str
    detected_language: str
    translated_text: str | None
    logistic_regression: ModelPrediction
    random_forest: ModelPrediction
    models_agree: bool
    dialect_marker_score: float
    recommendation: str
    recommendation_reason: str
    explanation: Explanation


class BatchAnalyzeRequest(BaseModel):
    comments: list[dict] = Field(..., min_length=1)
    model: Literal["logistic_regression", "random_forest", "both"] = "both"
    translate: bool = True

    @field_validator("comments")
    @classmethod
    def _check_comments(cls, v):
        for item in v:
            if "id" not in item or "text" not in item:
                raise ValueError("Chaque commentaire doit avoir 'id' et 'text'.")
            if not item["text"] or not str(item["text"]).strip():
                raise ValueError("Le texte d'un commentaire ne peut pas être vide.")
        return v


class Summary(BaseModel):
    total: int
    safe: int
    offensive: int
    hate_speech: int
    risk_level: str


class BatchAnalyzeResponse(BaseModel):
    results: list[dict]
    summary: Summary


def _detect_language(text: str) -> str:
    try:
        return detect(text.strip())
    except LangDetectException:
        return "unknown"


def _analyze_one_sync(
    original_text: str,
    model: str = "both",
    translate: bool = True,
) -> dict:
    if translate:
        translation = translate_if_needed(original_text)
        classification_text = translation.translated_text or original_text
        detected_language = translation.detected_language
        translated_text = translation.translated_text
    else:
        classification_text = original_text
        detected_language = _detect_language(original_text)
        translated_text = None

    cleaned = clean_text(classification_text)
    if not cleaned:
        raise HTTPException(status_code=400, detail="Texte vide après nettoyage.")

    if model == "both":
        lr = predict(cleaned, "logistic_regression")
        rf = predict(cleaned, "random_forest")
    elif model == "logistic_regression":
        lr = predict(cleaned, "logistic_regression")
        rf = lr
    else:  # random_forest
        rf = predict(cleaned, "random_forest")
        lr = rf

    lr_api_label = _LABEL_TO_API[lr["label"]]
    rf_api_label = _LABEL_TO_API[rf["label"]]

    dialect_score = round(compute_dialect_score(cleaned), 4)
    max_confidence = round(max(lr["confidence"], rf["confidence"]), 4)
    models_agree = lr_api_label == rf_api_label

    recommendation, reason = build_recommendation(
        lr_api_label, rf_api_label, max_confidence, dialect_score
    )

    primary_label = lr["label"] if model != "random_forest" else rf["label"]
    pred_idx = CLASS_INDEX[primary_label]
    lime_model = "logistic_regression" if model != "random_forest" else "random_forest"
    top_words = explain_with_lime(cleaned, pred_idx, model_name=lime_model, top_n=10)

    return {
        "original_text": original_text,
        "detected_language": detected_language,
        "translated_text": translated_text,
        "logistic_regression": {"label": lr_api_label, "confidence": lr["confidence"]},
        "random_forest": {"label": rf_api_label, "confidence": rf["confidence"]},
        "models_agree": models_agree,
        "dialect_marker_score": dialect_score,
        "recommendation": recommendation,
        "recommendation_reason": reason,
        "explanation": {"method": "lime", "top_words": top_words},
    }


async def analyze_one(
    original_text: str,
    model: str = "both",
    translate: bool = True,
) -> dict:
    return await asyncio.to_thread(_analyze_one_sync, original_text, model, translate)


@router.post("/analyze-comment", response_model=AnalyzeResponse)
async def analyze_comment(payload: AnalyzeRequest):
    if not payload.text.strip():
        raise HTTPException(status_code=400, detail="Le texte ne peut pas être vide.")
    return await analyze_one(payload.text, model="both", translate=True)


@router.post("/analyze-comments", response_model=BatchAnalyzeResponse)
async def analyze_comments(payload: BatchAnalyzeRequest):
    results = await asyncio.gather(
        *[
            analyze_one(str(item["text"]), model=payload.model, translate=payload.translate)
            for item in payload.comments
        ]
    )
    for item, result in zip(payload.comments, results):
        result["id"] = item["id"]

    primary_key = (
        "logistic_regression"
        if payload.model != "random_forest"
        else "random_forest"
    )
    safe = sum(1 for r in results if r[primary_key]["label"] == "neutral")
    offensive = sum(1 for r in results if r[primary_key]["label"] == "offensive")
    hate = sum(1 for r in results if r[primary_key]["label"] == "hate_speech")
    total = len(results)

    if hate > 0:
        risk_level = "high"
    elif offensive > total * 0.25:
        risk_level = "medium"
    else:
        risk_level = "low"

    return {
        "results": results,
        "summary": {
            "total": total,
            "safe": safe,
            "offensive": offensive,
            "hate_speech": hate,
            "risk_level": risk_level,
        },
    }
