"""Configuration and shared paths for the hate speech detector project."""
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATASET_PATH = PROJECT_ROOT / "datasets" / "labeled_data.csv"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"
MODELS_DIR = PROJECT_ROOT / "models"
DOCS_DIR = PROJECT_ROOT / "docs"

RANDOM_STATE = 42
TEST_SIZE = 0.2

CLASS_NAMES = {0: "hate_speech", 1: "offensive_language", 2: "neither"}
CLASS_LABELS = ["hate_speech", "offensive_language", "neither"]

TFIDF_MAX_FEATURES = 3000
TFIDF_NGRAM_RANGE = (1, 2)
