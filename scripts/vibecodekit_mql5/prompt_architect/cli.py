#!/usr/bin/env python3
"""Prompt Architect deterministic CLI."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Callable

from vibecodekit_mql5.prompt_architect.recommend import recommend_preset
from vibecodekit_mql5.prompt_architect.render import (
    render_blueprint,
    render_prompt,
    render_requirements,
    render_vision,
)
from vibecodekit_mql5.prompt_architect.schema import load_config, validate_config


def _write(path: Path | None, content: str) -> None:
    if path is None:
        print(content)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _render_if_requested(
    config: dict,
    target: Path | None,
    renderer: Callable[[dict], str],
    printed: bool,
) -> bool:
    if target is None:
        return printed
    _write(target, renderer(config))
    return printed


def build_result(config_path: Path) -> tuple[dict, dict]:
    """Load a config and return validation plus recommendation."""
    config = load_config(config_path)
    validation = validate_config(config)
    result = {
        "config": str(config_path),
        "valid": validation["valid"],
        "errors": validation["errors"],
        "warnings": validation["warnings"],
    }
    if validation["valid"]:
        result["recommended"] = recommend_preset(config)
    return config, result


def main() -> int:
    parser = argparse.ArgumentParser(description="Prompt Architect deterministic CLI")
    parser.add_argument("--config", type=Path, required=True, help="EA settings JSON/YAML")
    parser.add_argument("--validate", action="store_true", help="Validate config and print summary")
    parser.add_argument("--recommend-preset", action="store_true", help="Print preset recommendation")
    parser.add_argument("--render-prompt", type=Path, default=None, help="Write implementation prompt")
    parser.add_argument("--vision", type=Path, default=None, help="Write vision document")
    parser.add_argument("--requirements", type=Path, default=None, help="Write requirements JSON")
    parser.add_argument("--blueprint", type=Path, default=None, help="Write blueprint document")
    parser.add_argument("--json", action="store_true", help="Print machine-readable summary")
    args = parser.parse_args()

    try:
        config, result = build_result(args.config)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if not result["valid"]:
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Prompt Architect config invalid: {args.config}", file=sys.stderr)
            for error in result["errors"]:
                print(f"  ERROR: {error}", file=sys.stderr)
            for warning in result["warnings"]:
                print(f"  WARN: {warning}", file=sys.stderr)
        return 1

    printed = False
    if args.json:
        print(json.dumps(result, indent=2))
        printed = True
    elif args.validate:
        print(f"Prompt Architect config valid: {args.config}")
        for warning in result["warnings"]:
            print(f"  WARN: {warning}")
        printed = True

    if args.recommend_preset and not args.json:
        recommendation = result["recommended"]
        print(
            f"Recommended: {recommendation['preset']}/{recommendation['stack']} "
            f"(confidence={recommendation['confidence']})"
        )
        printed = True

    printed = _render_if_requested(config, args.render_prompt, render_prompt, printed)
    printed = _render_if_requested(config, args.vision, render_vision, printed)
    printed = _render_if_requested(config, args.requirements, render_requirements, printed)
    printed = _render_if_requested(config, args.blueprint, render_blueprint, printed)

    if not printed and not any([args.recommend_preset, args.render_prompt, args.vision,
                               args.requirements, args.blueprint]):
        print(f"Prompt Architect config valid: {args.config}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
