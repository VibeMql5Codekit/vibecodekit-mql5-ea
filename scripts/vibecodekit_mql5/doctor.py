#!/usr/bin/env python3
"""doctor — Health check for vibecodekit-mql5-ea installation.

Verifies: Python package, CLI tools, scaffolds, includes, tests.
Usage: mql5-doctor [--json]
"""
from __future__ import annotations

import argparse
import importlib
import json
import shutil
import sys
from pathlib import Path


def find_project_root() -> Path | None:
    for candidate in [Path.cwd(), Path(__file__).resolve().parent.parent.parent]:
        if (candidate / "pyproject.toml").exists():
            return candidate
    return None


def check_health() -> dict:
    checks = []
    root = find_project_root()

    checks.append({"name": "project_root", "pass": root is not None,
                    "detail": str(root) if root else "Not found"})

    try:
        import vibecodekit_mql5
        checks.append({"name": "package_importable", "pass": True, "detail": "OK"})
    except ImportError:
        checks.append({"name": "package_importable", "pass": False, "detail": "pip install -e '.[dev]'"})

    for cmd in ["mql5-build", "mql5-lint", "mql5-compile", "mql5-pip-normalize"]:
        found = shutil.which(cmd) is not None
        checks.append({"name": f"cli_{cmd}", "pass": found, "detail": "found" if found else "missing"})

    if root:
        for d in ["Include", "scaffolds", "scripts", "tests", "docs"]:
            exists = (root / d).is_dir()
            checks.append({"name": f"dir_{d}", "pass": exists, "detail": str(root / d)})

        includes = ["CPipNormalizer.mqh", "CRiskGuard.mqh", "CMagicRegistry.mqh",
                     "CSpreadGuard.mqh", "CMfeMaeLogger.mqh", "COnnxLoader.mqh", "CAsyncTradeManager.mqh"]
        for inc in includes:
            exists = (root / "Include" / inc).exists()
            checks.append({"name": f"include_{inc}", "pass": exists})

    passed = sum(1 for c in checks if c["pass"])
    return {"passed": passed, "total": len(checks), "checks": checks}


def main() -> int:
    parser = argparse.ArgumentParser(description="Health check")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = check_health()
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Doctor: {result['passed']}/{result['total']} checks pass")
        for c in result["checks"]:
            icon = "+" if c["pass"] else "X"
            detail = f" ({c.get('detail', '')})" if c.get("detail") else ""
            print(f"  [{icon}] {c['name']}{detail}")

    return 0 if result["passed"] == result["total"] else 1


if __name__ == "__main__":
    sys.exit(main())
