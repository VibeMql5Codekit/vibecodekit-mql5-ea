#!/usr/bin/env python3
"""survey — Strategy taxonomy and preset survey.

Lists available scaffolds, categorizes by strategy type, and provides recommendations.
Usage: mql5-survey [--path .] [--json]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

STRATEGY_CATEGORIES = {
    "trend": ["trend", "ema-cross", "macd", "breakout"],
    "mean-reversion": ["grid", "martingale", "bollinger"],
    "scalping": ["scalping", "hft-async"],
    "portfolio": ["portfolio", "multi-ea"],
    "ml": ["ml-onnx", "embedded-onnx-llm"],
    "utility": ["wizard", "service-llm-bridge", "cloud-api", "self-hosted-ollama"],
}


def survey_presets(root: Path) -> dict:
    scaffolds_dir = root / "scaffolds"
    if not scaffolds_dir.exists():
        return {"success": False, "error": "scaffolds/ directory not found"}

    presets = []
    for preset_dir in sorted(scaffolds_dir.iterdir()):
        if not preset_dir.is_dir():
            continue
        stacks = [s.name for s in preset_dir.iterdir() if s.is_dir()]
        category = "other"
        for cat, keywords in STRATEGY_CATEGORIES.items():
            if preset_dir.name in keywords:
                category = cat
                break
        presets.append({"name": preset_dir.name, "stacks": stacks, "category": category})

    categories = {}
    for p in presets:
        cat = p["category"]
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(p["name"])

    return {"success": True, "total": len(presets), "presets": presets, "by_category": categories}


def main() -> int:
    parser = argparse.ArgumentParser(description="Strategy taxonomy survey")
    parser.add_argument("--path", type=Path, default=Path("."))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = survey_presets(args.path.resolve())
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result["success"]:
            print(f"Survey: {result['total']} presets")
            for cat, names in result["by_category"].items():
                print(f"  [{cat}] {', '.join(names)}")
        else:
            print(f"Error: {result['error']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
