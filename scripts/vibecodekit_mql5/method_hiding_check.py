#!/usr/bin/env python3
"""method_hiding_check — Detect MQL5 method hiding issues.

Scans for parent/child class method conflicts where child hides parent method.
Usage: mql5-method-hiding-check --ea EA.mq5 [--json]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

CLASS_PATTERN = re.compile(
    r"class\s+(\w+)(?:\s*:\s*public\s+(\w+))?\s*\{([^}]*)\}",
    re.DOTALL,
)
METHOD_PATTERN = re.compile(
    r"(?:virtual\s+)?(\w+)\s+(\w+)\s*\(([^)]*)\)",
)


def extract_classes(content: str) -> list[dict]:
    classes = []
    for m in CLASS_PATTERN.finditer(content):
        name = m.group(1)
        parent = m.group(2)
        body = m.group(3)
        methods = []
        for mm in METHOD_PATTERN.finditer(body):
            ret_type = mm.group(1)
            mname = mm.group(2)
            params = mm.group(3).strip()
            is_virtual = "virtual" in content[max(0, mm.start() - 20):mm.start()]
            methods.append({"name": mname, "return": ret_type, "params": params, "virtual": is_virtual})
        classes.append({"name": name, "parent": parent, "methods": methods})
    return classes


def check_hiding(classes: list[dict]) -> list[dict]:
    class_map = {c["name"]: c for c in classes}
    issues = []
    for cls in classes:
        if not cls["parent"] or cls["parent"] not in class_map:
            continue
        parent = class_map[cls["parent"]]
        parent_methods = {m["name"]: m for m in parent["methods"]}
        for method in cls["methods"]:
            if method["name"] in parent_methods:
                pm = parent_methods[method["name"]]
                if not pm["virtual"]:
                    issues.append({
                        "class": cls["name"],
                        "parent": cls["parent"],
                        "method": method["name"],
                        "severity": "warning",
                        "message": f"{cls['name']}::{method['name']} hides {cls['parent']}::{method['name']} (not virtual)",
                    })
                elif method["params"] != pm["params"]:
                    issues.append({
                        "class": cls["name"],
                        "parent": cls["parent"],
                        "method": method["name"],
                        "severity": "info",
                        "message": f"Signature mismatch: {cls['name']}({method['params']}) vs {cls['parent']}({pm['params']})",
                    })
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Method hiding checker")
    parser.add_argument("--ea", type=Path, required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if not args.ea.exists():
        print(f"Error: {args.ea} not found")
        return 1

    content = args.ea.read_text(encoding="utf-8", errors="replace")
    classes = extract_classes(content)
    issues = check_hiding(classes)

    if args.json:
        print(json.dumps({"file": str(args.ea), "classes": len(classes), "issues": issues}))
    else:
        print(f"Method hiding check: {args.ea} ({len(classes)} classes)")
        if issues:
            for i in issues:
                print(f"  [{i['severity']}] {i['message']}")
        else:
            print("  No method hiding issues found.")

    return 1 if any(i["severity"] == "warning" for i in issues) else 0


if __name__ == "__main__":
    sys.exit(main())
