#!/usr/bin/env python3
"""Multi-broker stability gate — compare metrics across brokers.

Usage:
    mql5-multibroker broker1.xml broker2.xml broker3.xml
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

from vibecodekit_mql5.backtest import parse_report


def stability_check(reports: list[Path],
                    pf_tolerance: float = 0.30,
                    sharpe_tolerance: float = 0.20,
                    dd_tolerance: float = 5.0) -> dict:
    """Compute cross-broker stability metrics."""
    metrics = [parse_report(r) for r in reports]
    pfs = [m.profit_factor for m in metrics]
    sharpes = [m.sharpe_ratio for m in metrics]
    dds = [m.max_drawdown_pct for m in metrics]
    brokers = [m.symbol for m in metrics]

    def stdev(vals: list[float]) -> float:
        if len(vals) < 2:
            return 0.0
        mean = sum(vals) / len(vals)
        var = sum((x - mean) ** 2 for x in vals) / (len(vals) - 1)
        return math.sqrt(var)

    def mean(vals: list[float]) -> float:
        return sum(vals) / len(vals) if vals else 0

    pf_mean = mean(pfs)
    pf_std = stdev(pfs)
    pf_cv = pf_std / pf_mean if pf_mean > 0 else 999
    sharpe_std = stdev(sharpes)
    dd_range = max(dds) - min(dds) if dds else 0

    result = {
        "brokers": brokers,
        "pf_values": [round(x, 3) for x in pfs],
        "pf_mean": round(pf_mean, 3),
        "pf_stdev": round(pf_std, 3),
        "pf_cv": round(pf_cv, 3),
        "pf_pass": pf_cv <= pf_tolerance,
        "sharpe_values": [round(x, 3) for x in sharpes],
        "sharpe_stdev": round(sharpe_std, 3),
        "sharpe_pass": sharpe_std <= sharpe_tolerance,
        "dd_values": [round(x, 2) for x in dds],
        "dd_range": round(dd_range, 2),
        "dd_pass": dd_range <= dd_tolerance,
        "overall_pass": pf_cv <= pf_tolerance and sharpe_std <= sharpe_tolerance and dd_range <= dd_tolerance,
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Multi-broker stability gate")
    parser.add_argument("reports", nargs="+", type=Path, help="XML reports")
    parser.add_argument("--pf-tol", type=float, default=0.30)
    parser.add_argument("--sharpe-tol", type=float, default=0.20)
    parser.add_argument("--dd-tol", type=float, default=5.0)
    args = parser.parse_args()

    result = stability_check(args.reports, args.pf_tol, args.sharpe_tol, args.dd_tol)

    print("Multi-broker stability:")
    for i, b in enumerate(result["brokers"]):
        print(f"  {b}: PF={result['pf_values'][i]}, "
              f"Sharpe={result['sharpe_values'][i]}, "
              f"DD={result['dd_values'][i]}%")
    print(f"\nPF CV: {result['pf_cv']:.3f} ({'PASS' if result['pf_pass'] else 'FAIL'})")
    print(f"Sharpe stdev: {result['sharpe_stdev']:.3f} ({'PASS' if result['sharpe_pass'] else 'FAIL'})")
    print(f"DD range: {result['dd_range']:.2f}% ({'PASS' if result['dd_pass'] else 'FAIL'})")
    status = "PASS" if result["overall_pass"] else "FAIL"
    print(f"\nOverall: {status}")

    return 0 if result["overall_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
