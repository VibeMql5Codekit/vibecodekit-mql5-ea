#!/usr/bin/env python3
"""MetaEditor compile wrapper — wraps metaeditor64.exe for CLI use.

Usage:
    mql5-compile path/to/EA.mq5
    mql5-compile path/to/EA.mq5 --include ./Include
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def find_metaeditor() -> str | None:
    """Locate metaeditor64.exe (env var, Wine prefix, or Windows default)."""
    env = os.environ.get("METAEDITOR_PATH")
    if env and Path(env).exists():
        return env

    if sys.platform.startswith("linux"):
        wineprefix = os.environ.get("WINEPREFIX",
                                     str(Path.home() / ".wine-mql5"))
        prefix = Path(wineprefix)
        if prefix.exists():
            candidates = list(prefix.rglob("metaeditor64.exe"))
            if candidates:
                return str(candidates[0])

    if sys.platform == "win32":
        default = Path(r"C:\Program Files\MetaTrader 5\metaeditor64.exe")
        if default.exists():
            return str(default)

    return None


def compile_mq5(source: Path, include_dir: Path | None = None,
                timeout: int = 120) -> tuple[int, str]:
    """Compile a .mq5 file. Returns (exit_code, log_text)."""
    metaeditor = find_metaeditor()
    if not metaeditor:
        return -1, "MetaEditor not found. Set METAEDITOR_PATH."

    log_path = source.with_suffix(".log")
    cmd_parts = []

    if sys.platform.startswith("linux"):
        xvfb = shutil.which("xvfb-run")
        if xvfb:
            cmd_parts.extend(["xvfb-run", "-a"])
        cmd_parts.extend(["wine", metaeditor])
    else:
        cmd_parts.append(metaeditor)

    cmd_parts.append(f"/compile:{source}")
    if include_dir:
        cmd_parts.append(f"/include:{include_dir}")
    cmd_parts.append(f"/log:{log_path}")

    subprocess.run(cmd_parts, capture_output=True, text=True,
                   timeout=timeout)

    log_text = ""
    if log_path.exists():
        try:
            log_text = log_path.read_text(encoding="utf-16-le", errors="ignore")
        except OSError:
            log_text = log_path.read_text(errors="ignore")

    errors = len(re.findall(r"(?i)\d+\s+error", log_text))
    warnings = len(re.findall(r"(?i)\d+\s+warning", log_text))

    print(f"Compile: {source.name}")
    if "0 error" in log_text.lower():
        print(f"  Result: SUCCESS (0 errors, {warnings} warnings)")
        return 0, log_text
    else:
        print(f"  Result: FAILED ({errors} errors, {warnings} warnings)")
        return 1, log_text


def main() -> int:
    parser = argparse.ArgumentParser(description="MQL5 compile wrapper")
    parser.add_argument("source", type=Path, help=".mq5 file to compile")
    parser.add_argument("--include", type=Path, help="Include directory")
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()

    if not args.source.exists():
        print(f"Error: {args.source} not found", file=sys.stderr)
        return 1

    code, log = compile_mq5(args.source, args.include, args.timeout)
    return code


if __name__ == "__main__":
    sys.exit(main())
