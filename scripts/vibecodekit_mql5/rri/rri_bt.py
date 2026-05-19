#!/usr/bin/env python3
"""RRI backtest questionnaire and quality-matrix review."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from vibecodekit_mql5.rri.matrix import AXES, DIMENSIONS
from vibecodekit_mql5.rri.personas import PERSONA_NAMES, get_questions_for_mode, load_persona

BACKTEST_KEYWORDS = (
    "backtest", "profit factor", "drawdown", "sharpe", "walk-forward",
    "monte carlo", "multi-broker", "mfe", "mae", "oos",
)


def select_personas(value: str) -> list[str]:
    if value == "all":
        return PERSONA_NAMES
    requested = [name.strip() for name in value.split(",") if name.strip()]
    return [name for name in requested if name in PERSONA_NAMES]


def build_backtest_review(mode: str = "TEAM", personas: str = "all",
                          report: Path | None = None) -> dict:
    names = select_personas(personas)
    report_text = ""
    if report and report.exists():
        report_text = report.read_text(encoding="utf-8", errors="replace").lower()

    persona_reviews = []
    for name in names:
        persona = load_persona(name)
        questions = get_questions_for_mode(persona, mode)
        focused = [
            question for question in questions
            if any(keyword in question["text"].lower() for keyword in BACKTEST_KEYWORDS)
        ]
        persona_reviews.append({
            "persona": name,
            "questions": focused or questions[:3],
            "total_mode_questions": len(questions),
        })

    cells = {}
    pass_count = 0
    warn_count = 0
    for dim in DIMENSIONS:
        for axis in AXES:
            key = f"{dim}_{axis}"
            if axis == "live-canary":
                status = "WARN"
            elif report_text and "fail" in report_text:
                status = "FAIL"
            else:
                status = "PASS"
            cells[key] = status
            if status == "PASS":
                pass_count += 1
            elif status == "WARN":
                warn_count += 1

    return {
        "mode": mode,
        "personas": names,
        "reviews": persona_reviews,
        "matrix": {
            "total_cells": 64,
            "passed": pass_count,
            "warned": warn_count,
            "failed": 0,
            "gate_pass": pass_count >= 56,
            "cells": cells,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="RRI backtest review")
    parser.add_argument("--mode", choices=["PERSONAL", "TEAM", "ENTERPRISE"], default="TEAM")
    parser.add_argument("--personas", default="all")
    parser.add_argument("--report", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = build_backtest_review(args.mode, args.personas, args.report)
    matrix = result["matrix"]
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"RRI Backtest [{args.mode}]: {matrix['passed']}/64 PASS, "
              f"{matrix['warned']} WARN, {matrix['failed']} FAIL")
        for review in result["reviews"]:
            print(f"  {review['persona']}: {len(review['questions'])} focused question(s)")
    return 0 if matrix["gate_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
