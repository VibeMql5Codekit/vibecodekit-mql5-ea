#!/usr/bin/env python3
"""Permission Layer 5: methodology — RRI methodology gate."""
from __future__ import annotations

import re
from pathlib import Path


def check(ea_path: str, **kwargs: object) -> dict:
    """Check that EA follows methodology requirements."""
    p = Path(ea_path)
    if not p.exists():
        return {"pass": False, "layer": 5, "name": "methodology",
                "details": f"File not found: {ea_path}"}

    content = p.read_text(encoding="utf-8", errors="replace")
    issues: list[str] = []

    if not re.search(r'#include\s*[<"]CPipNormalizer', content):
        issues.append("missing CPipNormalizer include")
    if not re.search(r'#include\s*[<"]CRiskGuard', content):
        issues.append("missing CRiskGuard include")
    if not re.search(r'#include\s*[<"]CMagicRegistry', content):
        issues.append("missing CMagicRegistry include")
    if not re.search(r"\bOnDeinit\b", content):
        issues.append("missing OnDeinit handler")
    if not re.search(r"#property\s+version", content):
        issues.append("missing version property")

    return {"pass": len(issues) == 0, "layer": 5, "name": "methodology",
            "details": "; ".join(issues) if issues else "OK",
            "issues": issues}
