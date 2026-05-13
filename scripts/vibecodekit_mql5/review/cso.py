#!/usr/bin/env python3
"""cso — Chief Security Officer audit.

OWASP Top 10 (adapted for MQL5) + STRIDE + supply-chain checks.
Usage: mql5-cso --ea EA.mq5 [--json]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SECURITY_CHECKS = [
    ("S01", "DLL import (code injection risk)", r"#import\s+\".*\.dll\""),
    ("S02", "WebRequest in OnTick (data exfil)", r"OnTick.*WebRequest|WebRequest.*OnTick"),
    ("S03", "Raw file write (data leak)", r"FileOpen.*FILE_WRITE"),
    ("S04", "Hardcoded credentials", r"(?:password|api.?key|secret)\s*=\s*\""),
    ("S05", "Unsafe string format (buffer overflow)", r"StringFormat.*%s.*user"),
    ("S06", "No error check after trade", r"OrderSend\s*\([^;]*;\s*(?!.*ResultRetcode)"),
    ("S07", "Global variable leak", r"GlobalVariable(?:Set|Get)"),
    ("S08", "Timer abuse (resource exhaustion)", r"EventSetTimer\s*\(\s*[01]\s*\)"),
    ("S09", "Unsafe array access (no bounds check)", r"\[\s*\w+\s*\](?!.*ArraySize)"),
    ("S10", "Print sensitive data", r"Print.*(?:password|key|secret|token)"),
]


def run_cso_audit(path: Path) -> dict:
    if not path.exists():
        return {"file": str(path), "error": f"File not found: {path}"}
    content = path.read_text(encoding="utf-8", errors="replace")
    findings = []
    for sid, desc, pattern in SECURITY_CHECKS:
        matches = list(re.finditer(pattern, content, re.IGNORECASE | re.DOTALL))
        status = "FAIL" if matches else "PASS"
        finding = {"id": sid, "description": desc, "status": status, "occurrences": len(matches)}
        if matches:
            lines = []
            for m in matches[:3]:
                line_num = content[:m.start()].count("\n") + 1
                lines.append(line_num)
            finding["lines"] = lines
        findings.append(finding)

    failed = sum(1 for f in findings if f["status"] == "FAIL")
    return {"file": str(path), "checks": len(findings), "failed": failed, "findings": findings}


def main() -> int:
    parser = argparse.ArgumentParser(description="CSO security audit")
    parser.add_argument("--ea", type=Path, required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if not args.ea.exists():
        print(f"Error: {args.ea} not found")
        return 1

    result = run_cso_audit(args.ea)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"CSO Audit: {args.ea} ({result['checks']} checks, {result['failed']} FAIL)")
        for f in result["findings"]:
            icon = "X" if f["status"] == "FAIL" else "+"
            extra = f" (lines: {f.get('lines', [])})" if f["status"] == "FAIL" else ""
            print(f"  [{icon}] {f['id']}: {f['description']}{extra}")

    return 1 if result["failed"] > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
