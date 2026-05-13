#!/usr/bin/env python3
"""Fitness function templates for Strategy Tester optimization.

5 templates: max_profit, min_dd, sharpe_ratio, profit_factor, custom_weighted.

Usage:
    mql5-fitness --template sharpe_ratio --report report.xml
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from vibecodekit_mql5.backtest import parse_report


def fitness_max_profit(m) -> float:
    return m.net_profit


def fitness_min_dd(m) -> float:
    return -m.max_drawdown_pct


def fitness_sharpe(m) -> float:
    return m.sharpe_ratio


def fitness_pf(m) -> float:
    return m.profit_factor


def fitness_custom(m, w_pf: float = 0.3, w_sharpe: float = 0.3,
                   w_dd: float = 0.2, w_rf: float = 0.2) -> float:
    dd_score = max(0, 100 - m.max_drawdown_pct) / 100
    return (w_pf * m.profit_factor +
            w_sharpe * m.sharpe_ratio +
            w_dd * dd_score * 10 +
            w_rf * m.recovery_factor)


TEMPLATES = {
    "max_profit": fitness_max_profit,
    "min_dd": fitness_min_dd,
    "sharpe_ratio": fitness_sharpe,
    "profit_factor": fitness_pf,
    "custom_weighted": fitness_custom,
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Fitness function calculator")
    parser.add_argument("--template", choices=list(TEMPLATES.keys()), required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    m = parse_report(args.report)
    fn = TEMPLATES[args.template]
    score = fn(m)

    print(f"Template: {args.template}")
    print(f"Score: {score:.4f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
