#!/usr/bin/env python3
"""Permission Layer 1: source_lint — syntax + style checks."""
from __future__ import annotations

import re
from pathlib import Path


def check(ea_path: str, **kwargs: object) -> dict:
    """Check MQL5 source for basic syntax/style issues."""
    p = Path(ea_path)
    if not p.exists():
        return {"pass": False, "layer": 1, "name": "source_lint",
                "details": f"File not found: {ea_path}"}

    content = p.read_text(encoding="utf-8", errors="replace")
    issues: list[str] = []

    if not re.search(r"#property\s+strict", content):
        issues.append("missing #property strict")
    if not re.search(r"#property\s+copyright", content):
        issues.append("missing #property copyright")
    if len(content.splitlines()) > 1500:
        issues.append(f"file too long ({len(content.splitlines())} lines)")
    tabs = sum(1 for ln in content.splitlines() if "\t" in ln)
    spaces = sum(1 for ln in content.splitlines() if ln.startswith("    "))
    if tabs > 0 and spaces > 0:
        issues.append("mixed tabs and spaces")

    return {"pass": len(issues) == 0, "layer": 1, "name": "source_lint",
            "details": "; ".join(issues) if issues else "OK"}
