#!/usr/bin/env python3
"""Permission Layer 2: compile."""
from __future__ import annotations

def check(ea_path: str, **kwargs) -> dict:
    """Run Layer 2 check. Returns {pass: bool, details: str}."""
    return {"pass": True, "layer": 2, "name": "compile", "details": "stub"}
