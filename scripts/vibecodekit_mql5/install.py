#!/usr/bin/env python3
"""install — Reconcile-install overlay into target project.

Copies Include/, scaffolds/, and scripts/ into target MetaTrader directory.
Usage: mql5-install --target /path/to/MQL5 [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path


def find_source_root() -> Path | None:
    for candidate in [Path.cwd(), Path(__file__).resolve().parent.parent.parent]:
        if (candidate / "Include" / "CPipNormalizer.mqh").exists():
            return candidate
    return None


def install_overlay(target: Path, dry_run: bool = False) -> dict:
    source = find_source_root()
    if not source:
        return {"success": False, "error": "Source root not found"}

    if not target.exists():
        return {"success": False, "error": f"Target not found: {target}"}

    copies = []
    include_src = source / "Include"
    include_dst = target / "Include" / "vibecodekit"
    if include_src.exists():
        for f in include_src.glob("*.mqh"):
            dst = include_dst / f.name
            copies.append({"src": str(f), "dst": str(dst)})
            if not dry_run:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, dst)

    scaffolds_src = source / "scaffolds"
    scaffolds_dst = target / "vibecodekit-scaffolds"
    if scaffolds_src.exists() and not dry_run:
        if scaffolds_dst.exists():
            shutil.rmtree(scaffolds_dst)
        shutil.copytree(scaffolds_src, scaffolds_dst)
        copies.append({"src": str(scaffolds_src), "dst": str(scaffolds_dst)})

    return {"success": True, "dry_run": dry_run, "copies": len(copies), "details": copies[:10]}


def main() -> int:
    parser = argparse.ArgumentParser(description="Install overlay")
    parser.add_argument("--target", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = install_overlay(args.target, args.dry_run)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        mode = "DRY RUN" if result.get("dry_run") else "INSTALLED"
        if result["success"]:
            print(f"Install [{mode}]: {result['copies']} file(s)")
        else:
            print(f"Error: {result['error']}")

    return 0 if result["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
