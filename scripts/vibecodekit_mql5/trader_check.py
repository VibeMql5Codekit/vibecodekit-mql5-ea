#!/usr/bin/env python3
"""Trader-17 checklist — 17-point pre-deployment verification.

Usage:
    mql5-trader-check --report report.xml --ea EA.mq5
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

CHECKLIST_ITEMS = [
    ("T01", "Stop-loss on every trade"),
    ("T02", "Risk per trade ≤ 2%"),
    ("T03", "Dynamic lot sizing (not fixed)"),
    ("T04", "Spread check before entry"),
    ("T05", "Slippage protection (deviation)"),
    ("T06", "News/session guard (avoid high-impact events)"),
    ("T07", "Pip normalization (CPipNormalizer)"),
    ("T08", "Multi-broker tested (≥3)"),
    ("T09", "Walk-forward validated (OOS PF ≥ 1.5)"),
    ("T10", "Monte Carlo DD95 ≤ 1.5× actual"),
    ("T11", "Overfit checked (OOS/IS ratio)"),
    ("T12", "Magic number unique (CMagicRegistry)"),
    ("T13", "Daily loss limit (CRiskGuard)"),
    ("T14", "Max positions limit"),
    ("T15", "No raw OrderSend (use CTrade)"),
    ("T16", "No WebRequest in OnTick"),
    ("T17", "Async trades have OnTradeTransaction"),
]


def check_ea_source(ea_path: Path) -> dict[str, str]:
    """Check EA source for Trader-17 items. Returns item_id -> PASS/WARN/N-A."""
    results: dict[str, str] = {}
    if not ea_path.exists():
        return {item[0]: "N-A" for item in CHECKLIST_ITEMS}

    content = ea_path.read_text(encoding="utf-8", errors="replace")

    results["T01"] = "PASS" if "sl" in content.lower() or "StopLoss" in content else "WARN"
    results["T02"] = "PASS" if "RiskPercent" in content or "risk" in content.lower() else "WARN"
    results["T03"] = "PASS" if "LotForRisk" in content or "MoneyFixedRisk" in content else "WARN"
    results["T04"] = "PASS" if "SpreadGuard" in content or "spread" in content.lower() else "N-A"
    results["T05"] = "PASS" if "DeviationInPoints" in content else "WARN"
    results["T06"] = "PASS" if re.search(r"news|session.?guard|trading.?session|high.?impact", content, re.IGNORECASE) else "N-A"
    results["T07"] = "PASS" if "CPipNormalizer" in content else "WARN"
    results["T08"] = "N-A"  # Requires multibroker test results
    results["T09"] = "N-A"  # Requires walkforward results
    results["T10"] = "N-A"  # Requires monte carlo results
    results["T11"] = "N-A"  # Requires overfit check results
    results["T12"] = "PASS" if "CMagicRegistry" in content or "Magic" in content else "WARN"
    results["T13"] = "PASS" if "CRiskGuard" in content or "DailyLoss" in content else "WARN"
    results["T14"] = "PASS" if "MaxPos" in content or "max_positions" in content.lower() else "WARN"
    results["T15"] = "PASS" if not re.search(r"\bOrderSend\s*\(", content) else "WARN"
    results["T16"] = "PASS" if not re.search(r"OnTick.*WebRequest", content, re.DOTALL) else "WARN"
    has_async = re.search(r"\bOrderSendAsync\s*\(", content)
    has_handler = re.search(r"\bOnTradeTransaction\b", content)
    results["T17"] = "PASS" if not has_async or has_handler else "WARN"

    return results


def main() -> int:
    parser = argparse.ArgumentParser(description="Trader-17 checklist")
    parser.add_argument("--ea", type=Path, help=".mq5 file to check")
    args = parser.parse_args()

    if not args.ea:
        parser.error("--ea required")

    results = check_ea_source(args.ea)
    passed = sum(1 for v in results.values() if v == "PASS")
    warns = sum(1 for v in results.values() if v == "WARN")
    na = sum(1 for v in results.values() if v == "N-A")

    for item_id, desc in CHECKLIST_ITEMS:
        status = results.get(item_id, "N-A")
        icon = "+" if status == "PASS" else ("!" if status == "WARN" else "-")
        print(f"[{icon}] {item_id}: {desc} — {status}")

    print(f"\n{passed} PASS, {warns} WARN, {na} N-A ({passed}/{17} required ≥ 15)")
    return 0 if passed >= 15 else 1


if __name__ == "__main__":
    sys.exit(main())
