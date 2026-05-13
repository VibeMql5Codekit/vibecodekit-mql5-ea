#!/usr/bin/env python3
"""vision — Define goals, KPIs, and non-goals for an EA project.

Usage: mql5-vision --name "Gold Scalper" --goal "Scalp XAUUSD" [--json]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

VISION_TEMPLATE = """# Vision: {name}

## Goal
{goal}

## KPIs
1. Profit Factor >= {pf_target}
2. Max Drawdown <= {dd_target}%
3. Sharpe Ratio >= {sharpe_target}

## Non-goals
- Real-money trading without manual approval
- Multi-asset portfolio management (Phase 1)
- High-frequency market making

## Stack
MQL5 + CPipNormalizer + CRiskGuard + vibecodekit-mql5-ea pipeline

## Timeline
{timeline}
"""


def generate_vision(name: str, goal: str, pf: float = 1.5,
                    dd: float = 20, sharpe: float = 1.0,
                    timeline: str = "4 weeks") -> dict:
    content = VISION_TEMPLATE.format(
        name=name, goal=goal, pf_target=pf,
        dd_target=dd, sharpe_target=sharpe, timeline=timeline,
    )
    return {"name": name, "goal": goal, "kpis": {"pf": pf, "dd": dd, "sharpe": sharpe},
            "timeline": timeline, "content": content}


def main() -> int:
    parser = argparse.ArgumentParser(description="Vision generator")
    parser.add_argument("--name", required=True)
    parser.add_argument("--goal", required=True)
    parser.add_argument("--pf", type=float, default=1.5)
    parser.add_argument("--dd", type=float, default=20)
    parser.add_argument("--sharpe", type=float, default=1.0)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = generate_vision(args.name, args.goal, args.pf, args.dd, args.sharpe)
    if args.json:
        print(json.dumps({k: v for k, v in result.items() if k != "content"}, indent=2))
    else:
        print(result["content"])
    if args.output:
        args.output.write_text(result["content"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
