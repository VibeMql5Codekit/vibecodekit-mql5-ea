#!/usr/bin/env python3
"""Permission Layer 3: ap_lint — anti-pattern detection gate."""
from __future__ import annotations

from pathlib import Path


def check(ea_path: str, **kwargs: object) -> dict:
    """Run anti-pattern lint. Fail on any CRITICAL finding."""
    from vibecodekit_mql5.lint import lint_file

    p = Path(ea_path)
    if not p.exists():
        return {"pass": False, "layer": 3, "name": "ap_lint",
                "details": f"File not found: {ea_path}"}

    findings = lint_file(p)
    criticals = [f for f in findings if f.severity == "CRITICAL"]
    warnings = [f for f in findings if f.severity == "WARNING"]

    if criticals:
        detail = "; ".join(f"{f.ap_id}@L{f.line}" for f in criticals[:5])
        return {"pass": False, "layer": 3, "name": "ap_lint",
                "details": f"{len(criticals)} critical: {detail}",
                "criticals": len(criticals), "warnings": len(warnings)}

    return {"pass": True, "layer": 3, "name": "ap_lint",
            "details": f"0 critical, {len(warnings)} warnings",
            "criticals": 0, "warnings": len(warnings)}
