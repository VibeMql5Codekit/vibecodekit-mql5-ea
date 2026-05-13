#!/usr/bin/env python3
"""investigate — Root-cause debug with NO-FIX-WITHOUT-INVESTIGATION policy.

Analyzes EA source for common bug patterns and suggests root causes.
Usage: mql5-investigate --ea EA.mq5 --symptom "EA stops trading after 3 days"
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

BUG_PATTERNS = [
    ("mem_leak", "Potential memory leak", r"new\s+\w+.*(?!delete)"),
    ("array_oob", "Array out-of-bounds risk", r"\[\s*\w+\s*-\s*1\s*\]"),
    ("div_zero", "Division by zero risk", r"/\s*(?:\w+|0)(?:\s*;|\s*\))"),
    ("uninit_var", "Possibly uninitialized variable", r"double\s+\w+\s*;(?!\s*=)"),
    ("magic_collision", "Magic number not from registry", r"(?:MAGIC|magic)\s*=\s*\d+"),
    ("no_error_check", "Trade without error handling", r"trade\.\w+\(.*\);\s*\n(?!\s*if)"),
    ("timer_leak", "EventSetTimer without EventKillTimer", r"EventSetTimer"),
    ("infinite_loop", "Potential infinite loop", r"while\s*\(\s*(?:true|1)\s*\)"),
]

SYMPTOM_HINTS = {
    "stops trading": ["mem_leak", "timer_leak", "magic_collision"],
    "wrong lot": ["div_zero", "uninit_var"],
    "crash": ["array_oob", "mem_leak", "div_zero"],
    "no trades": ["magic_collision", "no_error_check"],
}


def investigate(path: Path, symptom: str = "") -> dict:
    content = path.read_text(encoding="utf-8", errors="replace")
    findings = []
    for pid, desc, pattern in BUG_PATTERNS:
        matches = list(re.finditer(pattern, content, re.IGNORECASE))
        if matches:
            lines = [content[:m.start()].count("\n") + 1 for m in matches[:5]]
            findings.append({"id": pid, "description": desc, "lines": lines})

    likely_causes = []
    if symptom:
        for key, pids in SYMPTOM_HINTS.items():
            if key in symptom.lower():
                for f in findings:
                    if f["id"] in pids:
                        likely_causes.append(f)

    return {
        "file": str(path), "symptom": symptom,
        "total_patterns": len(findings), "likely_causes": likely_causes,
        "all_findings": findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Root-cause investigation")
    parser.add_argument("--ea", type=Path, required=True)
    parser.add_argument("--symptom", default="", help="Describe the bug symptom")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if not args.ea.exists():
        print(f"Error: {args.ea} not found")
        return 1

    result = investigate(args.ea, args.symptom)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Investigation: {args.ea}")
        if args.symptom:
            print(f"Symptom: {args.symptom}")
        print(f"Patterns found: {result['total_patterns']}")
        if result["likely_causes"]:
            print("\nLikely root causes:")
            for c in result["likely_causes"]:
                print(f"  [!] {c['id']}: {c['description']} (lines: {c['lines']})")
        print("\nAll findings:")
        for f in result["all_findings"]:
            print(f"  {f['id']}: {f['description']} (lines: {f['lines'][:3]})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
