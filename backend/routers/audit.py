"""Dialect bias audit endpoint."""
import json
from pathlib import Path

from fastapi import APIRouter, HTTPException

OUTPUTS_DIR = Path(__file__).resolve().parents[1] / "outputs"
AUDIT_FILE = OUTPUTS_DIR / "bias_audit.json"

router = APIRouter(tags=["audit"])


@router.get("/bias-audit")
async def get_bias_audit():
    if not AUDIT_FILE.exists():
        raise HTTPException(
            status_code=503,
            detail="Audit de biais non disponible. Exécutez d'abord train.py.",
        )
    with open(AUDIT_FILE, encoding="utf-8") as f:
        return json.load(f)
