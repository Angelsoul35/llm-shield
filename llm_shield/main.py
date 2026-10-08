"""llm-shield HTTP API."""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field

from .shield import Shield

app = FastAPI(
    title="llm-shield",
    version="1.0.0",
    summary="Guardrails against prompt injection and data leaks for LLM apps.",
)

_shield: Shield | None = None


def get_shield() -> Shield:
    global _shield
    if _shield is None:
        _shield = Shield()
    return _shield


class TextRequest(BaseModel):
    text: str = Field(min_length=1)


@app.get("/health", tags=["ops"])
def health() -> dict:
    return {"status": "ok"}


@app.post("/scan/input", tags=["shield"])
def scan_input(request: TextRequest) -> dict:
    return get_shield().scan_input(request.text).as_dict()


@app.post("/scan/output", tags=["shield"])
def scan_output(request: TextRequest) -> dict:
    return get_shield().scan_output(request.text).as_dict()
