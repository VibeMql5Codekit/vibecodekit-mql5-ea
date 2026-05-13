#!/usr/bin/env python3
"""8×8 quality matrix — 8 dimensions × 8 stress axes = 64 cells.

Usage:
    mql5-matrix --ea EA.mq5 --report report.xml --mode ENTERPRISE
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

DIMENSIONS = [
    "correctness", "robustness", "performance", "security",
    "maintainability", "portability", "usability", "compliance",
]

AXES = [
    "normal_market", "high_volatility", "low_liquidity", "news_event",
    "broker_switch", "timeframe_switch", "multi_symbol", "stress_test",
]

MODE_THRESHOLDS = {
    "PERSONAL": 32,
    "TEAM": 48,
    "ENTERPRISE": 56,
}


def evaluate_matrix(results: dict[tuple[str, str], str] | None = None,
                    mode: str = "TEAM") -> dict:
    """Evaluate 64-cell matrix. Returns summary."""
    if results is None:
        results = {}

    cells = {}
    for dim in DIMENSIONS:
        for axis in AXES:
            key = (dim, axis)
            cells[key] = results.get(key, "N-A")

    passed = sum(1 for v in cells.values() if v == "PASS")
    failed = sum(1 for v in cells.values() if v == "FAIL")
    na = sum(1 for v in cells.values() if v == "N-A")
    threshold = MODE_THRESHOLDS.get(mode, 48)

    return {
        "total_cells": 64,
        "passed": passed,
        "failed": failed,
        "na": na,
        "threshold": threshold,
        "gate_pass": passed >= threshold,
        "cells": {f"{k[0]}_{k[1]}": v for k, v in cells.items()},
    }


def render_html(result: dict) -> str:
    """Render matrix as HTML table."""
    html = ["<table border='1'><tr><th></th>"]
    for axis in AXES:
        html.append(f"<th>{axis}</th>")
    html.append("</tr>")

    for dim in DIMENSIONS:
        html.append(f"<tr><td><b>{dim}</b></td>")
        for axis in AXES:
            key = f"{dim}_{axis}"
            val = result["cells"].get(key, "N-A")
            color = {"PASS": "#90EE90", "FAIL": "#FFB6C1"}.get(val, "#E0E0E0")
            html.append(f"<td style='background:{color}'>{val}</td>")
        html.append("</tr>")

    html.append("</table>")
    return "\n".join(html)


def main() -> int:
    parser = argparse.ArgumentParser(description="8×8 quality matrix")
    parser.add_argument("--mode", choices=list(MODE_THRESHOLDS.keys()), default="TEAM")
    parser.add_argument("--html", type=Path, help="Output HTML file")
    args = parser.parse_args()

    result = evaluate_matrix(mode=args.mode)
    print(f"Matrix: {result['passed']}/{result['total_cells']} PASS "
          f"(threshold: {result['threshold']}, gate: {'PASS' if result['gate_pass'] else 'FAIL'})")

    if args.html:
        html = render_html(result)
        args.html.write_text(html)
        print(f"HTML report: {args.html}")

    return 0 if result["gate_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
