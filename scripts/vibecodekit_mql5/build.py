#!/usr/bin/env python3
"""Scaffold renderer — generate EA project from scaffold template.

Usage:
    mql5-build --preset stdlib --stack netting --name MyEA --output ./out/
    mql5-build --list
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCAFFOLDS_DIR = REPO_ROOT / "scaffolds"

PRESETS = ["stdlib", "wizard-composable", "portfolio-basket", "ml-onnx"]
STACKS = ["netting", "hedging", "python-bridge"]


def list_presets() -> list[dict[str, list[str]]]:
    """Return available preset×stack combinations."""
    result = []
    for preset_dir in sorted(SCAFFOLDS_DIR.iterdir()):
        if not preset_dir.is_dir():
            continue
        stacks = [d.name for d in sorted(preset_dir.iterdir()) if d.is_dir()]
        result.append({"preset": preset_dir.name, "stacks": stacks})
    return result


def render_scaffold(preset: str, stack: str, ea_name: str, output: Path) -> Path:
    """Copy and rename scaffold to output directory."""
    src = SCAFFOLDS_DIR / preset / stack
    if not src.exists():
        raise FileNotFoundError(f"Scaffold not found: {src}")

    dst = output / ea_name
    dst.mkdir(parents=True, exist_ok=True)

    for item in src.rglob("*"):
        if item.is_file():
            rel = item.relative_to(src)
            new_name = str(rel).replace("EAName", ea_name)
            target = dst / new_name
            target.parent.mkdir(parents=True, exist_ok=True)
            content = item.read_text(encoding="utf-8", errors="replace")
            content = content.replace("EAName", ea_name)
            target.write_text(content, encoding="utf-8")

    print(f"Rendered {preset}/{stack} -> {dst}")
    return dst


def main() -> int:
    parser = argparse.ArgumentParser(description="MQL5 EA scaffold builder")
    parser.add_argument("--preset", choices=PRESETS, help="Scaffold preset")
    parser.add_argument("--stack", choices=STACKS, default="netting")
    parser.add_argument("--name", default="MyEA", help="EA name (replaces EAName)")
    parser.add_argument("--output", type=Path, default=Path("."), help="Output dir")
    parser.add_argument("--list", action="store_true", help="List available presets")
    args = parser.parse_args()

    if args.list:
        for item in list_presets():
            print(f"  {item['preset']}: {', '.join(item['stacks'])}")
        return 0

    if not args.preset:
        parser.error("--preset required (use --list to see options)")

    try:
        render_scaffold(args.preset, args.stack, args.name, args.output)
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
