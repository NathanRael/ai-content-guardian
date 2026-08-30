"""Text cleaning for the AI Content Guardian ML pipeline.

Raw text is preserved for display and only the cleaned copy is fed to the
vectorizer/models. Keeping casing and punctuation can help TF-IDF capture
intensity and sarcasm cues; lowercasing is delegated to the vectorizer.
"""
import re


def clean_text(text: str) -> str:
    """Remove @mentions, URLs and excessive noise while keeping punctuation/case."""
    if not isinstance(text, str):
        return ""
    # strip HTML entities that survived scraping
    text = re.sub(r"&\w+;", "", text)
    # mentions
    text = re.sub(r"@\w+", "", text)
    # URLs
    text = re.sub(r"http\S+|www\.\S+", "", text)
    # keep letters, digits, spaces and selected punctuation
    text = re.sub(r"[^A-Za-z0-9\s.,!?;:'\"-]", "", text)
    # collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text
