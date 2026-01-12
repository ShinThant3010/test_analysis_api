from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict

import yaml

_CONFIG_CACHE: Dict[str, Any] | None = None
_CONFIG_PATH = Path(__file__).resolve().parents[1] / "config.yaml"
_DEFAULT_PROMPT_TEMPLATE = """You are a diagnostic engine for assessment tests across many domains.

You receive a JSON array of questions where the student answered incorrectly.

Task:
1. Look across ALL incorrect questions for this single student and test.
2. Find concrete, reusable weaknesses and error patterns (not just "Grammar" or "Math").
3. Group evidence questions that share the same weakness or pattern.
4. Group ONLY when the underlying error pattern is the same (e.g., consistent rule misuse or concept confusion).
5. Keep distinct error patterns separate, even if the topics feel loosely related.
6. Aim for the smallest number of weaknesses that still faithfully separates different patterns (do not over-merge or over-split).
7. Prefer grouping closely related sub-rules under one weakness when they belong to the same concept domain.

Output format (JSON ONLY, no extra text):

[
  {
    "weakness": "short name (1 sentence max, specific to the pattern)",
    "pattern_type": "language | numeracy | logical_reasoning | reading_comprehension | domain_knowledge | test_strategy | other",
    "description": "2-4 sentences explaining the pattern and why errors happen.",
    "evidence_question_ids": [<questionId>, ...],
    "frequency": <number of questions that show this pattern>
  }
]

Here is the JSON array of incorrect questions:

{cases_json}

Respond with ONLY the JSON array as described above.
"""


def _load_config() -> Dict[str, Any]:
    global _CONFIG_CACHE
    if _CONFIG_CACHE is not None:
        return _CONFIG_CACHE

    if not _CONFIG_PATH.exists():
        _CONFIG_CACHE = {}
        return _CONFIG_CACHE

    with _CONFIG_PATH.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}

    if not isinstance(data, dict):
        data = {}

    _CONFIG_CACHE = data
    return _CONFIG_CACHE


def get_default_model() -> str:
    config = _load_config()
    return os.getenv("GENERATION_MODEL", config.get("default_model", "gemini-2.5-flash"))


def get_prompt_template() -> str:
    config = _load_config()
    return config.get("prompt_template") or _DEFAULT_PROMPT_TEMPLATE
