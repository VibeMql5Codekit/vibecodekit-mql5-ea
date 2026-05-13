#!/usr/bin/env python3
"""metaeditor-bridge tools — compile, syntax-check, include-resolution."""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

TOOLS: list[dict] = [
    {"name": "compile", "description": "Compile .mq5 file via MetaEditor (Wine)",
     "inputSchema": {"type": "object",
                     "properties": {"file": {"type": "string"}},
                     "required": ["file"]}},
    {"name": "syntax_check", "description": "Check MQL5 syntax without full compile",
     "inputSchema": {"type": "object",
                     "properties": {"file": {"type": "string"}},
                     "required": ["file"]}},
    {"name": "list_includes", "description": "List #include dependencies of a file",
     "inputSchema": {"type": "object",
                     "properties": {"file": {"type": "string"}},
                     "required": ["file"]}},
]


def handle_compile(params: dict) -> dict:
    """Compile a .mq5 file using MetaEditor via Wine."""
    fpath = Path(params["file"])
    if not fpath.exists():
        return {"error": f"File not found: {fpath}"}

    me_paths = [Path("/opt/metaeditor64/metaeditor64.exe"),
                Path.home() / ".wine" / "MetaEditor64.exe"]
    me = next((m for m in me_paths if m.exists()), None)
    if me is None:
        return {"status": "skipped", "reason": "MetaEditor not installed"}

    try:
        r = subprocess.run(["wine", str(me), f"/compile:{fpath}", "/log"],
                           capture_output=True, text=True, timeout=60)
        return {"status": "ok" if r.returncode == 0 else "error",
                "returncode": r.returncode, "stdout": r.stdout[:500],
                "stderr": r.stderr[:500]}
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        return {"status": "skipped", "reason": str(e)}


def handle_syntax_check(params: dict) -> dict:
    """Basic syntax validation without MetaEditor."""
    fpath = Path(params["file"])
    if not fpath.exists():
        return {"error": f"File not found: {fpath}"}

    content = fpath.read_text(encoding="utf-8", errors="replace")
    issues: list[str] = []

    if not re.search(r"#property\s+strict", content):
        issues.append("missing #property strict")

    opens = content.count("{")
    closes = content.count("}")
    if opens != closes:
        issues.append(f"brace mismatch: {opens} open vs {closes} close")

    parens_o = content.count("(")
    parens_c = content.count(")")
    if parens_o != parens_c:
        issues.append(f"paren mismatch: {parens_o} vs {parens_c}")

    return {"status": "ok" if not issues else "warning",
            "issues": issues, "lines": len(content.splitlines())}


def handle_list_includes(params: dict) -> dict:
    """Extract #include directives from a file."""
    fpath = Path(params["file"])
    if not fpath.exists():
        return {"error": f"File not found: {fpath}"}

    content = fpath.read_text(encoding="utf-8", errors="replace")
    includes = re.findall(r'#include\s*[<"]([^>"]+)[>"]', content)
    return {"file": str(fpath), "includes": includes,
            "count": len(includes)}


HANDLERS = {"compile": handle_compile, "syntax_check": handle_syntax_check,
            "list_includes": handle_list_includes}
