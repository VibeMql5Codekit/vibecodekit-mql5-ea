#!/usr/bin/env python3
"""ceo_review — CEO-mode review with 4 modes.

Modes: SCOPE_EXPANSION | SELECTIVE | HOLD | REDUCTION
Usage: mql5-ceo-review --ea EA.mq5 --mode HOLD
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

CEO_MODES = ["SCOPE_EXPANSION", "SELECTIVE", "HOLD", "REDUCTION"]

CHECKS = {
    "scope_alignment": "Does the EA stay within its stated scope?",
    "roi_justified": "Is the complexity justified by expected returns?",
    "maintainability": "Can a new developer maintain this in 6 months?",
    "risk_exposure": "Is the max drawdown within acceptable bounds?",
    "competitive_moat": "Does this EA have a defensible edge?",
    "resource_efficiency": "Are compute/memory resources used efficiently?",
}


def ceo_review(path: Path, mode: str) -> dict:
    content = path.read_text(encoding="utf-8", errors="replace")
    loc = len(content.splitlines())
    input_count = len(re.findall(r"(?m)^\s*input\s+", content))
    has_risk = bool(re.search(r"CRiskGuard|DailyLoss|MaxPos", content))
    has_pip = "CPipNormalizer" in content

    findings = []
    if mode == "REDUCTION":
        if loc > 300:
            findings.append({"check": "loc_reduction", "action": "Consider splitting into modules", "severity": "high"})
        if input_count > 6:
            findings.append({"check": "input_reduction", "action": f"Reduce inputs from {input_count} to ≤ 6", "severity": "high"})
    elif mode == "HOLD":
        if not has_risk:
            findings.append({"check": "risk_missing", "action": "Add CRiskGuard before production", "severity": "medium"})
    elif mode == "SCOPE_EXPANSION":
        if not has_pip:
            findings.append({"check": "broker_support", "action": "Add CPipNormalizer for multi-broker", "severity": "medium"})

    return {
        "file": str(path), "mode": mode, "loc": loc, "inputs": input_count,
        "has_risk_guard": has_risk, "has_pip_normalizer": has_pip,
        "findings": findings, "recommendation": mode,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="CEO-mode review")
    parser.add_argument("--ea", type=Path, required=True)
    parser.add_argument("--mode", choices=CEO_MODES, default="HOLD")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if not args.ea.exists():
        print(f"Error: {args.ea} not found")
        return 1

    result = ceo_review(args.ea, args.mode)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"CEO Review [{args.mode}]: {args.ea} ({result['loc']} LOC, {result['inputs']} inputs)")
        for f in result["findings"]:
            print(f"  [{f['severity']}] {f['check']}: {f['action']}")
        if not result["findings"]:
            print("  No issues found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
