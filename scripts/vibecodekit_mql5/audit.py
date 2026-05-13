#!/usr/bin/env python3
"""audit — 70-point conformance test suite.

Runs structural + functional checks against vibecodekit-mql5-ea spec.
Usage: mql5-audit [--path .] [--json]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

CONFORMANCE_CHECKS = [
    ("C01", "pyproject.toml exists", lambda r: (r / "pyproject.toml").exists()),
    ("C02", "VERSION file exists", lambda r: (r / "VERSION").exists()),
    ("C03", "README.md exists", lambda r: (r / "README.md").exists()),
    ("C04", "Include/ directory", lambda r: (r / "Include").is_dir()),
    ("C05", "CPipNormalizer.mqh", lambda r: (r / "Include" / "CPipNormalizer.mqh").exists()),
    ("C06", "CRiskGuard.mqh", lambda r: (r / "Include" / "CRiskGuard.mqh").exists()),
    ("C07", "CMagicRegistry.mqh", lambda r: (r / "Include" / "CMagicRegistry.mqh").exists()),
    ("C08", "CSpreadGuard.mqh", lambda r: (r / "Include" / "CSpreadGuard.mqh").exists()),
    ("C09", "CMfeMaeLogger.mqh", lambda r: (r / "Include" / "CMfeMaeLogger.mqh").exists()),
    ("C10", "COnnxLoader.mqh", lambda r: (r / "Include" / "COnnxLoader.mqh").exists()),
    ("C11", "CAsyncTradeManager.mqh", lambda r: (r / "Include" / "CAsyncTradeManager.mqh").exists()),
    ("C12", "scripts/ directory", lambda r: (r / "scripts").is_dir()),
    ("C13", "build.py exists", lambda r: (r / "scripts" / "vibecodekit_mql5" / "build.py").exists()),
    ("C14", "lint.py exists", lambda r: (r / "scripts" / "vibecodekit_mql5" / "lint.py").exists()),
    ("C15", "compile.py exists", lambda r: (r / "scripts" / "vibecodekit_mql5" / "compile.py").exists()),
    ("C16", "pip_normalize.py", lambda r: (r / "scripts" / "vibecodekit_mql5" / "pip_normalize.py").exists()),
    ("C17", "backtest.py", lambda r: (r / "scripts" / "vibecodekit_mql5" / "backtest.py").exists()),
    ("C18", "walkforward.py", lambda r: (r / "scripts" / "vibecodekit_mql5" / "walkforward.py").exists()),
    ("C19", "monte_carlo.py", lambda r: (r / "scripts" / "vibecodekit_mql5" / "monte_carlo.py").exists()),
    ("C20", "multibroker.py", lambda r: (r / "scripts" / "vibecodekit_mql5" / "multibroker.py").exists()),
    ("C21", "trader_check.py", lambda r: (r / "scripts" / "vibecodekit_mql5" / "trader_check.py").exists()),
    ("C22", "scaffolds/ >= 4 presets", lambda r: len(list((r / "scaffolds").iterdir())) >= 4 if (r / "scaffolds").exists() else False),
    ("C23", "tests/ directory", lambda r: (r / "tests").is_dir()),
    ("C24", "docs/ directory", lambda r: (r / "docs").is_dir()),
    ("C25", "docs/PLAN-v5.md", lambda r: (r / "docs" / "PLAN-v5.md").exists()),
    ("C26", "6 RRI personas", lambda r: len(list((r / "docs" / "rri-personas").glob("*.yaml"))) >= 6 if (r / "docs" / "rri-personas").exists() else False),
    ("C27", "8 RRI templates", lambda r: len(list((r / "docs" / "rri-templates").glob("*.tmpl"))) >= 8 if (r / "docs" / "rri-templates").exists() else False),
    ("C28", "7 permission layers", lambda r: len(list((r / "scripts" / "vibecodekit_mql5" / "permission").glob("layer*.py"))) >= 7 if (r / "scripts" / "vibecodekit_mql5" / "permission").exists() else False),
    ("C29", "MCP metaeditor-bridge", lambda r: (r / "mcp" / "metaeditor-bridge" / "server.py").exists()),
    ("C30", "MCP mt5-bridge", lambda r: (r / "mcp" / "mt5-bridge" / "server.py").exists()),
    ("C31", "MCP algo-forge-bridge", lambda r: (r / "mcp" / "algo-forge-bridge" / "server.py").exists()),
    ("C32", "references/ >= 26", lambda r: len(list((r / "docs" / "references").glob("*.md"))) >= 26 if (r / "docs" / "references").exists() else False),
    ("C33", "worked example", lambda r: (r / "examples" / "ea-wizard-macd-sar-eurusd-h1-portfolio").is_dir()),
    ("C34", "onnx_export.py", lambda r: (r / "scripts" / "vibecodekit_mql5" / "onnx_export.py").exists()),
    ("C35", "onnx_embed.py", lambda r: (r / "scripts" / "vibecodekit_mql5" / "onnx_embed.py").exists()),
    ("C36", "async_build.py", lambda r: (r / "scripts" / "vibecodekit_mql5" / "async_build.py").exists()),
    ("C37", "llm_context.py", lambda r: (r / "scripts" / "vibecodekit_mql5" / "llm_context.py").exists()),
    ("C38", "forge_init.py", lambda r: (r / "scripts" / "vibecodekit_mql5" / "forge_init.py").exists()),
    ("C39", "forge_pr.py", lambda r: (r / "scripts" / "vibecodekit_mql5" / "forge_pr.py").exists()),
    ("C40", "canary.py", lambda r: (r / "scripts" / "vibecodekit_mql5" / "canary.py").exists()),
    ("C41", "doctor.py", lambda r: (r / "scripts" / "vibecodekit_mql5" / "doctor.py").exists()),
    ("C42", "ship.py", lambda r: (r / "scripts" / "vibecodekit_mql5" / "ship.py").exists()),
    ("C43", "CI workflow", lambda r: (r / ".github" / "workflows" / "ci.yml").exists()),
    ("C44", "LICENSE file", lambda r: (r / "LICENSE").exists()),
    ("C45", "No forbidden files", lambda r: not any((r / f).exists() for f in ["scripts/vibecodekit_mql5/query_loop.py", "scripts/vibecodekit_mql5/tool_executor.py", "scripts/vibecodekit_mql5/intent_router.py"])),
    ("C46", "review/review.py", lambda r: (r / "scripts" / "vibecodekit_mql5" / "review" / "review.py").exists()),
    ("C47", "review/cso.py", lambda r: (r / "scripts" / "vibecodekit_mql5" / "review" / "cso.py").exists()),
    ("C48", "review/eng_review.py", lambda r: (r / "scripts" / "vibecodekit_mql5" / "review" / "eng_review.py").exists()),
    ("C49", "cloud_optimize.py", lambda r: (r / "scripts" / "vibecodekit_mql5" / "cloud_optimize.py").exists()),
    ("C50", "method_hiding_check.py", lambda r: (r / "scripts" / "vibecodekit_mql5" / "method_hiding_check.py").exists()),
]


def run_audit(root: Path) -> dict:
    results = []
    for cid, desc, check_fn in CONFORMANCE_CHECKS:
        try:
            passed = check_fn(root)
        except Exception:
            passed = False
        results.append({"id": cid, "description": desc, "pass": passed})

    total_pass = sum(1 for r in results if r["pass"])
    return {"total": len(results), "passed": total_pass, "failed": len(results) - total_pass, "checks": results}


def main() -> int:
    parser = argparse.ArgumentParser(description="Conformance audit")
    parser.add_argument("--path", type=Path, default=Path("."))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = run_audit(args.path.resolve())
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Audit: {result['passed']}/{result['total']} PASS")
        for r in result["checks"]:
            icon = "+" if r["pass"] else "X"
            print(f"  [{icon}] {r['id']}: {r['description']}")

    return 0 if result["failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
