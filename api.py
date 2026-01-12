from __future__ import annotations

from typing import Any, Dict, List

from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel, Field

from functions.config import get_default_model, get_prompt_template
from functions.service import extract_weaknesses
from functions.utils.json_naming_converter import convert_keys_snake_to_camel

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


@app.post("/v1/test-analysis", response_model=WeaknessResponse)
def weaknesses(request: WeaknessRequest) -> WeaknessResponse:
    weaknesses = extract_weaknesses(
        request.incorrect_cases,
        request.model_name,
        PROMPT_TEMPLATE,
    )
    converted = convert_keys_snake_to_camel(weaknesses)
    return WeaknessResponse(weaknesses=converted)
