#!/usr/bin/env python3
"""Broker safety layer — Layer 7 standalone check.

Verifies pip normalization + multi-broker stability for a given EA.

Usage:
    mql5-broker-safety --ea EA.mq5 --reports r1.xml r2.xml r3.xml
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from vibecodekit_mql5.multibroker import stability_check


def check_pip_normalizer_usage(ea_path: Path) -> bool:
    """Check if EA uses CPipNormalizer."""
    if not ea_path.exists():
        return False
    content = ea_path.read_text(encoding="utf-8", errors="replace")
    return "CPipNormalizer" in content


def broker_safety_gate(ea_path: Path, reports: list[Path]) -> dict:
    """Run Layer 7 broker safety gate."""
    has_pipnorm = check_pip_normalizer_usage(ea_path)
    stability = stability_check(reports) if len(reports) >= 2 else None

    result = {
        "pip_normalizer": has_pipnorm,
        "stability": stability,
        "pass": has_pipnorm and (stability is None or stability["overall_pass"]),
    }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Broker safety gate (Layer 7)")
    parser.add_argument("--ea", type=Path, required=True)
    parser.add_argument("--reports", nargs="*", type=Path, default=[])
    args = parser.parse_args()

    result = broker_safety_gate(args.ea, args.reports)

    print(f"PipNormalizer: {'PASS' if result['pip_normalizer'] else 'FAIL'}")
    if result["stability"]:
        print(f"Stability: {'PASS' if result['stability']['overall_pass'] else 'FAIL'}")
    status = "PASS" if result["pass"] else "FAIL"
    print(f"Layer 7 gate: {status}")
    return 0 if result["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
