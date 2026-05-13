#!/usr/bin/env python3
"""refine — Classify diff against the refine envelope.

Categories: BUG_FIX, PERF, UX, DOCS, SCOPE_CREEP.
Usage: mql5-refine --diff changes.diff [--json]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

CATEGORIES = {
    "BUG_FIX": [r"fix", r"bug", r"error", r"crash", r"wrong", r"incorrect"],
    "PERF": [r"optimi[zs]e", r"faster", r"cache", r"reduce.*memory", r"speed"],
    "UX": [r"message", r"help", r"usage", r"print", r"error.*message", r"cli"],
    "DOCS": [r"readme", r"doc", r"comment", r"guide", r"\.md"],
    "SCOPE_CREEP": [r"new.*feature", r"add.*command", r"new.*module"],
}


def classify_diff(diff_text: str) -> dict:
    scores: dict[str, int] = {cat: 0 for cat in CATEGORIES}
    lines = diff_text.splitlines()
    changed_lines = [l for l in lines if l.startswith("+") or l.startswith("-")]

    for cat, patterns in CATEGORIES.items():
        for line in changed_lines:
            for pat in patterns:
                if re.search(pat, line, re.IGNORECASE):
                    scores[cat] += 1

    primary = max(scores, key=scores.get) if any(scores.values()) else "UNKNOWN"
    return {
        "primary_category": primary,
        "scores": scores,
        "total_changed_lines": len(changed_lines),
        "is_scope_creep": scores["SCOPE_CREEP"] > 5,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Diff classifier")
    parser.add_argument("--diff", type=Path, required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if not args.diff.exists():
        print(f"Error: {args.diff} not found")
        return 1

    diff_text = args.diff.read_text(encoding="utf-8", errors="replace")
    result = classify_diff(diff_text)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Refine: {result['primary_category']} ({result['total_changed_lines']} changed lines)")
        for cat, score in result["scores"].items():
            if score > 0:
                print(f"  {cat}: {score}")
        if result["is_scope_creep"]:
            print("  WARNING: Possible scope creep detected!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
