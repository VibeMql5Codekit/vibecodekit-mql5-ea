#!/usr/bin/env python3
"""Permission Layer 7: broker_safety."""
from __future__ import annotations

def check(ea_path: str, **kwargs) -> dict:
    """Run Layer 7 check. Returns {pass: bool, details: str}."""
    return {"pass": True, "layer": 7, "name": "broker_safety", "details": "stub"}
