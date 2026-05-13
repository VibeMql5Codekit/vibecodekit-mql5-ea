#!/usr/bin/env python3
"""Permission Layer 1: source_lint."""
from __future__ import annotations

def check(ea_path: str, **kwargs) -> dict:
    """Run Layer 1 check. Returns {pass: bool, details: str}."""
    return {"pass": True, "layer": 1, "name": "source_lint", "details": "stub"}
