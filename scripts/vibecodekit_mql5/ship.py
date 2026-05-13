#!/usr/bin/env python3
"""ship — Git tag + push release.

Tags the current commit and pushes to remote.
Usage: mql5-ship --version 1.0.0 [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys


def get_current_version() -> str:
    try:
        from pathlib import Path
        version_file = Path(__file__).resolve().parent.parent.parent / "VERSION"
        if version_file.exists():
            return version_file.read_text().strip()
    except Exception:
        pass
    return "0.0.0"


def ship_release(version: str, dry_run: bool = False) -> dict:
    tag = f"v{version}"
    steps = []

    if dry_run:
        steps.append({"step": "tag", "command": f"git tag -a {tag} -m 'Release {tag}'", "status": "dry-run"})
        steps.append({"step": "push", "command": f"git push origin {tag}", "status": "dry-run"})
        return {"success": True, "tag": tag, "dry_run": True, "steps": steps}

    try:
        subprocess.run(["git", "tag", "-a", tag, "-m", f"Release {tag}"], check=True, capture_output=True)
        steps.append({"step": "tag", "status": "done"})
    except subprocess.CalledProcessError as e:
        return {"success": False, "error": f"Tag failed: {e.stderr.decode()}", "steps": steps}

    try:
        subprocess.run(["git", "push", "origin", tag], check=True, capture_output=True)
        steps.append({"step": "push", "status": "done"})
    except subprocess.CalledProcessError as e:
        return {"success": False, "error": f"Push failed: {e.stderr.decode()}", "steps": steps}

    return {"success": True, "tag": tag, "dry_run": False, "steps": steps}


def main() -> int:
    parser = argparse.ArgumentParser(description="Ship release")
    parser.add_argument("--version", default=None, help="Version to tag")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    version = args.version or get_current_version()
    result = ship_release(version, args.dry_run)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        mode = "DRY RUN" if result.get("dry_run") else "LIVE"
        print(f"Ship [{mode}]: {result.get('tag', 'unknown')}")
        for s in result.get("steps", []):
            print(f"  {s['step']}: {s['status']}")
        if not result["success"]:
            print(f"  Error: {result['error']}")

    return 0 if result["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
