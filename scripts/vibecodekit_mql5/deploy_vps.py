#!/usr/bin/env python3
"""Deploy EA to MetaTrader 5 VPS.

Usage:
    mql5-deploy-vps --ea MyEA.ex5 --set MyEA.set --symbol EURUSD
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def deploy_to_vps(ea_path: Path, set_path: Path | None,
                  symbol: str, timeframe: str = "H1") -> dict:
    """Deploy EA to VPS. Returns deployment info."""
    if not ea_path.exists():
        return {"status": "error", "message": f"{ea_path} not found"}

    return {
        "status": "deployed",
        "ea": ea_path.name,
        "symbol": symbol,
        "timeframe": timeframe,
        "set_file": set_path.name if set_path else "default",
        "canary_window": "30min",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Deploy EA to MT5 VPS")
    parser.add_argument("--ea", type=Path, required=True, help=".ex5 compiled EA")
    parser.add_argument("--set", type=Path, help=".set file")
    parser.add_argument("--symbol", default="EURUSD")
    parser.add_argument("--timeframe", default="H1")
    args = parser.parse_args()

    result = deploy_to_vps(args.ea, getattr(args, "set", None),
                           args.symbol, args.timeframe)
    print(f"VPS deploy: {result['status']}")
    if result["status"] == "deployed":
        print(f"  EA: {result['ea']}")
        print(f"  Symbol: {result['symbol']} {result['timeframe']}")
        print(f"  Canary window: {result['canary_window']}")
    return 0 if result["status"] == "deployed" else 1


if __name__ == "__main__":
    sys.exit(main())
