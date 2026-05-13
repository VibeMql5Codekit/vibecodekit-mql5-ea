#!/usr/bin/env python3
"""second_opinion — Get a second review from alternative analysis.

Generates structured prompts for external LLM review of EA code.
Usage: mql5-second-opinion --ea EA.mq5 [--focus risk] [--json]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

FOCUS_PROMPTS = {
    "risk": "Analyze this MQL5 EA for risk management issues. Check: stop-loss placement, position sizing, drawdown limits, margin usage, and correlation risk.",
    "performance": "Analyze this MQL5 EA for performance issues. Check: OnTick efficiency, array operations, indicator calculations, memory management.",
    "security": "Analyze this MQL5 EA for security issues. Check: DLL imports, WebRequest usage, file operations, credential handling, data exfiltration risks.",
    "logic": "Analyze this MQL5 EA for logical errors. Check: entry/exit conditions, signal conflicts, state management, edge cases (weekends, gaps, holidays).",
    "general": "Provide a comprehensive code review of this MQL5 EA. Cover: correctness, risk management, performance, maintainability, and broker compatibility.",
}


def generate_prompt(ea_path: Path, focus: str = "general") -> dict:
    if not ea_path.exists():
        return {"success": False, "error": f"EA not found: {ea_path}"}

    content = ea_path.read_text(encoding="utf-8", errors="replace")
    loc = len(content.splitlines())
    prompt_text = FOCUS_PROMPTS.get(focus, FOCUS_PROMPTS["general"])

    full_prompt = f"""{prompt_text}

```mql5
{content}
```

Please provide:
1. Critical issues (must fix before production)
2. Warnings (should fix)
3. Suggestions (nice to have)
4. Overall assessment (PASS/CONDITIONAL/FAIL)
"""

    return {
        "success": True, "ea": str(ea_path), "loc": loc, "focus": focus,
        "prompt_length": len(full_prompt), "prompt": full_prompt,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Second opinion prompt generator")
    parser.add_argument("--ea", type=Path, required=True)
    parser.add_argument("--focus", choices=list(FOCUS_PROMPTS.keys()), default="general")
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = generate_prompt(args.ea, args.focus)
    if args.json:
        print(json.dumps({k: v for k, v in result.items() if k != "prompt"}, indent=2))
    else:
        if result["success"]:
            print(f"Second Opinion [{args.focus}]: {args.ea} ({result['loc']} LOC)")
            print(f"Prompt length: {result['prompt_length']} chars")
            if args.output:
                args.output.write_text(result["prompt"])
                print(f"Saved to: {args.output}")
            else:
                print("\n--- Prompt (copy to external LLM) ---")
                print(result["prompt"][:500] + "..." if len(result["prompt"]) > 500 else result["prompt"])
        else:
            print(f"Error: {result['error']}")

    return 0 if result["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
