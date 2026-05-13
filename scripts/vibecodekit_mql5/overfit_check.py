#!/usr/bin/env python3
"""Overfit detection — check IS vs OOS PF ratio and parameter count.

Usage:
    mql5-overfit-check is_report.xml oos_report.xml --inputs 8
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from vibecodekit_mql5.backtest import parse_report


def overfit_check(is_path: Path, oos_path: Path,
                  input_count: int = 0) -> dict:
    """Check for overfitting indicators."""
    is_m = parse_report(is_path)
    oos_m = parse_report(oos_path)

    pf_ratio = oos_m.profit_factor / is_m.profit_factor if is_m.profit_factor > 0 else 0
    pf_drop = 1.0 - pf_ratio

    result = {
        "is_pf": is_m.profit_factor,
        "oos_pf": oos_m.profit_factor,
        "pf_ratio": round(pf_ratio, 3),
        "pf_drop_pct": round(pf_drop * 100, 1),
        "input_count": input_count,
        "excessive_inputs": input_count > 6,
        "severe_overfit": pf_ratio < 0.5,
        "moderate_overfit": 0.5 <= pf_ratio < 0.7,
        "healthy": pf_ratio >= 0.7,
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Overfit check")
    parser.add_argument("is_report", type=Path)
    parser.add_argument("oos_report", type=Path)
    parser.add_argument("--inputs", type=int, default=0)
    args = parser.parse_args()

    result = overfit_check(args.is_report, args.oos_report, args.inputs)

    print(f"PF ratio (OOS/IS): {result['pf_ratio']:.3f}")
    print(f"PF drop: {result['pf_drop_pct']:.1f}%")
    if result["excessive_inputs"]:
        print(f"WARNING: {result['input_count']} inputs (AP-5: max 6)")
    if result["severe_overfit"]:
        print("SEVERE OVERFIT: PF ratio < 0.5")
        return 1
    if result["moderate_overfit"]:
        print("MODERATE OVERFIT: PF ratio 0.5-0.7")
    if result["healthy"]:
        print("HEALTHY: PF ratio >= 0.7")
    return 0


if __name__ == "__main__":
    sys.exit(main())
