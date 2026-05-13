#!/usr/bin/env python3
"""Auto-refactor hardcoded pip patterns to CPipNormalizer calls.

Detects hardcoded pip values (0.0001, 0.01, 10*_Point) and suggests
replacements using CPipNormalizer.Pips() calls.

Usage:
    mql5-pip-normalize path/to/EA.mq5
    mql5-pip-normalize path/to/EA.mq5 --fix   # auto-apply
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

HARDCODED_PATTERNS = [
    (re.compile(r"\b(\d+)\s*\*\s*0\.0001\b"), r"pipNorm.Pips(\1)"),
    (re.compile(r"\b(\d+)\s*\*\s*0\.01\b"), r"pipNorm.Pips(\1)"),
    (re.compile(r"\b0\.0001\s*\*\s*(\d+)\b"), r"pipNorm.Pips(\1)"),
    (re.compile(r"\b0\.01\s*\*\s*(\d+)\b"), r"pipNorm.Pips(\1)"),
    (re.compile(r"(\d+)\s*\*\s*10\s*\*\s*_Point\b"), r"pipNorm.Pips(\1)"),
    (re.compile(r"10\s*\*\s*_Point\s*\*\s*(\d+)\b"), r"pipNorm.Pips(\1)"),
]

INCLUDE_LINE = '#include "CPipNormalizer.mqh"'
DECL_LINE = "CPipNormalizer pipNorm;"
INIT_LINE = "pipNorm.Init();"


def scan_file(path: Path) -> list[tuple[int, str, str]]:
    """Return list of (line_num, original, suggested) replacements."""
    content = path.read_text(encoding="utf-8", errors="replace")
    lines = content.splitlines()
    replacements = []

    for i, line in enumerate(lines, start=1):
        new_line = line
        for pattern, repl in HARDCODED_PATTERNS:
            new_line = pattern.sub(repl, new_line)
        if new_line != line:
            replacements.append((i, line.strip(), new_line.strip()))

    return replacements


def fix_file(path: Path) -> int:
    """Apply replacements in-place. Returns count of changes."""
    content = path.read_text(encoding="utf-8", errors="replace")
    new_content = content
    count = 0

    for pattern, repl in HARDCODED_PATTERNS:
        new_content, n = pattern.subn(repl, new_content)
        count += n

    if count > 0:
        if INCLUDE_LINE not in new_content:
            new_content = INCLUDE_LINE + "\n" + new_content
        path.write_text(new_content, encoding="utf-8")

    return count


def main() -> int:
    parser = argparse.ArgumentParser(description="Pip normalize refactorer")
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--fix", action="store_true", help="Apply fixes in-place")
    args = parser.parse_args()

    total = 0
    for p in args.paths:
        files = list(p.rglob("*.mq5")) + list(p.rglob("*.mqh")) if p.is_dir() else [p]
        for f in files:
            replacements = scan_file(f)
            if replacements:
                print(f"\n{f} ({len(replacements)} findings):")
                for ln, old, new in replacements:
                    print(f"  L{ln}: {old}")
                    print(f"    -> {new}")
                total += len(replacements)
                if args.fix:
                    fix_file(f)
                    print(f"  FIXED {len(replacements)} patterns")

    print(f"\nTotal: {total} hardcoded pip patterns found")
    return 1 if total > 0 and not args.fix else 0


if __name__ == "__main__":
    sys.exit(main())
