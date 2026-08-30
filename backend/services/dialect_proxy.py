"""Coarse lexical proxy for African-American English (AAE) markers.

This module is a pedagogical stress-test tool, NOT a validated dialect
classifier. The score is a simple ratio of matched lexical/grammatical markers
to the number of words in the text. A high score only means that the text
contains tokens that also appear in documented AAE inventories; it does not
identify the speaker's dialect or race.

For rigorous dialect identification see:
Blodgett, S. L., Green, B., & O'Connor, B. (2016). Demographic dialectal
variation in social media: A case study of African-American English.
arXiv:1608.08868.
"""
import re

# Documented AAE lexical and morpho-syntactic markers used as a proxy.
AAE_MARKERS = [
    r"\bfinna\b",
    r"\btryna\b",
    r"\bain'?t\b",
    r"\bimma\b",
    r"\b(i'?m|you'?re|he'?s|she'?s|they'?re|we'?re)\s+gon(na)?\b",
    r"\by'?all\b",
    r"\bya\b",
    r"\bnah\b",
    r"\bbruh\b",
    r"\bcuz\b",
    r"\btho\b",
    r"\bsomethin'?\b",
    r"\bwatchu\b",
    r"\bwit\b",
    r"\boutta\b",
    r"\bfasho\b",
    r"\bsholl\b",
    r"\blil\b",
    r"\bdunno\b",
    r"\b\w+in'\b",  # talkin', walkin'
    r"\bbe\s+\w+ing\b",  # habitual be
    r"\bdone\s+\w+\b",  # completive done
    # multiple negation
    r"\b(don'?t|doesn'?t|ain'?t|can'?t|won'?t)\b.*\b(no|nobody|nothing|nowhere|never|none|neither)\b",
]


_MARKER_PATTERN = re.compile("|".join(f"(?:{p})" for p in AAE_MARKERS), re.IGNORECASE)


def compute_dialect_score(text: str) -> float:
    """Return a 0-1 ratio of AAE marker hits over word count."""
    if not isinstance(text, str) or not text.strip():
        return 0.0
    lowered = text.lower()
    hits = len(_MARKER_PATTERN.findall(lowered))
    words = max(len(lowered.split()), 1)
    return min(hits / words, 1.0)
