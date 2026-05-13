#!/usr/bin/env python3
"""Walk-forward analysis — IS/OOS split and metric comparison.

Forward 1/4 mode: 75% in-sample, 25% out-of-sample.

Usage:
    mql5-walkforward is_report.xml oos_report.xml
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from vibecodekit_mql5.backtest import parse_report


def walk_forward_check(is_path: Path, oos_path: Path,
                       min_oos_pf: float = 1.5) -> dict:
    """Compare IS vs OOS metrics. Return result dict."""
    for p, label in [(is_path, "IS"), (oos_path, "OOS")]:
        if not p.exists():
            return {"error": f"{label} report not found: {p}", "overall_pass": False}
    is_m = parse_report(is_path)
    oos_m = parse_report(oos_path)

    pf_ratio = oos_m.profit_factor / is_m.profit_factor if is_m.profit_factor > 0 else 0
    sharpe_ratio = oos_m.sharpe_ratio / is_m.sharpe_ratio if is_m.sharpe_ratio > 0 else 0
    dd_diff = abs(oos_m.max_drawdown_pct - is_m.max_drawdown_pct)

    result = {
        "is_pf": is_m.profit_factor,
        "oos_pf": oos_m.profit_factor,
        "pf_ratio": round(pf_ratio, 3),
        "is_sharpe": is_m.sharpe_ratio,
        "oos_sharpe": oos_m.sharpe_ratio,
        "sharpe_ratio": round(sharpe_ratio, 3),
        "is_dd": is_m.max_drawdown_pct,
        "oos_dd": oos_m.max_drawdown_pct,
        "dd_diff": round(dd_diff, 2),
        "oos_pf_pass": oos_m.profit_factor >= min_oos_pf,
        "pf_ratio_pass": pf_ratio >= 0.5,
        "overall_pass": oos_m.profit_factor >= min_oos_pf and pf_ratio >= 0.5,
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Walk-forward analysis")
    parser.add_argument("is_report", type=Path, help="In-sample XML report")
    parser.add_argument("oos_report", type=Path, help="Out-of-sample XML report")
    parser.add_argument("--min-pf", type=float, default=1.5)
    args = parser.parse_args()

    result = walk_forward_check(args.is_report, args.oos_report, args.min_pf)

    print(f"IS PF: {result['is_pf']:.2f}  |  OOS PF: {result['oos_pf']:.2f}")
    print(f"PF ratio (OOS/IS): {result['pf_ratio']:.3f}")
    print(f"IS Sharpe: {result['is_sharpe']:.2f}  |  OOS Sharpe: {result['oos_sharpe']:.2f}")
    print(f"DD diff: {result['dd_diff']:.2f}%")
    status = "PASS" if result["overall_pass"] else "FAIL"
    print(f"\nWalk-forward gate: {status}")

    return 0 if result["overall_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
