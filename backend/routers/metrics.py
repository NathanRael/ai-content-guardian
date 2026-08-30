"""Model metrics endpoint (cached at training time)."""
import json
from pathlib import Path

from fastapi import APIRouter, HTTPException

OUTPUTS_DIR = Path(__file__).resolve().parents[1] / "outputs"
METRICS_FILE = OUTPUTS_DIR / "metrics.json"
EDGE_CASES_FILE = OUTPUTS_DIR / "edge_cases.json"

router = APIRouter(tags=["metrics"])


@router.get("/metrics")
async def get_metrics():
    if not METRICS_FILE.exists():
        raise HTTPException(
            status_code=503,
            detail="Métriques non disponibles. Exécutez d'abord train.py.",
        )
    with open(METRICS_FILE, encoding="utf-8") as f:
        metrics = json.load(f)

    edge_cases = []
    if EDGE_CASES_FILE.exists():
        with open(EDGE_CASES_FILE, encoding="utf-8") as f:
            edge_cases = json.load(f)

    return {
        "logistic_regression": metrics["logistic_regression"],
        "random_forest": metrics["random_forest"],
        "edge_cases": edge_cases,
    }
