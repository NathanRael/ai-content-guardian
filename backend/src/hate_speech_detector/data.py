"""Data loading, cleaning, AAE dialect proxy and train/test split.

The AAE proxy is a coarse lexical approximation for pedagogical stress testing.
It is NOT a validated dialect classifier. See:
Blodgett, S. L., Green, B., & O'Connor, B. (2016). Demographic dialectal variation
in social media: A case study of African-American English. arXiv:1608.08868.
"""
import re

import joblib
import pandas as pd
from sklearn.model_selection import train_test_split

from hate_speech_detector.config import (
    CLASS_LABELS,
    DATASET_PATH,
    OUTPUTS_DIR,
    RANDOM_STATE,
    TEST_SIZE,
)

# 18 lexical / morpho-syntactic markers documented in AAE linguistics.
# These are regex patterns matched against raw lower-cased tokens.
AAE_PATTERNS = [
    # lexical
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
    r"\boff\b",
    r"\bfasho\b",
    r"\bsholl\b",
    r"\blil\b",
    r"\bdunno\b",
    # phonological / morphological
    r"\b\w+in'\b",  # e.g. talkin', somethin'
    # grammatical (habitual be, completive done, multiple negation)
    r"\bbe\s+\w+ing\b",
    r"\bdone\s+\w+\b",
    r"\b(don'?t|doesn'?t|ain'?t|can'?t|won'?t)\b.*\b(no|nobody|nothing|nowhere|never|none|neither)\b",
]


def clean_text(text: str) -> str:
    """Clean a tweet while preserving punctuation and case.

    Choices:
    - Remove @mentions and URLs (noise, not language content).
    - Keep punctuation (. , ! ? ; : ' " -) and casing because they can
      carry intensity/sarcasm cues useful to the model.
    - Strip other non-alphanumeric characters and collapse whitespace.
    """
    if not isinstance(text, str):
        return ""
    # mentions
    text = re.sub(r"@\w+", "", text)
    # URLs
    text = re.sub(r"http\S+|www\.\S+", "", text)
    # keep letters, digits, spaces and selected punctuation
    text = re.sub(r"[^A-Za-z0-9\s.,!?;:'\"-]", "", text)
    # collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def count_aae_markers(text: str) -> int:
    """Return number of AAE marker pattern matches in text."""
    lowered = text.lower()
    count = 0
    for pattern in AAE_PATTERNS:
        count += len(re.findall(pattern, lowered))
    return count


def compute_aae_proxy(df: pd.DataFrame) -> pd.DataFrame:
    """Add AAE dialect proxy columns.

    aae_marker_count: raw number of marker hits.
    aae_score: marker count normalised by tweet word count (capped at 1).
    aae_proxy_high: top quartile of aae_score in the dataset.
    """
    df = df.copy()
    df["word_count"] = df["tweet_clean"].apply(lambda x: len(str(x).split()))
    df["aae_marker_count"] = df["tweet_clean"].apply(count_aae_markers)
    df["aae_score"] = df.apply(
        lambda row: min(row["aae_marker_count"] / max(row["word_count"], 1), 1.0),
        axis=1,
    )
    score_threshold = df["aae_score"].quantile(0.75)
    # If the 75th percentile is 0, fall back to presence of at least one marker.
    if score_threshold == 0:
        df["aae_proxy_high"] = (df["aae_marker_count"] >= 1).astype(int)
        threshold = 0.0
    else:
        df["aae_proxy_high"] = (df["aae_score"] >= score_threshold).astype(int)
        threshold = score_threshold
    return df, threshold


def load_and_prepare() -> pd.DataFrame:
    """Load labeled_data.csv, clean text and build the AAE proxy."""
    df = pd.read_csv(DATASET_PATH)
    required_cols = {"tweet", "class", "count", "hate_speech", "offensive_language", "neither"}
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns in {DATASET_PATH}: {missing}")

    df["tweet_clean"] = df["tweet"].apply(clean_text)
    df = df[df["tweet_clean"].str.len() > 0].reset_index(drop=True)

    # class: 0=hate speech, 1=offensive language, 2=neither
    df["class_label"] = df["class"].map(lambda c: CLASS_LABELS[int(c)])

    df, aae_threshold = compute_aae_proxy(df)
    return df, aae_threshold


def split_data(df: pd.DataFrame):
    """Stratified 80/20 split on class."""
    idx = list(range(len(df)))
    train_idx, test_idx = train_test_split(
        idx,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=df["class"],
    )
    return train_idx, test_idx


def main():
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    df, aae_threshold = load_and_prepare()
    print(f"Loaded {len(df)} tweets from {DATASET_PATH}")

    distribution = df["class_label"].value_counts().sort_index()
    print("\nClass distribution:")
    print(distribution)
    print("\nClass imbalance note: offensive_language is typically dominant; "
          "hate_speech is the minority class. This shapes metric choice "
          "(macro-F1) and justifies class_weight='balanced'.")

    train_idx, test_idx = split_data(df)
    df["split"] = ""
    df.loc[train_idx, "split"] = "train"
    df.loc[test_idx, "split"] = "test"

    df.to_csv(OUTPUTS_DIR / "data_clean.csv", index=False)
    joblib.dump(train_idx, OUTPUTS_DIR / "idx_train.joblib")
    joblib.dump(test_idx, OUTPUTS_DIR / "idx_test.joblib")
    joblib.dump(aae_threshold, OUTPUTS_DIR / "aae_threshold.joblib")

    distribution.to_csv(OUTPUTS_DIR / "class_distribution.csv")
    print(f"\nSaved cleaned data, indices and AAE threshold ({aae_threshold:.4f}) to {OUTPUTS_DIR}")


if __name__ == "__main__":
    main()
