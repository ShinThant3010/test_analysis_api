from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, Header, Response
from pydantic import BaseModel, Field

from functions.config import get_default_model, get_prompt_template
from functions.service import extract_weaknesses
from functions.utils.json_naming_converter import convert_keys_snake_to_camel
from functions.utils.token_log import get_token_entries, reset_token_log

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
    log: Optional[List[Dict[str, Any]]] = None


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/test-analysis", response_model=WeaknessResponse, response_model_exclude_none=True)
def weaknesses(
    request: WeaknessRequest,
    response: Response,
    include_log: bool = Header(default=True, alias="x-log"),
) -> WeaknessResponse:
    
    start = time.perf_counter()
    if include_log:
        reset_token_log()
    weaknesses = extract_weaknesses(
        request.incorrect_cases,
        request.model_name,
        PROMPT_TEMPLATE,
        log_usage=include_log,
    )
    converted = convert_keys_snake_to_camel(weaknesses)
    
    runtime_seconds = time.perf_counter() - start
    response.headers["x-runtime-seconds"] = f"{runtime_seconds:.6f}"
    
    log_entries = get_token_entries() if include_log else None
    return WeaknessResponse(weaknesses=converted, log=log_entries)
