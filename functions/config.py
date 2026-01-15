from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict

import yaml

_CONFIG_CACHE: Dict[str, Any] | None = None
_CONFIG_PATH = Path(__file__).resolve().parents[1] / "config.yaml"

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
    return config.get("prompt_template")
