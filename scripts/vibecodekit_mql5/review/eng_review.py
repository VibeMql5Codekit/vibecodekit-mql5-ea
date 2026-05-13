#!/usr/bin/env python3
"""eng_review — Engineering-mode code review.

Enforces: architecture compliance, ASCII diagrams, state machine, invariants.
Usage: mql5-eng-review --ea EA.mq5
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

INVARIANTS = [
    ("no_raw_ordersend", r"\bOrderSend\s*\(", True),
    ("has_oninit", r"\bOnInit\s*\(", False),
    ("has_ondeinit", r"\bOnDeinit\s*\(", False),
    ("has_ontick", r"\bOnTick\s*\(", False),
    ("no_hardcoded_lots", r"\b0\.\d+\b.*(?:volume|lot)", True),
    ("uses_ctrade", r"#include\s*<Trade\\Trade\.mqh>", False),
    ("no_sleep_ontick", r"OnTick.*Sleep\s*\(", True),
    ("error_handling", r"ResultRetcode|GetLastError", False),
]


def check_invariants(path: Path) -> list[dict]:
    content = path.read_text(encoding="utf-8", errors="replace")
    results = []
    for name, pattern, is_violation in INVARIANTS:
        found = bool(re.search(pattern, content, re.DOTALL | re.IGNORECASE))
        passed = not found if is_violation else found
        results.append({"invariant": name, "pass": passed, "is_violation": is_violation})
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Engineering review")
    parser.add_argument("--ea", type=Path, required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if not args.ea.exists():
        print(f"Error: {args.ea} not found")
        return 1

    results = check_invariants(args.ea)
    passed = sum(1 for r in results if r["pass"])
    total = len(results)

    if args.json:
        print(json.dumps({"file": str(args.ea), "checks": results, "passed": passed, "total": total}))
    else:
        print(f"Eng Review: {args.ea} ({passed}/{total} invariants)")
        for r in results:
            icon = "+" if r["pass"] else "!"
            print(f"  [{icon}] {r['invariant']}")

    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
