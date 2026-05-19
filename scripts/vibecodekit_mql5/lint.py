#!/usr/bin/env python3
"""Anti-pattern linter for MQL5 EA source files.

Detects 8 critical anti-patterns (exit 1 on any)
and 5 best-practice warnings (Phase C).

Usage:
    mql5-lint path/to/EA.mq5
    mql5-lint path/to/dir/
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path
from typing import NamedTuple


class Finding(NamedTuple):
    ap_id: str
    severity: str  # CRITICAL | WARNING
    file: str
    line: int
    message: str


# 8 critical AP detectors (Phase A)
CRITICAL_DETECTORS: list[tuple[str, str, re.Pattern[str]]] = [
    ("AP-01", "No stop-loss: trade opened without SL",
     re.compile(r"""(?x)
        (?:\.Buy|\.Sell|\.BuyLimit|\.BuyStop|\.SellLimit|\.SellStop)\s*\(
        (?:[^)]*,\s*0(?:\.0+)?\s*[,)]  |  # SL param = 0
         [^,)]*,\s*[^,)]+\)            )  # Only 2 args (lot, symbol) — no SL
     """)),
    ("AP-03", "Fixed lot size (hardcoded numeric literal)",
     re.compile(r"""(?x)
        (?:\.Buy|\.Sell|\.BuyLimit|\.BuyStop|\.SellLimit|\.SellStop)\s*\(
         \s*(?:\d+\.\d+)  |          # lot = inline hardcoded number
        \b(?:lot|volume)\s*=\s*\d+\.\d+\s*;  # lot = assigned hardcoded number
     """)),
    ("AP-05", "Overfitted: excessive extern/input params",
     re.compile(r"""(?x)
        (?:^|\n)\s*(?:input|extern)\s+
     """)),
    ("AP-15", "Raw OrderSend() — use CTrade methods instead",
     re.compile(r"\bOrderSend\s*\(")),
    ("AP-17", "WebRequest in OnTick — blocks tick processing",
     re.compile(r"""(?x)
        \bvoid\s+OnTick\b[\s\S]{0,2000}\bWebRequest\s*\(
     """)),
    ("AP-18", "OrderSendAsync without OnTradeTransaction handler",
     re.compile(r"\bOrderSendAsync\s*\(")),
    ("AP-20", "Hardcoded pip value (use CPipNormalizer)",
     re.compile(r"""(?x)
        (?:\*\s*(?:0\.0001|0\.01|10\s*\*\s*_Point)\b) |
        (?:=\s*(?:0\.0001|0\.01)\s*;)
     """)),
    ("AP-21", "JPY/XAU pip broken — digits not checked",
     re.compile(r"""(?x)
        (?:_Point\s*\*\s*10(?:\b|[^0-9])   # Assumes 5-digit everywhere
           (?!.*(?:Digits|_Digits))
        ) |
        (?:digits-tested:\s*\d                # Only tested one digit class
        )
     """)),
]


# 5 best-practice AP detectors (Phase C — warnings, not blocking)
WARNING_DETECTORS: list[tuple[str, str, re.Pattern[str]]] = [
    ("AP-02", "No take-profit: trade without TP target",
     re.compile(r"""(?x)
        (?:\.Buy|\.Sell|\.BuyLimit|\.BuyStop|\.SellLimit|\.SellStop)\s*\(
        [^)]*,\s*[^,]+,\s*0(?:\.0+)?\s*[,)]  # TP param = 0
     """)),
    ("AP-04", "No trailing stop implementation",
     re.compile(r"")),  # special: absence-check, handled below
    ("AP-06", "No error retry on trade operations",
     re.compile(r"")),  # special: absence-check, handled below
    ("AP-07", "Print() used instead of PrintFormat()",
     re.compile(r"\bPrint\s*\(\s*\"[^\"]*\"\s*\+\s*")),
    ("AP-08", "No comment on trade operation",
     re.compile(r"""(?x)
        (?:\.Buy|\.Sell)\s*\(\s*[^)]*\)
        (?!.*\.SetComment)
     """)),
]


def lint_file(path: Path) -> list[Finding]:
    """Lint a single .mq5/.mqh file for anti-patterns."""
    findings: list[Finding] = []
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except (OSError, PermissionError):
        return findings

    for ap_id, message, pattern in CRITICAL_DETECTORS:
        if ap_id == "AP-05":
            count = len(pattern.findall(content))
            if count > 6:
                findings.append(Finding(ap_id, "CRITICAL", str(path), 1,
                                        f"{message} ({count} inputs, max 6)"))
            continue

        if ap_id == "AP-18":
            has_async = re.search(r"\bOrderSendAsync\s*\(", content)
            code_no_comments = re.sub(r"//[^\n]*", "", content)
            code_no_comments = re.sub(r"/\*[\s\S]*?\*/", "", code_no_comments)
            has_handler = re.search(r"\bvoid\s+OnTradeTransaction\b", code_no_comments)
            if has_async and not has_handler:
                match = re.search(r"\bOrderSendAsync\s*\(", content)
                ln = content[:match.start()].count("\n") + 1 if match else 1
                findings.append(Finding(ap_id, "CRITICAL", str(path), ln, message))
            continue

        for match in pattern.finditer(content):
            ln = content[:match.start()].count("\n") + 1
            findings.append(Finding(ap_id, "CRITICAL", str(path), ln, message))

    # Phase C: 5 best-practice warning detectors
    code_no_comments = re.sub(r"//[^\n]*", "", content)
    code_no_comments = re.sub(r"/\*[\s\S]*?\*/", "", code_no_comments)

    for ap_id, message, pattern in WARNING_DETECTORS:
        if ap_id == "AP-04":
            has_trade = re.search(r"(?:\.Buy|\.Sell)\s*\(", code_no_comments)
            has_trail = re.search(
                r"(?:Trailing|TrailingStop|ModifyPosition|PositionModify)",
                code_no_comments)
            if has_trade and not has_trail:
                findings.append(Finding(ap_id, "WARNING", str(path), 1,
                                        message))
            continue

        if ap_id == "AP-06":
            has_send = re.search(
                r"(?:\.Buy|\.Sell|OrderSend)\s*\(", code_no_comments)
            has_retry = re.search(
                r"(?:retry|TRADE_RETCODE_REQUOTE|Sleep\s*\(\s*\d+\s*\))",
                code_no_comments)
            if has_send and not has_retry:
                findings.append(Finding(ap_id, "WARNING", str(path), 1,
                                        message))
            continue

        for match in pattern.finditer(code_no_comments):
            ln = code_no_comments[:match.start()].count("\n") + 1
            findings.append(Finding(ap_id, "WARNING", str(path), ln,
                                    message))

    return findings


def lint_paths(paths: list[Path]) -> list[Finding]:
    """Lint files or directories."""
    all_findings: list[Finding] = []
    for p in paths:
        if p.is_dir():
            for f in sorted(p.rglob("*.mq5")) + sorted(p.rglob("*.mqh")):
                all_findings.extend(lint_file(f))
        elif p.suffix in (".mq5", ".mqh"):
            all_findings.extend(lint_file(p))
    return all_findings


def main() -> int:
    parser = argparse.ArgumentParser(description="MQL5 anti-pattern linter")
    parser.add_argument("paths", nargs="+", type=Path, help=".mq5/.mqh files or dirs")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    findings = lint_paths(args.paths)

    criticals = [f for f in findings if f.severity == "CRITICAL"]
    warnings = [f for f in findings if f.severity == "WARNING"]

    if args.json:
        import json
        print(json.dumps([f._asdict() for f in findings], indent=2))
    else:
        for f in findings:
            icon = "X" if f.severity == "CRITICAL" else "!"
            print(f"[{icon}] {f.ap_id} {f.file}:{f.line} — {f.message}")

        print(f"\n{len(criticals)} critical, {len(warnings)} warnings")

    return 1 if criticals else 0


if __name__ == "__main__":
    sys.exit(main())
