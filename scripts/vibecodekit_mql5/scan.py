#!/usr/bin/env python3
"""scan — Read-only repository exploration.

Scans project structure, identifies EAs, includes, and anti-pattern baseline.
Usage: mql5-scan [--path .] [--json]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def scan_project(root: Path) -> dict:
    mq5_files = list(root.rglob("*.mq5"))
    mqh_files = list(root.rglob("*.mqh"))
    py_files = list(root.rglob("*.py"))
    yaml_files = list(root.rglob("*.yaml")) + list(root.rglob("*.yml"))

    scaffolds = []
    scaffolds_dir = root / "scaffolds"
    if scaffolds_dir.exists():
        for preset in scaffolds_dir.iterdir():
            if preset.is_dir():
                stacks = [s.name for s in preset.iterdir() if s.is_dir()]
                scaffolds.append({"preset": preset.name, "stacks": stacks})

    includes = []
    inc_dir = root / "Include"
    if inc_dir.exists():
        includes = [f.name for f in inc_dir.glob("*.mqh")]

    return {
        "root": str(root),
        "mq5_count": len(mq5_files),
        "mqh_count": len(mqh_files),
        "py_count": len(py_files),
        "yaml_count": len(yaml_files),
        "scaffolds": scaffolds,
        "includes": includes,
        "has_pyproject": (root / "pyproject.toml").exists(),
        "has_ci": (root / ".github" / "workflows" / "ci.yml").exists(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan project")
    parser.add_argument("--path", type=Path, default=Path("."))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = scan_project(args.path.resolve())
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Scan: {result['root']}")
        print(f"  MQ5: {result['mq5_count']}, MQH: {result['mqh_count']}, Python: {result['py_count']}")
        print(f"  Scaffolds: {len(result['scaffolds'])}, Includes: {len(result['includes'])}")
        print(f"  CI: {'yes' if result['has_ci'] else 'no'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
