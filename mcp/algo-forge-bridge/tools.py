#!/usr/bin/env python3
"""algo-forge-bridge tools — strategy optimization and iteration."""
from __future__ import annotations

import json
from pathlib import Path

TOOLS: list[dict] = [
    {"name": "init_workspace", "description": "Initialize an Algo Forge workspace",
     "inputSchema": {"type": "object",
                     "properties": {"ea_path": {"type": "string"},
                                    "workspace": {"type": "string"}},
                     "required": ["ea_path"]}},
    {"name": "evaluate", "description": "Evaluate and rank strategy candidates",
     "inputSchema": {"type": "object",
                     "properties": {"workspace": {"type": "string"}},
                     "required": ["workspace"]}},
    {"name": "suggest_params", "description": "Suggest next parameter set based on history",
     "inputSchema": {"type": "object",
                     "properties": {"workspace": {"type": "string"}},
                     "required": ["workspace"]}},
]


def handle_init_workspace(params: dict) -> dict:
    """Initialize forge workspace via forge_init module."""
    import sys
    scripts_dir = str(Path(__file__).resolve().parents[2] / "scripts")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    from vibecodekit_mql5.forge_init import create_workspace
    ea = Path(params["ea_path"])
    ws = Path(params.get("workspace", ".forge/default"))
    return create_workspace(ea, ws)


def handle_evaluate(params: dict) -> dict:
    """Evaluate candidates in workspace."""
    import sys
    scripts_dir = str(Path(__file__).resolve().parents[2] / "scripts")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    from vibecodekit_mql5.forge_pr import rank_candidates
    ws = Path(params["workspace"])
    results_dir = ws / "results"
    candidates = rank_candidates(ws, results_dir)
    return {"workspace": str(ws), "candidates": candidates[:10],
            "total": len(candidates)}


def handle_suggest_params(params: dict) -> dict:
    """Suggest next parameter set based on workspace config."""
    ws = Path(params["workspace"])
    config_path = ws / "forge-config.json"
    if not config_path.exists():
        return {"error": "Workspace not initialized"}

    config = json.loads(config_path.read_text())
    parameters = config.get("parameters", [])
    opt = config.get("optimization", {})

    suggestions: list[dict] = []
    for p in parameters:
        s = {"name": p["name"], "type": p["type"],
             "current": p.get("default", ""),
             "suggestion": "vary ±10% from current"}
        suggestions.append(s)

    return {"method": opt.get("method", "genetic"),
            "population": opt.get("population", 50),
            "suggestions": suggestions}


HANDLERS = {"init_workspace": handle_init_workspace,
            "evaluate": handle_evaluate,
            "suggest_params": handle_suggest_params}
