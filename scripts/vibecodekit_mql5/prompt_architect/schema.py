"""Schema loading and fail-closed validation for Prompt Architect configs."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[3]
PROMPT_ARCHITECT_DIR = REPO_ROOT / "docs" / "prompt-architect"
SCHEMA_PATH = PROMPT_ARCHITECT_DIR / "ea-settings.schema.json"
CONFLICT_RULES_PATH = PROMPT_ARCHITECT_DIR / "conflict-rules.yaml"

ALLOWED_TIMEFRAMES = {"M1", "M5", "M15", "M30", "H1", "H4", "D1", "W1", "MN1"}
ALLOWED_DIRECTIONS = {"buy", "sell", "both"}
ALLOWED_METHODS = {
    "one_shot", "trend", "mean_reversion", "scalping", "grid", "dca", "martingale",
    "hedging", "breakout", "news", "portfolio", "onnx", "custom",
}
ALLOWED_BROKER_MODES = {"netting", "hedging", "unknown"}
ALLOWED_ACCOUNT_TYPES = {"demo", "live", "personal", "prop_firm"}
ALLOWED_LOT_MODES = {"fixed", "percent_risk"}
ALLOWED_SLTP_MODES = {"fixed_points", "atr", "candle", "virtual", "none"}

SECRET_NEEDLES = ("api_key", "telegram_token", "license_key", "password", "broker_password")


def load_yaml_or_json(path: Path) -> dict[str, Any]:
    """Load a YAML or JSON object from disk."""
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() == ".json":
        data = json.loads(text)
    else:
        data = yaml.safe_load(text)
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain an object")
    return data


def load_config(path: Path) -> dict[str, Any]:
    """Load a Prompt Architect config file."""
    return load_yaml_or_json(path)


def load_schema() -> dict[str, Any]:
    """Load the canonical Prompt Architect schema."""
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def load_conflict_rules() -> dict[str, Any]:
    """Load declarative conflict-rule metadata for reporting."""
    return yaml.safe_load(CONFLICT_RULES_PATH.read_text(encoding="utf-8"))


def _field(data: dict[str, Any], path: str) -> Any:
    current: Any = data
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def _missing(data: dict[str, Any], path: str) -> bool:
    value = _field(data, path)
    return value is None or value == "" or value == []


def _append(errors: list[str], message: str) -> None:
    if message not in errors:
        errors.append(message)


def validate_config(config: dict[str, Any]) -> dict[str, Any]:
    """Validate required schema semantics and high-risk conflict rules."""
    errors: list[str] = []
    warnings: list[str] = []

    required = [
        "schema_version", "name", "symbol", "timeframe", "direction", "trading_method",
        "broker_mode", "account_type", "strategy", "risk", "execution", "sltp", "features",
    ]
    for key in required:
        if key not in config:
            _append(errors, f"missing required field: {key}")

    if errors:
        return {"valid": False, "errors": errors, "warnings": warnings}

    if config.get("schema_version") != "1.0":
        _append(errors, "schema_version must be 1.0")
    name = str(config.get("name", ""))
    if not re.match(r"^[A-Za-z][A-Za-z0-9_]{2,63}$", name):
        _append(errors, "name must match ^[A-Za-z][A-Za-z0-9_]{2,63}$")
    if config.get("timeframe") not in ALLOWED_TIMEFRAMES:
        _append(errors, f"timeframe must be one of {sorted(ALLOWED_TIMEFRAMES)}")
    if config.get("direction") not in ALLOWED_DIRECTIONS:
        _append(errors, f"direction must be one of {sorted(ALLOWED_DIRECTIONS)}")
    if config.get("trading_method") not in ALLOWED_METHODS:
        _append(errors, f"trading_method must be one of {sorted(ALLOWED_METHODS)}")
    if config.get("broker_mode") not in ALLOWED_BROKER_MODES:
        _append(errors, f"broker_mode must be one of {sorted(ALLOWED_BROKER_MODES)}")
    if config.get("account_type") not in ALLOWED_ACCOUNT_TYPES:
        _append(errors, f"account_type must be one of {sorted(ALLOWED_ACCOUNT_TYPES)}")

    strategy = config.get("strategy", {})
    if not isinstance(strategy, dict):
        _append(errors, "strategy must be an object")
        strategy = {}
    for key in ["description", "entry_logic", "exit_logic", "indicators"]:
        if _missing(config, f"strategy.{key}"):
            _append(errors, f"strategy.{key} is required")
    if len(str(strategy.get("description", ""))) < 10:
        _append(errors, "strategy.description must be at least 10 characters")
    if not isinstance(strategy.get("indicators", []), list):
        _append(errors, "strategy.indicators must be a list")

    risk = config.get("risk", {})
    if not isinstance(risk, dict):
        _append(errors, "risk must be an object")
        risk = {}
    lot_mode = risk.get("lot_mode")
    if lot_mode not in ALLOWED_LOT_MODES:
        _append(errors, f"risk.lot_mode must be one of {sorted(ALLOWED_LOT_MODES)}")
    if lot_mode == "percent_risk" and _missing(config, "risk.risk_percent"):
        _append(errors, "PA-001: percent-risk lot mode requires risk.risk_percent")
    if lot_mode == "fixed" and _missing(config, "risk.fixed_lot"):
        _append(errors, "PA-002: fixed lot mode requires risk.fixed_lot")
    if int(risk.get("max_open_positions", 0) or 0) < 1:
        _append(errors, "risk.max_open_positions must be >= 1")

    execution = config.get("execution", {})
    if not isinstance(execution, dict):
        _append(errors, "execution must be an object")
        execution = {}
    for key in ["max_spread_points", "slippage_points", "filling_mode"]:
        if _missing(config, f"execution.{key}"):
            _append(errors, f"execution.{key} is required")

    sltp = config.get("sltp", {})
    if not isinstance(sltp, dict):
        _append(errors, "sltp must be an object")
        sltp = {}
    if sltp.get("mode") not in ALLOWED_SLTP_MODES:
        _append(errors, f"sltp.mode must be one of {sorted(ALLOWED_SLTP_MODES)}")
    if config.get("account_type") in {"live", "prop_firm"} and sltp.get("mode") == "none":
        _append(errors, "PA-008: live or prop-firm EAs require an explicit stop policy")

    grid = config.get("grid", {})
    if isinstance(grid, dict) and grid.get("enabled"):
        for key in ["max_orders", "distance_points"]:
            if _missing(config, f"grid.{key}"):
                _append(errors, f"PA-003: enabled grid requires grid.{key}")
        if _missing(config, "risk.max_drawdown_percent"):
            _append(errors, "PA-003: enabled grid requires risk.max_drawdown_percent")

    filters = config.get("filters", {})
    integrations = config.get("integrations", {})
    if isinstance(filters, dict) and filters.get("avoid_news"):
        has_webrequest = isinstance(integrations, dict) and bool(integrations.get("webrequest"))
        has_manual_policy = "manual news calendar" in str(config.get("notes", "")).lower()
        if not has_webrequest and not has_manual_policy:
            _append(errors, "PA-004: avoid_news requires WebRequest or a manual news policy")

    if config.get("account_type") == "prop_firm":
        for path in ["risk.max_daily_loss_percent", "risk.max_drawdown_percent"]:
            if _missing(config, path):
                _append(warnings, f"PA-005: prop-firm accounts should specify {path}")

    if isinstance(integrations, dict) and integrations.get("custom_indicator"):
        if not strategy.get("indicators"):
            _append(errors, "PA-006: custom indicator logic requires strategy.indicators")

    if isinstance(integrations, dict) and integrations.get("onnx"):
        notes = str(config.get("notes", "")).lower()
        has_threshold = any(
            item.get("type") == "onnx" and "confidence_threshold" in item.get("params", {})
            for item in strategy.get("indicators", [])
            if isinstance(item, dict)
        )
        if not has_threshold and "confidence threshold" not in notes:
            _append(warnings, "PA-007: ONNX strategies should define confidence threshold")

    if config.get("broker_mode") == "unknown":
        _append(warnings, "PA-010: unknown broker mode requires broker-engineer RRI review")

    serialized = json.dumps(config, ensure_ascii=False).lower()
    for needle in SECRET_NEEDLES:
        if needle in serialized:
            _append(errors, f"PA-009: config must not contain secret-like field '{needle}'")

    return {"valid": not errors, "errors": errors, "warnings": warnings}
