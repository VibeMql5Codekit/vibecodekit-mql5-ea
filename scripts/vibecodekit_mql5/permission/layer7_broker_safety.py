#!/usr/bin/env python3
"""Permission Layer 7: broker_safety — broker compatibility gate."""
from __future__ import annotations

import re
from pathlib import Path


def check(ea_path: str, **kwargs: object) -> dict:
    """Check broker-safety patterns in EA source."""
    p = Path(ea_path)
    if not p.exists():
        return {"pass": False, "layer": 7, "name": "broker_safety",
                "details": f"File not found: {ea_path}"}

    content = p.read_text(encoding="utf-8", errors="replace")
    issues: list[str] = []

    if re.search(r"(?:0\.0001|0\.01)\s*[;*]", content):
        if not re.search(r"CPipNormalizer", content):
            issues.append("hardcoded pip without CPipNormalizer")

    if re.search(r"(?:\.Buy|\.Sell)\s*\(", content):
        if not re.search(r"(?:Spread|CSpreadGuard|ASK-BID)", content,
                         re.IGNORECASE):
            issues.append("no spread check before trade")

    if re.search(r"ACCOUNT_MARGIN_MODE", content) is None:
        if re.search(r"(?:\.Buy|\.Sell)\s*\(", content):
            issues.append("no margin mode check (netting vs hedging)")

    if re.search(r"\bSymbol\(\)\b", content):
        if not re.search(r"SymbolInfoInteger.*SYMBOL_DIGITS", content):
            issues.append("uses Symbol() without checking digits")

    return {"pass": len(issues) == 0, "layer": 7, "name": "broker_safety",
            "details": "; ".join(issues) if issues else "OK",
            "issues": issues}
