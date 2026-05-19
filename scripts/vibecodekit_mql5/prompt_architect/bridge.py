"""Bridge Prompt Architect configs into RRI and vibecodekit pipeline plans."""
from __future__ import annotations

from typing import Any

from vibecodekit_mql5.rri.personas import PERSONA_NAMES, get_questions_for_mode, load_persona
from vibecodekit_mql5.rri.step_workflow import WorkflowEngine

BASE_PERSONAS = ("trader", "risk-auditor", "broker-engineer", "strategy-architect")
EXTERNAL_INTEGRATIONS = ("telegram", "webrequest", "onnx", "license", "custom_indicator")
PERFORMANCE_METHODS = {"trend", "mean_reversion", "scalping", "grid", "dca",
                       "martingale", "breakout", "portfolio", "onnx"}


def _field(data: dict[str, Any], path: str) -> Any:
    current: Any = data
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def infer_rri_mode(config: dict[str, Any]) -> str:
    """Infer the minimum RRI depth needed before implementation."""
    if config.get("account_type") in {"live", "prop_firm"}:
        return "ENTERPRISE"
    if config.get("broker_mode") == "unknown":
        return "ENTERPRISE"
    if _field(config, "grid.enabled"):
        return "TEAM"
    integrations = config.get("integrations", {})
    if isinstance(integrations, dict) and any(
        integrations.get(key) for key in EXTERNAL_INTEGRATIONS
    ):
        return "TEAM"
    if config.get("account_type") == "demo":
        return "TEAM"
    return "PERSONAL"


def select_rri_personas(config: dict[str, Any]) -> dict[str, list[str]]:
    """Select RRI personas and deterministic reasons from EASettings fields."""
    reasons: dict[str, list[str]] = {}

    def add(persona: str, reason: str) -> None:
        reasons.setdefault(persona, [])
        if reason not in reasons[persona]:
            reasons[persona].append(reason)

    for persona in BASE_PERSONAS:
        add(persona, "required for every Prompt Architect implementation plan")

    account_type = config.get("account_type")
    if account_type in {"live", "prop_firm"}:
        add("devops", f"{account_type} account requires deployment controls")
        add("perf-analyst", f"{account_type} account requires performance evidence")

    if _field(config, "grid.enabled"):
        add("risk-auditor", "grid/DCA requires hard risk caps and stop policies")
        add("perf-analyst", "grid/DCA requires drawdown and robustness review")

    if config.get("trading_method") in PERFORMANCE_METHODS:
        add("perf-analyst", f"{config['trading_method']} strategy requires metric targets")

    integrations = config.get("integrations", {})
    if isinstance(integrations, dict):
        enabled = [key for key in EXTERNAL_INTEGRATIONS if integrations.get(key)]
        if enabled:
            add("devops", f"external integration enabled: {', '.join(enabled)}")
        if integrations.get("onnx"):
            add("strategy-architect", "ONNX strategy requires fallback signal design")
            add("perf-analyst", "ONNX strategy requires confidence-threshold validation")
        if integrations.get("custom_indicator"):
            add("strategy-architect", "custom indicator buffers require explicit signal mapping")

    if config.get("broker_mode") == "unknown":
        add("broker-engineer", "unknown broker mode must be resolved before scaffold build")

    return {persona: reasons[persona] for persona in PERSONA_NAMES if persona in reasons}


def build_rri_bridge(config: dict[str, Any]) -> dict[str, Any]:
    """Build persona-scoped RRI questions from a normalized Prompt Architect config."""
    mode = infer_rri_mode(config)
    selected = select_rri_personas(config)
    interviews = []
    for persona, reasons in selected.items():
        data = load_persona(persona)
        questions = get_questions_for_mode(data, mode)
        interviews.append({
            "persona": persona,
            "role": data.get("role", ""),
            "reasons": reasons,
            "question_count": len(questions),
            "questions": questions,
        })
    return {
        "mode": mode,
        "personas": list(selected),
        "interviews": interviews,
        "total_questions": sum(item["question_count"] for item in interviews),
        "workflow": WorkflowEngine(mode).status(),
    }


def render_rri_plan(config: dict[str, Any]) -> str:
    """Render persona-scoped RRI plan as Markdown."""
    bridge = build_rri_bridge(config)
    lines = [
        f"# Prompt Architect RRI plan: {config['name']}",
        "",
        f"- Mode: `{bridge['mode']}`",
        f"- Personas: `{', '.join(bridge['personas'])}`",
        f"- Total questions: `{bridge['total_questions']}`",
        "",
        "## Persona interviews",
    ]
    for interview in bridge["interviews"]:
        lines.extend([
            "",
            f"### {interview['persona']} — {interview['role']}",
            "",
            "Reasons:",
            *[f"- {reason}" for reason in interview["reasons"]],
            "",
            "Questions:",
        ])
        for question in interview["questions"]:
            lines.append(f"- Q{question.get('id')}: {question.get('text')}")
    lines.extend([
        "",
        "## Workflow bridge",
        "",
        "- Step 2 RRI must be answered before finalizing Step 3 vision and Step 4 blueprint.",
        "- Generated requirements must remain traceable to RRI answers and vibecodekit gates.",
    ])
    return "\n".join(lines) + "\n"
