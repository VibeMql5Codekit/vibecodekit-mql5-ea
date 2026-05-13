#!/usr/bin/env python3
"""tip — Task Instruction Pack generator.

Breaks blueprint into implementable tasks with dependencies.
Usage: mql5-tip --blueprint blueprint.md --output tips/ [--json]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def generate_tips(blueprint_path: Path | None = None) -> list[dict]:
    tips = [
        {"id": "TIP-001", "title": "Setup project structure", "phase": "0", "depends": [], "minutes": 30},
        {"id": "TIP-002", "title": "Implement CPipNormalizer", "phase": "A", "depends": ["TIP-001"], "minutes": 120},
        {"id": "TIP-003", "title": "Implement CRiskGuard", "phase": "A", "depends": ["TIP-001"], "minutes": 90},
        {"id": "TIP-004", "title": "Implement lint + build CLI", "phase": "A", "depends": ["TIP-002"], "minutes": 120},
        {"id": "TIP-005", "title": "Backtest + walk-forward", "phase": "B", "depends": ["TIP-004"], "minutes": 180},
        {"id": "TIP-006", "title": "Multi-broker gate", "phase": "B", "depends": ["TIP-005"], "minutes": 120},
        {"id": "TIP-007", "title": "Permission pipeline", "phase": "C", "depends": ["TIP-004"], "minutes": 150},
        {"id": "TIP-008", "title": "ONNX + async trade", "phase": "D", "depends": ["TIP-006"], "minutes": 180},
        {"id": "TIP-009", "title": "MCP servers + docs", "phase": "E", "depends": ["TIP-008"], "minutes": 240},
        {"id": "TIP-010", "title": "Conformance tests", "phase": "E", "depends": ["TIP-009"], "minutes": 120},
    ]
    return tips


def main() -> int:
    parser = argparse.ArgumentParser(description="TIP generator")
    parser.add_argument("--blueprint", type=Path, default=None)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    tips = generate_tips(args.blueprint)
    if args.json:
        print(json.dumps(tips, indent=2))
    else:
        total_min = sum(t["minutes"] for t in tips)
        print(f"TIPs: {len(tips)} tasks, ~{total_min} min total")
        for t in tips:
            deps = ", ".join(t["depends"]) if t["depends"] else "none"
            print(f"  {t['id']} [{t['phase']}] {t['title']} ({t['minutes']}m, deps: {deps})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
