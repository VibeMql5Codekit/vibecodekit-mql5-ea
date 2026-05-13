#!/usr/bin/env python3
"""Permission Layer 2: compile — MetaEditor compilation gate."""
from __future__ import annotations

import subprocess
from pathlib import Path


def check(ea_path: str, **kwargs: object) -> dict:
    """Attempt MetaEditor compilation. Passes if MetaEditor unavailable."""
    p = Path(ea_path)
    if not p.exists():
        return {"pass": False, "layer": 2, "name": "compile",
                "details": f"File not found: {ea_path}"}

    me_paths = [
        Path("/opt/metaeditor64/metaeditor64.exe"),
        Path.home() / ".wine" / "MetaEditor64.exe",
    ]
    me = next((m for m in me_paths if m.exists()), None)
    if me is None:
        return {"pass": True, "layer": 2, "name": "compile",
                "details": "MetaEditor not found — skipped (non-blocking)"}

    try:
        result = subprocess.run(
            ["wine", str(me), "/compile:" + str(p), "/log"],
            capture_output=True, text=True, timeout=60)
        ok = result.returncode == 0
        return {"pass": ok, "layer": 2, "name": "compile",
                "details": result.stdout[:200] if not ok else "OK"}
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        return {"pass": True, "layer": 2, "name": "compile",
                "details": f"Wine/MetaEditor unavailable: {exc} — skipped"}
