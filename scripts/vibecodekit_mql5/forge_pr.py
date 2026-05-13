#!/usr/bin/env python3
"""Algo Forge — evaluate and rank strategy parameter sets.

Reads forge workspace config, applies fitness function to backtest
results, and ranks candidates for next iteration.

Usage:
    mql5-forge-pr --workspace .forge/MyEA/ --results backtest.xml
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def evaluate_fitness(metrics: dict, fitness_cfg: dict) -> float:
    """Calculate composite fitness score from backtest metrics."""
    primary = fitness_cfg.get("primary", "profit_factor")
    secondary = fitness_cfg.get("secondary", "sharpe_ratio")
    constraints = fitness_cfg.get("constraints", {})

    pf = metrics.get(primary, 0)
    sr = metrics.get(secondary, 0)

    max_dd = constraints.get("max_drawdown_pct", 100)
    min_trades = constraints.get("min_trades", 0)

    dd = metrics.get("max_drawdown_pct",
                     metrics.get("maximal_drawdown_pct", 100))
    if dd > max_dd:
        return -1.0
    if metrics.get("total_trades", 0) < min_trades:
        return -1.0

    return round(0.6 * pf + 0.4 * sr, 4)


def rank_candidates(workspace: Path, results_dir: Path) -> list[dict]:
    """Load backtest results, score, and rank."""
    config_path = workspace / "forge-config.json"
    if not config_path.exists():
        return []

    config = json.loads(config_path.read_text())
    fitness_cfg = config.get("fitness", {})

    candidates: list[dict] = []
    for f in sorted(results_dir.glob("*.json")):
        metrics = json.loads(f.read_text())
        score = evaluate_fitness(metrics, fitness_cfg)
        candidates.append({"file": f.name, "metrics": metrics,
                           "fitness": score})

    candidates.sort(key=lambda c: c["fitness"], reverse=True)

    for i, c in enumerate(candidates):
        c["rank"] = i + 1

    return candidates


def main() -> int:
    ap = argparse.ArgumentParser(description="Algo Forge evaluate")
    ap.add_argument("--workspace", type=Path, default=Path(".forge/default"))
    ap.add_argument("--results", type=Path, default=None)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    results_dir = args.results or (args.workspace / "results")
    candidates = rank_candidates(args.workspace, results_dir)

    if args.json:
        print(json.dumps(candidates, indent=2))
    else:
        if not candidates:
            print("No results found. Run backtests first.")
        else:
            for c in candidates[:10]:
                print(f"#{c['rank']} {c['file']}: fitness={c['fitness']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
