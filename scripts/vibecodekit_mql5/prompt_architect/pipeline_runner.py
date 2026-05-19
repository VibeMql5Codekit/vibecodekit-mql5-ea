"""Safe runner for Prompt Architect pipeline plans."""
from __future__ import annotations

import json
import shlex
import subprocess
from pathlib import Path
from typing import cast

ALLOWED_TOOLS = {
    "mql5-prompt-architect",
    "mql5-build",
    "mql5-lint",
    "mql5-compile",
    "mql5-permission",
    "mql5-matrix",
}
EXPECTED_STEPS = (
    ("validate_prompt_config", "mql5-prompt-architect"),
    ("generate_planning_artifacts", "mql5-prompt-architect"),
    ("build_scaffold", "mql5-build"),
    ("lint", "mql5-lint"),
    ("compile", "mql5-compile"),
    ("permission_gate", "mql5-permission"),
    ("quality_matrix", "mql5-matrix"),
)


def load_pipeline_plan(path: Path) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return cast(dict[str, object], payload)


def validate_pipeline_plan(plan: dict[str, object]) -> list[str]:
    """Validate the deterministic command envelope before execution."""
    errors: list[str] = []
    commands = plan.get("commands")
    if plan.get("schema_version") != "1.0":
        errors.append("schema_version must be 1.0")
    if not isinstance(commands, list) or not commands:
        return [*errors, "commands must be a non-empty list"]
    if len(commands) != len(EXPECTED_STEPS):
        errors.append(f"commands must contain exactly {len(EXPECTED_STEPS)} steps")

    expected_step = 1
    for item in commands:
        if expected_step <= len(EXPECTED_STEPS):
            expected_name = EXPECTED_STEPS[expected_step - 1][0]
            expected_tool = EXPECTED_STEPS[expected_step - 1][1]
        else:
            expected_name = ""
            expected_tool = ""
        if not isinstance(item, dict):
            errors.append(f"commands[{expected_step - 1}] must be an object")
            expected_step += 1
            continue
        step = item.get("step")
        command = item.get("command")
        name = item.get("name")
        if step != expected_step:
            errors.append(f"commands[{expected_step - 1}].step must be {expected_step}")
        if not isinstance(name, str) or not name:
            errors.append(f"commands[{expected_step - 1}].name is required")
        elif name != expected_name:
            errors.append(f"commands[{expected_step - 1}].name must be {expected_name}")
        if not isinstance(command, str) or not command:
            errors.append(f"commands[{expected_step - 1}].command is required")
            expected_step += 1
            continue
        parts = shlex.split(command)
        if expected_tool and (not parts or parts[0] != expected_tool):
            errors.append(
                f"commands[{expected_step - 1}].command must start with {expected_tool}"
            )
        elif parts[0] not in ALLOWED_TOOLS:
            errors.append(f"commands[{expected_step - 1}].command uses unsupported tool")
        expected_step += 1
    return errors


def run_pipeline_plan(
    plan: dict[str, object],
    workdir: Path,
    execute: bool = False,
    from_step: int = 1,
    to_step: int | None = None,
) -> dict[str, object]:
    """Dry-run or execute a validated Prompt Architect pipeline plan."""
    errors = validate_pipeline_plan(plan)
    if errors:
        return {"valid": False, "all_pass": False, "errors": errors, "steps": []}
    if from_step < 1 or (to_step is not None and to_step < from_step):
        return {
            "valid": False,
            "all_pass": False,
            "errors": ["invalid pipeline step range"],
            "steps": [],
        }

    raw_commands = cast(list[dict[str, object]], plan["commands"])
    selected: list[dict[str, object]] = []
    for item in raw_commands:
        step = cast(int, item["step"])
        if step < from_step or (to_step is not None and step > to_step):
            continue
        selected.append(item)
    if not selected:
        return {
            "valid": False,
            "all_pass": False,
            "errors": ["pipeline step range selected no commands"],
            "steps": [],
        }

    results: list[dict[str, object]] = []
    all_pass = True
    for item in selected:
        command = cast(str, item["command"])
        result = {
            "step": item["step"],
            "name": item["name"],
            "command": command,
            "status": "DRY-RUN",
            "exit_code": 0,
        }
        if execute:
            exit_code = 1
            try:
                completed = subprocess.run(
                    shlex.split(command),
                    cwd=workdir,
                    capture_output=True,
                    text=True,
                )
                result["status"] = "PASS" if completed.returncode == 0 else "FAIL"
                exit_code = completed.returncode
                result["exit_code"] = exit_code
                result["stdout"] = completed.stdout
                result["stderr"] = completed.stderr
            except OSError as exc:
                result["status"] = "FAIL"
                result["exit_code"] = 1
                result["stdout"] = ""
                result["stderr"] = str(exc)
            if exit_code != 0:
                all_pass = False
                results.append(result)
                break
        results.append(result)

    return {
        "valid": True,
        "execute": execute,
        "all_pass": all_pass,
        "steps_run": len(results),
        "steps": results,
    }


def render_pipeline_run(summary: dict[str, object]) -> str:
    """Render a human-readable pipeline run summary."""
    if not summary["valid"]:
        return "\n".join(["Pipeline plan invalid:", *[f"  ERROR: {e}" for e in summary["errors"]]])
    mode = "execute" if summary["execute"] else "dry-run"
    lines = [f"Pipeline {mode}: {'PASS' if summary['all_pass'] else 'FAIL'}"]
    for item in cast(list[dict[str, object]], summary["steps"]):
        lines.append(
            f"  [{item['status']}] step {item['step']} {item['name']}: {item['command']}"
        )
    return "\n".join(lines)
