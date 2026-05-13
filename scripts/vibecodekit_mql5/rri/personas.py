#!/usr/bin/env python3
"""RRI personas loader — 6 MQL5-domain personas with question banks."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

PERSONAS_DIR = Path(__file__).resolve().parents[3] / "docs" / "rri-personas"

PERSONA_NAMES = [
    "trader", "risk-auditor", "broker-engineer",
    "strategy-architect", "devops", "perf-analyst",
]

MODE_QUESTION_COUNTS = {
    "PERSONAL": 5,
    "TEAM": 12,
    "ENTERPRISE": 25,
}


def load_persona(name: str) -> dict[str, Any]:
    """Load a persona YAML file."""
    path = PERSONAS_DIR / f"{name}.yaml"
    if not path.exists():
        return {"name": name, "questions": [], "error": "file not found"}
    with path.open() as f:
        return yaml.safe_load(f) or {"name": name, "questions": []}


def load_all_personas() -> list[dict[str, Any]]:
    """Load all 6 personas."""
    return [load_persona(name) for name in PERSONA_NAMES]


def get_questions_for_mode(persona: dict, mode: str = "TEAM") -> list:
    """Filter questions by mode count."""
    questions = persona.get("questions", [])
    limit = MODE_QUESTION_COUNTS.get(mode, 12)
    return questions[:limit]
