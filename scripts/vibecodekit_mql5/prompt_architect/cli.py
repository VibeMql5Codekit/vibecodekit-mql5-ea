#!/usr/bin/env python3
"""Prompt Architect deterministic CLI."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Callable

from vibecodekit_mql5.prompt_architect.bridge import render_rri_plan
from vibecodekit_mql5.prompt_architect.pipeline import render_pipeline_plan
from vibecodekit_mql5.prompt_architect.pipeline_runner import (
    load_pipeline_plan,
    render_pipeline_run,
    run_pipeline_plan,
    validate_pipeline_plan,
)
from vibecodekit_mql5.prompt_architect.provider import LLM_PROVIDERS, run_llm_codegen
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


def _without_content(summary: dict[str, object]) -> dict[str, object]:
    return {key: value for key, value in summary.items() if key != "content"}


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
    parser.add_argument("--config", type=Path, default=None, help="EA settings JSON/YAML")
    parser.add_argument("--validate", action="store_true", help="Validate config and print summary")
    parser.add_argument("--recommend-preset", action="store_true", help="Print preset recommendation")
    parser.add_argument("--render-prompt", type=Path, default=None, help="Write implementation prompt")
    parser.add_argument("--rri-plan", type=Path, default=None, help="Write RRI bridge plan")
    parser.add_argument("--vision", type=Path, default=None, help="Write vision document")
    parser.add_argument("--requirements", type=Path, default=None, help="Write requirements JSON")
    parser.add_argument("--blueprint", type=Path, default=None, help="Write blueprint document")
    parser.add_argument("--pipeline", type=Path, default=None, help="Write next-step pipeline JSON")
    parser.add_argument("--llm-provider", choices=LLM_PROVIDERS, default=None,
                        help="Prepare or run optional provider-backed codegen")
    parser.add_argument("--llm-model", default=None, help="Provider model override")
    parser.add_argument("--llm-endpoint", default=None, help="Provider endpoint override")
    parser.add_argument("--llm-output", type=Path, default=None, help="Write LLM prompt/response")
    parser.add_argument("--llm-timeout", type=int, default=30, help="Provider call timeout seconds")
    parser.add_argument("--run-pipeline", type=Path, default=None, help="Validate or run pipeline JSON")
    parser.add_argument("--execute", action="store_true", help="Execute --run-pipeline commands")
    parser.add_argument("--workdir", type=Path, default=Path("."), help="Pipeline working directory")
    parser.add_argument("--from-step", type=int, default=1, help="First pipeline step to run")
    parser.add_argument("--to-step", type=int, default=None, help="Last pipeline step to run")
    parser.add_argument("--json", action="store_true", help="Print machine-readable summary")
    args = parser.parse_args()

    if args.run_pipeline is not None:
        try:
            plan = load_pipeline_plan(args.run_pipeline)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1
        if not args.execute:
            errors = validate_pipeline_plan(plan)
            summary = {"valid": not errors, "execute": False, "all_pass": not errors,
                       "errors": errors, "steps": []}
            if not errors:
                summary = run_pipeline_plan(plan, args.workdir, False, args.from_step, args.to_step)
        else:
            summary = run_pipeline_plan(plan, args.workdir, True, args.from_step, args.to_step)
        if args.json:
            print(json.dumps(summary, indent=2))
        else:
            print(render_pipeline_run(summary))
        return 0 if summary["valid"] and summary["all_pass"] else 1

    if args.config is None:
        parser.error("--config required unless --run-pipeline is used")

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

    llm_failed = False
    llm_summary = None
    if args.llm_provider is not None:
        llm_summary = run_llm_codegen(
            config,
            args.llm_provider,
            args.llm_model,
            args.llm_endpoint,
            args.llm_timeout,
        )
        result["llm"] = _without_content(llm_summary)
        llm_failed = llm_summary["status"] not in {"prompt-ready", "ok"}
        if args.llm_output is not None and not llm_failed:
            _write(args.llm_output, str(llm_summary.get("content", "")))

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
    printed = _render_if_requested(config, args.rri_plan, render_rri_plan, printed)
    printed = _render_if_requested(config, args.vision, render_vision, printed)
    printed = _render_if_requested(config, args.requirements, render_requirements, printed)
    printed = _render_if_requested(config, args.blueprint, render_blueprint, printed)
    printed = _render_if_requested(
        config,
        args.pipeline,
        lambda item: render_pipeline_plan(item, str(args.config)),
        printed,
    )
    if llm_summary is not None and not args.json:
        if llm_failed:
            print(f"LLM provider failed: {llm_summary.get('error', 'unknown error')}",
                  file=sys.stderr)
        else:
            target = f" -> {args.llm_output}" if args.llm_output is not None else ""
            print(
                f"LLM provider {llm_summary['provider']} status: "
                f"{llm_summary['status']}{target}"
            )
        printed = True

    if not printed and not any([args.recommend_preset, args.render_prompt, args.vision,
                               args.rri_plan, args.requirements, args.blueprint,
                               args.pipeline, args.llm_provider]):
        print(f"Prompt Architect config valid: {args.config}")

    return 1 if llm_failed else 0


if __name__ == "__main__":
    sys.exit(main())
