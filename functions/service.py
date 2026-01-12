from __future__ import annotations

import ast
import json
import os
import time
import uuid
from typing import Any, Dict, List

from fastapi import HTTPException
from google import genai

def _get_client() -> genai.Client:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GOOGLE_API_KEY is missing")
    return genai.Client(api_key=api_key)


def _remove_code_fences(text: str) -> str:
    text = text.replace("```json", "")
    text = text.replace("```", "")
    return text.strip()


def _convert_llm_weaknesses(raw_text: str) -> List[Dict[str, Any]]:
    text = raw_text.strip()

    try:
        data = json.loads(text)
        if isinstance(data, list):
            return data
        return [data]
    except Exception:
        pass

    try:
        data = ast.literal_eval(text)
        if isinstance(data, list):
            return data
        return [data]
    except Exception:
        print("Failed to parse LLM response as JSON or Python literal.")
        print("LLM Response:", text)
        pass

    raise HTTPException(status_code=502, detail="Model response is not valid JSON.")

def extract_weaknesses(
    incorrect_cases: List[Dict[str, Any]],
    model_name: str,
    prompt_template: str,
) -> List[Dict[str, Any]]:
    if not incorrect_cases:
        return []

    cases_json = json.dumps(incorrect_cases, ensure_ascii=False, indent=2)
    template = prompt_template
    prompt = template.format(cases_json=cases_json)

    client = _get_client()
    start = time.time()
    response = None
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=[{"parts": [{"text": prompt}]}],
        )
    finally:
        _ = time.time() - start

    if response is None or not getattr(response, "text", None):
        raise HTTPException(status_code=502, detail="No response from model")

    weaknesses = _convert_llm_weaknesses(_remove_code_fences(response.text))

    for item in weaknesses:
        item.setdefault("id", str(uuid.uuid4()))

    return weaknesses
