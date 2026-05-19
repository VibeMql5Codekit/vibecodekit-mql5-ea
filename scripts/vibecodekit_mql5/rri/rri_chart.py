#!/usr/bin/env python3
"""RRI chart and indicator questionnaire."""
from __future__ import annotations

import argparse
import json
import sys

from vibecodekit_mql5.rri.personas import PERSONA_NAMES, get_questions_for_mode, load_persona

CHART_KEYWORDS = (
    "chart", "indicator", "signal", "session", "time zone", "timeframe",
    "visual", "alert", "spread", "digits", "broker",
)


def build_chart_review(mode: str = "TEAM", persona: str = "all") -> dict:
    names = PERSONA_NAMES if persona == "all" else [persona]
    reviews = []
    for name in names:
        data = load_persona(name)
        questions = get_questions_for_mode(data, mode)
        focused = [
            question for question in questions
            if any(keyword in question["text"].lower() for keyword in CHART_KEYWORDS)
        ]
        reviews.append({
            "persona": name,
            "questions": focused or questions[:2],
            "total_mode_questions": len(questions),
        })
    total_questions = sum(len(item["questions"]) for item in reviews)
    return {"mode": mode, "reviews": reviews, "total_questions": total_questions}


def main() -> int:
    parser = argparse.ArgumentParser(description="RRI chart and indicator review")
    parser.add_argument("--mode", choices=["PERSONAL", "TEAM", "ENTERPRISE"], default="TEAM")
    parser.add_argument("--persona", choices=["all", *PERSONA_NAMES], default="all")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = build_chart_review(args.mode, args.persona)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"RRI Chart [{args.mode}]: {result['total_questions']} question(s)")
        for review in result["reviews"]:
            print(f"  {review['persona']}: {len(review['questions'])} focused question(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
