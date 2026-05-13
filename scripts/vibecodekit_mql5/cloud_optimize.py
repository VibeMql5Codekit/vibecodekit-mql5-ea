#!/usr/bin/env python3
"""cloud_optimize — Cloud Network optimization with cost gate.

Dispatches optimization to MQL5 Cloud Network with mode-based cost limits.
Usage: mql5-cloud-optimize --ea EA.mq5 --mode ENTERPRISE [--budget 100]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

MODE_POLICIES = {
    "PERSONAL": {"allowed": False, "reason": "Cloud Network costs real money. Use local optimization."},
    "TEAM": {"allowed": True, "max_budget_usd": 50, "max_agents": 64},
    "ENTERPRISE": {"allowed": True, "max_budget_usd": 500, "max_agents": 256},
}


def check_cost_gate(mode: str, budget: float) -> dict:
    policy = MODE_POLICIES.get(mode)
    if not policy:
        return {"allowed": False, "reason": f"Unknown mode: {mode}"}
    if not policy["allowed"]:
        return {"allowed": False, "reason": policy["reason"]}
    if budget < 0:
        return {"allowed": False, "reason": "Budget cannot be negative"}
    if budget > policy["max_budget_usd"]:
        return {
            "allowed": False,
            "reason": f"Budget ${budget} exceeds {mode} limit ${policy['max_budget_usd']}",
        }
    return {"allowed": True, "max_agents": policy["max_agents"], "budget": budget}


def generate_cloud_config(ea_path: Path, mode: str, budget: float,
                          symbol: str = "EURUSD", period: str = "H1") -> dict:
    gate = check_cost_gate(mode, budget)
    if not gate["allowed"]:
        return {"success": False, **gate}

    config = {
        "success": True,
        "ea": str(ea_path),
        "mode": mode,
        "symbol": symbol,
        "period": period,
        "cloud_agents": gate["max_agents"],
        "budget_usd": budget,
        "optimization_type": "genetic",
        "forward_mode": "half",
        "config_ini": (
            f"[Tester]\n"
            f"Expert={ea_path.stem}\n"
            f"Symbol={symbol}\n"
            f"Period={period}\n"
            f"Optimization=2\n"
            f"ForwardMode=1\n"
            f"UseCloud=1\n"
            f"CloudMaxAgents={gate['max_agents']}\n"
        ),
    }
    return config


def main() -> int:
    parser = argparse.ArgumentParser(description="Cloud Network optimization")
    parser.add_argument("--ea", type=Path, required=True)
    parser.add_argument("--mode", choices=list(MODE_POLICIES.keys()), default="TEAM")
    parser.add_argument("--budget", type=float, default=50.0, help="Max budget USD")
    parser.add_argument("--symbol", default="EURUSD")
    parser.add_argument("--period", default="H1")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = generate_cloud_config(args.ea, args.mode, args.budget, args.symbol, args.period)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result["success"]:
            print(f"Cloud Optimize: {args.ea} ({args.mode})")
            print(f"Agents: {result['cloud_agents']}, Budget: ${result['budget_usd']}")
            print(f"\n--- config.ini ---\n{result['config_ini']}")
        else:
            print(f"BLOCKED: {result['reason']}")

    return 0 if result.get("success") else 1


if __name__ == "__main__":
    sys.exit(main())
