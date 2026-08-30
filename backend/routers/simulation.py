"""LLM-based comment generation endpoint."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, field_validator

from services.comment_generator import MAX_COUNT, generate_comments

router = APIRouter(tags=["simulation"])


class GenerateRequest(BaseModel):
    topic: str = Field(..., min_length=1)
    count: int = Field(default=20, ge=1, le=MAX_COUNT)


class GenerateResponse(BaseModel):
    comments: list[dict]


@router.post("/generate-comments", response_model=GenerateResponse)
async def generate_comments_endpoint(payload: GenerateRequest):
    try:
        comments = await generate_comments(payload.topic, payload.count)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception:
        raise HTTPException(
            status_code=502,
            detail="Échec de la génération de commentaires par le fournisseur LLM.",
        )
    return {"comments": comments}
