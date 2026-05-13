#!/usr/bin/env python3
"""review — 7-specialist adversarial code review.

Perspectives: architect, security, perf, a11y, ux, dx, risk.
Usage: mql5-review --ea EA.mq5 [--mode TEAM]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

PERSPECTIVES = [
    ("architect", ["#include", "class ", "namespace", "inheritance"]),
    ("security", ["WebRequest", "FileOpen", "DLL", "import", "#import"]),
    ("perf", ["ArrayResize", "OnTick", "for(", "while(", "Sleep("]),
    ("a11y", ["Alert(", "Print(", "Comment(", "ChartSetString"]),
    ("ux", ["input ", "extern ", "sinput ", "MessageBox"]),
    ("dx", ["//", "/*", "#property description", "#define"]),
    ("risk", ["OrderSend", "OrderSendAsync", "PositionClose", "AccountInfoDouble"]),
]


def review_file(path: Path, mode: str) -> dict:
    content = path.read_text(encoding="utf-8", errors="replace")
    loc = len(content.splitlines())
    findings: list[dict] = []

    for name, patterns in PERSPECTIVES:
        hits = []
        for pat in patterns:
            matches = [i + 1 for i, line in enumerate(content.splitlines()) if pat in line]
            if matches:
                hits.append({"pattern": pat, "lines": matches[:5]})
        severity = "info"
        if name == "security" and hits:
            severity = "warning"
        if name == "risk" and any(p["pattern"] == "OrderSend" for p in hits):
            if not any(p["pattern"] == "OrderSendAsync" for p in hits):
                severity = "warning"
        findings.append({"perspective": name, "hits": len(hits), "severity": severity, "details": hits})

    high = sum(1 for f in findings if f["severity"] == "warning")
    return {"file": str(path), "loc": loc, "mode": mode, "findings": findings, "warnings": high}


def main() -> int:
    parser = argparse.ArgumentParser(description="7-specialist code review")
    parser.add_argument("--ea", type=Path, required=True, help=".mq5 file")
    parser.add_argument("--mode", default="TEAM", choices=["PERSONAL", "TEAM", "ENTERPRISE"])
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    if not args.ea.exists():
        print(f"Error: {args.ea} not found")
        return 1

    result = review_file(args.ea, args.mode)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Review: {result['file']} ({result['loc']} LOC, mode={args.mode})")
        for f in result["findings"]:
            icon = "!" if f["severity"] == "warning" else "."
            print(f"  [{icon}] {f['perspective']}: {f['hits']} pattern(s) found")
        print(f"\nWarnings: {result['warnings']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
