from __future__ import annotations

from typing import Any, Dict, List

from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.config import get_default_model, get_prompt_template
from app.service import extract_weaknesses

load_dotenv()

DEFAULT_MODEL = get_default_model()
PROMPT_TEMPLATE = get_prompt_template()

app = FastAPI(title="test_analysis_api")


class WeaknessRequest(BaseModel):
    incorrect_cases: List[Dict[str, Any]] = Field(
        ..., description="List of incorrect question cases with student and correct answers."
    )
    model_name: str = Field(
        default=DEFAULT_MODEL, description="Gemini model name."
    )


class WeaknessResponse(BaseModel):
    weaknesses: List[Dict[str, Any]]


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/test-analysis", response_model=WeaknessResponse)
def weaknesses(payload: WeaknessRequest) -> WeaknessResponse:
    weaknesses = extract_weaknesses(
        payload.incorrect_cases,
        payload.model_name,
        PROMPT_TEMPLATE,
    )
    return WeaknessResponse(weaknesses=weaknesses)
