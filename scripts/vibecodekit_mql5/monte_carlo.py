#!/usr/bin/env python3
"""Monte Carlo simulation — bootstrap trade sequences for DD percentiles.

Usage:
    mql5-monte-carlo report.xml --runs 1000
"""
from __future__ import annotations

import argparse
import random
import sys
import xml.etree.ElementTree as ET
from pathlib import Path


def extract_trade_pnls(report_path: Path) -> list[float]:
    """Extract individual trade P&L from XML report."""
    tree = ET.parse(report_path)
    root = tree.getroot()
    pnls = []
    for trade in root.iter("Trade"):
        pnl_el = trade.find("Profit")
        if pnl_el is not None and pnl_el.text:
            pnls.append(float(pnl_el.text))
    if not pnls:
        net = root.find(".//NetProfit")
        trades_n = root.find(".//TotalTrades")
        if net is not None and trades_n is not None:
            n = int(float(trades_n.text)) if trades_n.text else 10
            avg = float(net.text) / n if net.text and n > 0 else 0
            pnls = [avg] * n
    return pnls


def monte_carlo_dd(pnls: list[float], runs: int = 1000,
                   initial_balance: float = 10000.0) -> dict:
    """Bootstrap trade sequence N times. Return DD percentiles."""
    if not pnls:
        return {"dd_50": 0, "dd_75": 0, "dd_95": 0, "runs": 0}

    max_dds = []
    for _ in range(runs):
        shuffled = random.sample(pnls, len(pnls))
        equity = initial_balance
        peak = equity
        max_dd = 0.0
        for pnl in shuffled:
            equity += pnl
            if equity > peak:
                peak = equity
            dd_pct = ((peak - equity) / peak) * 100 if peak > 0 else 0
            max_dd = max(max_dd, dd_pct)
        max_dds.append(max_dd)

    max_dds.sort()
    n = len(max_dds)

    return {
        "dd_50": round(max_dds[int(n * 0.50)], 2),
        "dd_75": round(max_dds[int(n * 0.75)], 2),
        "dd_95": round(max_dds[min(int(n * 0.95), n - 1)], 2),
        "runs": runs,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Monte Carlo DD simulation")
    parser.add_argument("report", type=Path, help="XML report with trade data")
    parser.add_argument("--runs", type=int, default=1000)
    parser.add_argument("--balance", type=float, default=10000.0)
    args = parser.parse_args()

    pnls = extract_trade_pnls(args.report)
    if not pnls:
        print("No trade data found in report", file=sys.stderr)
        return 1

    result = monte_carlo_dd(pnls, args.runs, args.balance)
    print(f"Monte Carlo ({result['runs']} runs, {len(pnls)} trades):")
    print(f"  DD 50th percentile: {result['dd_50']:.2f}%")
    print(f"  DD 75th percentile: {result['dd_75']:.2f}%")
    print(f"  DD 95th percentile: {result['dd_95']:.2f}%")
    return 0


if __name__ == "__main__":
    sys.exit(main())
