"""Language detection and translation to English before classification."""
from dataclasses import dataclass

from deep_translator import GoogleTranslator
from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException


@dataclass
class TranslationResult:
    detected_language: str
    translated_text: str | None
    translation_warning: bool


def translate_if_needed(text: str) -> TranslationResult:
    """Detect language and translate to English when needed.

    Returns the original text if it is already English, if detection fails, or
    if translation fails. In the failure case `translation_warning` is True and
    `translated_text` is None so the caller can fall back to the raw input.
    """
    stripped = text.strip()
    if not stripped:
        return TranslationResult("unknown", None, False)

    try:
        detected = detect(stripped)
    except LangDetectException:
        return TranslationResult("unknown", None, True)

    if detected == "en":
        return TranslationResult("en", None, False)

    try:
        translated = GoogleTranslator(source="auto", target="en").translate(stripped)
        return TranslationResult(detected, translated, False)
    except Exception:
        return TranslationResult(detected, None, True)
