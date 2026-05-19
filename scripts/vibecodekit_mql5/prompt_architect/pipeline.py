"""Pipeline plan rendering for Prompt Architect configs."""
from __future__ import annotations

import json
from typing import Any

from vibecodekit_mql5.prompt_architect.bridge import build_rri_bridge
from vibecodekit_mql5.prompt_architect.recommend import recommend_preset


def build_pipeline_plan(config: dict[str, Any], config_path: str = "ea-settings.json") -> dict[str, Any]:
    """Build deterministic next commands for scaffold and gate execution."""
    recommendation = recommend_preset(config)
    bridge = build_rri_bridge(config)
    name = config["name"]
    ea_path = f"./work/{name}/{name}.mq5"
    return {
        "schema_version": "1.0",
        "ea": name,
        "rri_mode": bridge["mode"],
        "recommended": recommendation,
        "artifacts": {
            "rri_plan": "rri-plan.md",
            "vision": "vision.md",
            "requirements": "requirements.json",
            "blueprint": "blueprint.md",
            "matrix_html": "matrix.html",
        },
        "commands": [
            {
                "step": 1,
                "name": "validate_prompt_config",
                "command": (
                    f"mql5-prompt-architect --config {config_path} "
                    "--validate --recommend-preset --json"
                ),
            },
            {
                "step": 2,
                "name": "generate_planning_artifacts",
                "command": (
                    f"mql5-prompt-architect --config {config_path} "
                    "--rri-plan rri-plan.md --vision vision.md "
                    "--requirements requirements.json --blueprint blueprint.md"
                ),
            },
            {
                "step": 3,
                "name": "build_scaffold",
                "command": (
                    f"mql5-build --preset {recommendation['preset']} "
                    f"--stack {recommendation['stack']} --name {name} --output ./work"
                ),
            },
            {"step": 4, "name": "lint", "command": f"mql5-lint {ea_path}"},
            {"step": 5, "name": "compile", "command": f"mql5-compile {ea_path}"},
            {
                "step": 6,
                "name": "permission_gate",
                "command": f"mql5-permission --ea {ea_path} --mode {bridge['mode']} --json",
            },
            {
                "step": 7,
                "name": "quality_matrix",
                "command": f"mql5-matrix --mode {bridge['mode']} --html matrix.html",
            },
        ],
    }


def render_pipeline_plan(config: dict[str, Any], config_path: str = "ea-settings.json") -> str:
    """Render the pipeline plan as stable JSON text."""
    return json.dumps(build_pipeline_plan(config, config_path), indent=2)
