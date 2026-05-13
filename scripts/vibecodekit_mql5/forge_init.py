#!/usr/bin/env python3
"""Algo Forge — initialize a strategy iteration workspace.

Creates a forge workspace with parameter space definition,
fitness function config, and iteration history.

Usage:
    mql5-forge-init --ea MyEA.mq5 --workspace .forge/MyEA/
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


def extract_inputs(ea_path: Path) -> list[dict]:
    """Extract input parameters from EA source."""
    content = ea_path.read_text(encoding="utf-8", errors="replace")
    inputs: list[dict] = []
    for m in re.finditer(
        r"^\s*input\s+(\w+)\s+(\w+)\s*=\s*([^;]+);", content, re.M
    ):
        dtype, name, default = m.group(1), m.group(2), m.group(3).strip()
        inputs.append({"name": name, "type": dtype, "default": default,
                       "min": "", "max": "", "step": ""})
    return inputs


def create_workspace(ea_path: Path, workspace: Path) -> dict:
    """Create forge workspace directory with config files."""
    workspace.mkdir(parents=True, exist_ok=True)

    inputs = extract_inputs(ea_path) if ea_path.exists() else []

    config = {
        "ea_source": str(ea_path),
        "parameters": inputs,
        "fitness": {"primary": "profit_factor", "secondary": "sharpe_ratio",
                    "constraints": {"max_drawdown_pct": 30,
                                    "min_trades": 100}},
        "optimization": {"method": "genetic", "population": 50,
                         "generations": 20, "mutation_rate": 0.1},
        "iterations": [],
    }

    config_path = workspace / "forge-config.json"
    config_path.write_text(json.dumps(config, indent=2))

    (workspace / "results").mkdir(exist_ok=True)
    (workspace / "generations").mkdir(exist_ok=True)

    return {"workspace": str(workspace), "parameters": len(inputs),
            "config": str(config_path)}


def main() -> int:
    ap = argparse.ArgumentParser(description="Algo Forge init")
    ap.add_argument("--ea", type=Path, required=True)
    ap.add_argument("--workspace", type=Path, default=Path(".forge/default"))
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    result = create_workspace(args.ea, args.workspace)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Forge workspace: {result['workspace']}")
        print(f"Parameters extracted: {result['parameters']}")
        print(f"Config: {result['config']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
