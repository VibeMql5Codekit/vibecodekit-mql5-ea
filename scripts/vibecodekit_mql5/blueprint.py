#!/usr/bin/env python3
"""blueprint — Architecture + data model + interface generator.

Usage: mql5-blueprint --vision vision.md --output blueprint.md [--json]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

BLUEPRINT_SECTIONS = [
    "architecture", "data_flow", "include_libraries", "cli_commands",
    "req_matrix", "invariants", "risk_mitigations", "task_decomposition",
]


def generate_blueprint(vision_path: Path | None = None, name: str = "EA") -> dict:
    sections = {}
    for section in BLUEPRINT_SECTIONS:
        sections[section] = f"[{section}] — to be filled based on vision and RRI"

    if vision_path and vision_path.exists():
        content = vision_path.read_text(encoding="utf-8", errors="replace")
        if "Goal" in content:
            sections["architecture"] = "Architecture derived from vision document"

    return {"name": name, "sections": sections, "total_sections": len(sections)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Blueprint generator")
    parser.add_argument("--vision", type=Path, default=None)
    parser.add_argument("--name", default="EA")
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = generate_blueprint(args.vision, args.name)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Blueprint: {args.name} ({result['total_sections']} sections)")
        for k, v in result["sections"].items():
            print(f"  {k}: {v[:60]}")
    if args.output:
        args.output.write_text(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
