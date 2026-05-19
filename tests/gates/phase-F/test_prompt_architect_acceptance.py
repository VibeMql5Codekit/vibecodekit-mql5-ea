"""Phase F acceptance tests — deterministic Prompt Architect intake."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPTS = REPO_ROOT / "scripts"
EXAMPLES = REPO_ROOT / "examples" / "prompt-architect"
sys.path.insert(0, str(SCRIPTS))

from vibecodekit_mql5.prompt_architect.recommend import recommend_preset  # noqa: E402
from vibecodekit_mql5.prompt_architect.bridge import build_rri_bridge  # noqa: E402
from vibecodekit_mql5.prompt_architect.pipeline import build_pipeline_plan  # noqa: E402
from vibecodekit_mql5.prompt_architect.pipeline_runner import (  # noqa: E402
    run_pipeline_plan,
    validate_pipeline_plan,
)
from vibecodekit_mql5.prompt_architect.render import (  # noqa: E402
    render_blueprint,
    render_prompt,
    render_requirements,
    render_vision,
)
from vibecodekit_mql5.prompt_architect.schema import (  # noqa: E402
    load_config,
    load_schema,
    validate_config,
)


def test_prompt_architect_schema_exists_and_is_versioned():
    schema = load_schema()
    assert schema["title"] == "Vibecodekit MQL5 EA Prompt Architect Settings"
    assert schema["properties"]["schema_version"]["const"] == "1.0"
    assert "risk" in schema["required"]
    assert "execution" in schema["required"]
    assert "sltp" in schema["required"]


def test_all_prompt_architect_examples_validate():
    examples = [EXAMPLES / "xauusd-rsi-bb-scalper.json", *sorted(EXAMPLES.glob("*.yaml"))]
    assert len(examples) == 4
    for path in examples:
        config = load_config(path)
        result = validate_config(config)
        assert result["valid"], f"{path.name}: {result}"


def test_validation_fails_closed_for_grid_without_caps():
    config = load_config(EXAMPLES / "dca-grid-propfirm.yaml")
    config["grid"].pop("max_orders")
    result = validate_config(config)
    assert result["valid"] is False
    assert any("grid.max_orders" in error for error in result["errors"])


def test_validation_rejects_propfirm_without_stop_policy():
    config = load_config(EXAMPLES / "dca-grid-propfirm.yaml")
    config["sltp"] = {"mode": "none"}
    result = validate_config(config)
    assert result["valid"] is False
    assert any("stop policy" in error for error in result["errors"])


def test_validation_rejects_non_object_indicator_items():
    config = load_config(EXAMPLES / "xauusd-rsi-bb-scalper.json")
    config["strategy"]["indicators"] = ["rsi"]
    result = validate_config(config)
    assert result["valid"] is False
    assert "strategy.indicators[0] must be an object" in result["errors"]
    assert "- rsi" in render_prompt(config)


def test_preset_recommendations_match_examples():
    cases = {
        "xauusd-rsi-bb-scalper.json": ("scalping", "hedging"),
        "dca-grid-propfirm.yaml": ("dca", "hedging"),
        "onnx-trend-filter.yaml": ("ml-onnx", "python-bridge"),
        "custom-indicator-arrow-buffer.yaml": ("stdlib", "netting"),
    }
    for filename, expected in cases.items():
        recommendation = recommend_preset(load_config(EXAMPLES / filename))
        assert (recommendation["preset"], recommendation["stack"]) == expected


def test_renderers_emit_traceable_vibecodekit_outputs():
    config = load_config(EXAMPLES / "xauusd-rsi-bb-scalper.json")
    prompt = render_prompt(config)
    vision = render_vision(config)
    requirements = json.loads(render_requirements(config))
    blueprint = render_blueprint(config)

    assert "mql5-build --preset scalping --stack hedging" in prompt
    assert "mql5-permission" in prompt
    assert "# Vision: XauRsiBbScalper" in vision
    assert requirements["requirements"][0]["id"] == "REQ-001"
    assert requirements["requirements"][3]["gate"] == "layer3_ap_lint"
    assert "CPipNormalizer" in blueprint
    assert "CRiskGuard" in blueprint
    assert "## RRI bridge" in blueprint
    assert "mql5-permission --ea ./work/XauRsiBbScalper/XauRsiBbScalper.mq5 --mode TEAM --json" in blueprint


def test_prompt_architect_bridge_maps_propfirm_grid_to_enterprise_rri_and_pipeline():
    config = load_config(EXAMPLES / "dca-grid-propfirm.yaml")
    bridge = build_rri_bridge(config)
    pipeline = build_pipeline_plan(config, "examples/prompt-architect/dca-grid-propfirm.yaml")

    assert bridge["mode"] == "ENTERPRISE"
    assert bridge["personas"] == [
        "trader",
        "risk-auditor",
        "broker-engineer",
        "strategy-architect",
        "devops",
        "perf-analyst",
    ]
    assert bridge["total_questions"] == 150
    assert pipeline["recommended"]["preset"] == "dca"
    assert pipeline["recommended"]["stack"] == "hedging"
    assert pipeline["commands"][2]["command"] == (
        "mql5-build --preset dca --stack hedging --name PropFirmDcaGridGuard --output ./work"
    )
    assert pipeline["commands"][5]["command"] == (
        "mql5-permission --ea ./work/PropFirmDcaGridGuard/PropFirmDcaGridGuard.mq5 "
        "--mode ENTERPRISE --json"
    )


def test_prompt_architect_cli_validate_and_json_summary():
    cmd = [
        sys.executable,
        "-m",
        "vibecodekit_mql5.prompt_architect.cli",
        "--config",
        str(EXAMPLES / "xauusd-rsi-bb-scalper.json"),
        "--validate",
        "--recommend-preset",
        "--json",
    ]
    result = subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        env={"PYTHONPATH": str(SCRIPTS)},
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(result.stdout)
    assert payload["valid"] is True
    assert payload["recommended"]["preset"] == "scalping"
    assert payload["recommended"]["stack"] == "hedging"


def test_prompt_architect_cli_writes_outputs(tmp_path):
    prompt = tmp_path / "prompt.md"
    rri_plan = tmp_path / "rri-plan.md"
    vision = tmp_path / "vision.md"
    requirements = tmp_path / "requirements.json"
    blueprint = tmp_path / "blueprint.md"
    pipeline = tmp_path / "pipeline.json"
    cmd = [
        sys.executable,
        "-m",
        "vibecodekit_mql5.prompt_architect.cli",
        "--config",
        str(EXAMPLES / "onnx-trend-filter.yaml"),
        "--render-prompt",
        str(prompt),
        "--rri-plan",
        str(rri_plan),
        "--vision",
        str(vision),
        "--requirements",
        str(requirements),
        "--blueprint",
        str(blueprint),
        "--pipeline",
        str(pipeline),
    ]
    subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        env={"PYTHONPATH": str(SCRIPTS)},
        capture_output=True,
        text=True,
        check=True,
    )
    assert "ml-onnx" in prompt.read_text()
    assert "Mode: `TEAM`" in rri_plan.read_text()
    assert "OnnxTrendFilterEA" in vision.read_text()
    assert yaml.safe_load(requirements.read_text())["ea"] == "OnnxTrendFilterEA"
    assert "CSpreadGuard" in blueprint.read_text()
    assert json.loads(pipeline.read_text())["recommended"]["stack"] == "python-bridge"


def test_prompt_architect_pipeline_runner_dry_run_and_validates_allowlist():
    config = load_config(EXAMPLES / "dca-grid-propfirm.yaml")
    plan = build_pipeline_plan(config, "examples/prompt-architect/dca-grid-propfirm.yaml")
    assert validate_pipeline_plan(plan) == []

    summary = run_pipeline_plan(plan, REPO_ROOT, execute=False, from_step=3, to_step=4)
    assert summary["valid"] is True
    assert summary["all_pass"] is True
    assert summary["steps_run"] == 2
    assert summary["steps"][0]["status"] == "DRY-RUN"
    assert summary["steps"][0]["name"] == "build_scaffold"

    plan["commands"][0]["command"] = "rm -rf ./work"
    errors = validate_pipeline_plan(plan)
    assert errors == ["commands[0].command must start with mql5-prompt-architect"]


def test_prompt_architect_cli_run_pipeline_dry_run(tmp_path):
    config = load_config(EXAMPLES / "dca-grid-propfirm.yaml")
    pipeline = tmp_path / "pipeline.json"
    pipeline.write_text(json.dumps(build_pipeline_plan(config), indent=2), encoding="utf-8")
    cmd = [
        sys.executable,
        "-m",
        "vibecodekit_mql5.prompt_architect.cli",
        "--run-pipeline",
        str(pipeline),
        "--from-step",
        "3",
        "--to-step",
        "4",
        "--json",
    ]
    result = subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        env={"PYTHONPATH": str(SCRIPTS)},
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(result.stdout)
    assert payload["execute"] is False
    assert payload["all_pass"] is True
    assert [item["name"] for item in payload["steps"]] == ["build_scaffold", "lint"]


def test_prompt_architect_cli_invalid_config_exits_one(tmp_path):
    invalid = tmp_path / "invalid.yaml"
    config = load_config(EXAMPLES / "custom-indicator-arrow-buffer.yaml")
    config["risk"].pop("fixed_lot")
    invalid.write_text(yaml.safe_dump(config), encoding="utf-8")
    cmd = [
        sys.executable,
        "-m",
        "vibecodekit_mql5.prompt_architect.cli",
        "--config",
        str(invalid),
        "--validate",
    ]
    result = subprocess.run(
        cmd,
        cwd=REPO_ROOT,
        env={"PYTHONPATH": str(SCRIPTS)},
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "fixed lot mode requires risk.fixed_lot" in result.stderr
