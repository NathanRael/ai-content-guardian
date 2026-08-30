"""FastAPI entry point for AI Content Guardian."""
from __future__ import annotations

import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv

load_dotenv()


from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from routers.analyze import router as analyze_router
from routers.audit import router as audit_router
from routers.metrics import router as metrics_router
from routers.model_info import router as model_info_router
from routers.simulation import router as simulation_router
from services.ml_pipeline import load_models


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_models()
    yield


app = FastAPI(
    title="AI Content Guardian",
    description="Backend de modération de contenu avec audit de biais dialectal.",
    version="0.2.0",
    lifespan=lifespan,
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": "Données invalides. Vérifiez le format de la requête."},
    )

origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze_router)
app.include_router(simulation_router)
app.include_router(metrics_router)
app.include_router(audit_router)
app.include_router(model_info_router)


@app.get("/health")
async def health():
    return {"status": "ok"}
