"""LLM-based simulated comment generation via LangChain + Groq.

This module has NO dependency on ml_pipeline.py or any classification code.
The generative model is used only to create demo comments, never to classify.
"""
from __future__ import annotations

import os
import uuid

from langchain_groq import ChatGroq


DEFAULT_COUNT = 10
MAX_COUNT = 50


def _build_prompt(topic: str, count: int) -> str:
    return (
        f"Generate {count} short social-media style comments about '{topic}'. "
        "Produce a realistic mix: some neutral, some mildly offensive or snarky, "
        "and some borderline/provocative (for a content-moderation demo). "
        "Do NOT include actually hateful, threatening or extremist content. "
        "Each comment must be on its own line. No numbering, no labels."
    )


async def generate_comments(topic: str, count: int = DEFAULT_COUNT) -> list[dict]:
    """Call Groq via LangChain and return comments."""
    if not topic or not topic.strip():
        raise ValueError("Le sujet ne peut pas être vide.")
    if count < 1 or count > MAX_COUNT:
        raise ValueError(f"Le nombre de commentaires doit être entre 1 et {MAX_COUNT}.")

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("Clé API Groq manquante (GROQ_API_KEY).")

    model_name = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    llm = ChatGroq(
        api_key=api_key,
        model_name=model_name,
        temperature=0.8,
        max_tokens=2048,
    )

    prompt = _build_prompt(topic, count)
    response = await llm.ainvoke(prompt)
    content = response.content or ""

    lines = [line.strip() for line in content.splitlines() if line.strip()]
    return [{"id": str(uuid.uuid4()), "text": line} for line in lines[:count]]
