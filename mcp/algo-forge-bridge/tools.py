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


def handle_clone(params: dict) -> dict:
    """Clone an existing EA into a forge workspace for iteration."""
    ea = Path(params.get("ea_path", ""))
    if not ea.exists():
        return {"error": f"EA not found: {ea}"}
    ws = Path(params.get("workspace", ".forge/clone"))
    ws.mkdir(parents=True, exist_ok=True)
    import shutil
    dst = ws / ea.name
    shutil.copy2(ea, dst)
    return {"status": "ok", "cloned": str(ea), "workspace": str(ws), "target": str(dst)}


def handle_commit(params: dict) -> dict:
    """Commit current best candidate as the new baseline."""
    ws = Path(params["workspace"])
    candidate_id = params.get("candidate_id", "best")
    history_path = ws / "history.json"
    history = json.loads(history_path.read_text()) if history_path.exists() else []
    entry = {"generation": len(history) + 1, "candidate": candidate_id, "status": "committed"}
    history.append(entry)
    history_path.write_text(json.dumps(history, indent=2))
    return {"status": "ok", "generation": entry["generation"], "candidate": candidate_id}


def handle_repo_list(params: dict) -> dict:
    """List all forge workspaces."""
    forge_root = Path(params.get("root", ".forge"))
    if not forge_root.exists():
        return {"status": "ok", "workspaces": [], "count": 0}
    workspaces = []
    for ws_dir in forge_root.iterdir():
        if ws_dir.is_dir():
            config = ws_dir / "forge-config.json"
            workspaces.append({"name": ws_dir.name, "has_config": config.exists(), "path": str(ws_dir)})
    return {"status": "ok", "workspaces": workspaces, "count": len(workspaces)}


TOOLS.extend([
    {"name": "clone", "description": "Clone an EA into a forge workspace for iteration",
     "inputSchema": {"type": "object",
                     "properties": {"ea_path": {"type": "string"}, "workspace": {"type": "string"}},
                     "required": ["ea_path"]}},
    {"name": "commit", "description": "Commit best candidate as new baseline",
     "inputSchema": {"type": "object",
                     "properties": {"workspace": {"type": "string"}, "candidate_id": {"type": "string"}},
                     "required": ["workspace"]}},
    {"name": "repo_list", "description": "List all forge workspaces",
     "inputSchema": {"type": "object",
                     "properties": {"root": {"type": "string"}}}},
])

HANDLERS = {"init_workspace": handle_init_workspace,
            "evaluate": handle_evaluate,
            "suggest_params": handle_suggest_params,
            "clone": handle_clone,
            "commit": handle_commit,
            "repo_list": handle_repo_list}
