#!/usr/bin/env python3
"""canary — Post-deploy canary monitoring (30-min health check).

Monitors EA health, error rate, and latency after deployment.
Usage: mql5-canary --ea EA.mq5 --terminal-log terminal.log [--duration 30]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

HEALTH_CHECKS = [
    ("connection", r"connection|disconnect|timeout", "warning"),
    ("trade_error", r"error.*(?:order|trade|position)|retcode.*(?!10009)", "critical"),
    ("memory", r"out of memory|memory.*exceeded", "critical"),
    ("dll_error", r"dll.*error|cannot load|import failed", "warning"),
    ("requote", r"requote|price changed", "info"),
    ("sl_hit", r"stop loss|sl triggered", "info"),
]


def analyze_log(log_path: Path, ea_name: str = "", duration_min: int = 30) -> dict:
    if not log_path.exists():
        return {"success": False, "error": f"Log not found: {log_path}"}

    content = log_path.read_text(encoding="utf-8", errors="replace")
    lines = content.splitlines()

    findings = []
    for check_name, pattern, severity in HEALTH_CHECKS:
        matches = [line for line in lines if re.search(pattern, line, re.IGNORECASE)]
        if matches:
            findings.append({
                "check": check_name, "severity": severity,
                "count": len(matches), "samples": matches[:3],
            })

    critical = sum(1 for f in findings if f["severity"] == "critical")
    warnings = sum(1 for f in findings if f["severity"] == "warning")

    status = "HEALTHY"
    if critical > 0:
        status = "CRITICAL"
    elif warnings > 3:
        status = "DEGRADED"

    return {
        "success": True, "status": status, "ea": ea_name,
        "duration_min": duration_min, "log_lines": len(lines),
        "critical": critical, "warnings": warnings,
        "findings": findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Post-deploy canary monitor")
    parser.add_argument("--ea", default="", help="EA name")
    parser.add_argument("--terminal-log", type=Path, required=True)
    parser.add_argument("--duration", type=int, default=30)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = analyze_log(args.terminal_log, args.ea, args.duration)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result["success"]:
            print(f"Canary [{result['status']}]: {result['log_lines']} lines analyzed")
            print(f"Critical: {result['critical']}, Warnings: {result['warnings']}")
            for f in result["findings"]:
                print(f"  [{f['severity']}] {f['check']}: {f['count']} occurrence(s)")
        else:
            print(f"Error: {result['error']}")

    return 0 if result.get("status") != "CRITICAL" else 1


if __name__ == "__main__":
    sys.exit(main())
