"""Scaffold preset recommendation for Prompt Architect configs."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
PRESET_MAP_PATH = REPO_ROOT / "docs" / "prompt-architect" / "preset-map.yaml"


def _field(data: dict[str, Any], path: str) -> Any:
    current: Any = data
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def _matches(config: dict[str, Any], conditions: dict[str, Any]) -> bool:
    for path, expected in conditions.items():
        if path == "notes_contains":
            if str(expected).lower() not in str(config.get("notes", "")).lower():
                return False
        elif _field(config, path) != expected:
            return False
    return True


def load_preset_map() -> dict[str, Any]:
    """Load preset recommendation rules."""
    return yaml.safe_load(PRESET_MAP_PATH.read_text(encoding="utf-8"))


def recommend_preset(config: dict[str, Any]) -> dict[str, Any]:
    """Return the first matching preset recommendation."""
    preset_map = load_preset_map()
    for rule in preset_map.get("rules", []):
        if _matches(config, rule.get("when", {})):
            recommendation = dict(rule["recommend"])
            recommendation["rule_id"] = rule["id"]
            if "warning" in rule:
                recommendation["warning"] = rule["warning"]
            return recommendation
    fallback = dict(preset_map["fallback"])
    fallback["rule_id"] = "fallback"
    return fallback
