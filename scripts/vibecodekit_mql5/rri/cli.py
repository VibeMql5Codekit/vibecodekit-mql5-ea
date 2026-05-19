#!/usr/bin/env python3
"""RRI command-line entrypoint."""
from __future__ import annotations

import argparse
import json
import sys

from vibecodekit_mql5.rri.personas import PERSONA_NAMES, get_questions_for_mode, load_persona
from vibecodekit_mql5.rri.step_workflow import WorkflowEngine


def build_rri_session(mode: str = "TEAM", persona: str = "all") -> dict:
    names = PERSONA_NAMES if persona == "all" else [persona]
    interviews = []
    for name in names:
        data = load_persona(name)
        questions = get_questions_for_mode(data, mode)
        interviews.append({
            "persona": name,
            "role": data.get("role", ""),
            "questions": questions,
            "question_count": len(questions),
        })
    engine = WorkflowEngine(mode)
    return {
        "mode": mode,
        "interviews": interviews,
        "total_questions": sum(item["question_count"] for item in interviews),
        "workflow": engine.status(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Reverse Requirements Interview")
    parser.add_argument("--mode", choices=["PERSONAL", "TEAM", "ENTERPRISE"], default="TEAM")
    parser.add_argument("--persona", choices=["all", *PERSONA_NAMES], default="all")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = build_rri_session(args.mode, args.persona)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"RRI [{args.mode}]: {result['total_questions']} question(s)")
        for interview in result["interviews"]:
            print(f"  {interview['persona']}: {interview['question_count']} question(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
