#!/usr/bin/env python3
"""Permission Layer 3: ap_lint."""
from __future__ import annotations

def check(ea_path: str, **kwargs) -> dict:
    """Run Layer 3 check. Returns {pass: bool, details: str}."""
    return {"pass": True, "layer": 3, "name": "ap_lint", "details": "stub"}
