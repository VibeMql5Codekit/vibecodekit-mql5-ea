#!/usr/bin/env python3
"""Permission Layer 4: checklist — Trader-17 pre-deploy gate."""
from __future__ import annotations

from pathlib import Path


def check(ea_path: str, **kwargs: object) -> dict:
    """Run Trader-17 checklist. Require ≥ 15/17 PASS."""
    from vibecodekit_mql5.trader_check import check_ea_source

    p = Path(ea_path)
    if not p.exists():
        return {"pass": False, "layer": 4, "name": "checklist",
                "details": f"File not found: {ea_path}"}

    results = check_ea_source(p)
    passed = sum(1 for v in results.values() if v == "PASS")
    warns = sum(1 for v in results.values() if v == "WARN")

    ok = passed >= 15
    return {"pass": ok, "layer": 4, "name": "checklist",
            "details": f"Trader-17: {passed}/17 PASS, {warns} WARN",
            "passed": passed, "warns": warns}
