#!/usr/bin/env python3
"""MFE/MAE analysis — per-trade max favorable/adverse excursion.

Usage:
    mql5-mfe-mae trades.csv
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path


def analyze_mfe_mae(csv_path: Path) -> dict:
    """Analyze MFE/MAE from CSV log."""
    if not csv_path.exists():
        return {"error": "file not found"}

    mfes, maes, profits = [], [], []
    with csv_path.open() as f:
        reader = csv.DictReader(f)
        for row in reader:
            mfe = float(row.get("MFE", 0))
            mae = float(row.get("MAE", 0))
            profit = float(row.get("Profit", 0))
            mfes.append(mfe)
            maes.append(mae)
            profits.append(profit)

    if not mfes:
        return {"trades": 0}

    n = len(mfes)
    avg_mfe = sum(mfes) / n
    avg_mae = sum(maes) / n
    edge_ratio = avg_mfe / abs(avg_mae) if avg_mae != 0 else 0

    return {
        "trades": n,
        "avg_mfe": round(avg_mfe, 2),
        "avg_mae": round(avg_mae, 2),
        "edge_ratio": round(edge_ratio, 3),
        "optimal_sl_hint": round(abs(avg_mae) * 1.2, 2),
        "optimal_tp_hint": round(avg_mfe * 0.8, 2),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="MFE/MAE analyzer")
    parser.add_argument("csv", type=Path, help="MFE/MAE CSV log")
    args = parser.parse_args()

    result = analyze_mfe_mae(args.csv)
    if "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        return 1

    print(f"Trades: {result['trades']}")
    print(f"Avg MFE: {result['avg_mfe']}")
    print(f"Avg MAE: {result['avg_mae']}")
    print(f"Edge ratio: {result['edge_ratio']}")
    print(f"Optimal SL hint: {result['optimal_sl_hint']}")
    print(f"Optimal TP hint: {result['optimal_tp_hint']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
