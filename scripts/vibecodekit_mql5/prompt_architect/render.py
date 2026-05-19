"""Deterministic renderers for Prompt Architect outputs."""
from __future__ import annotations

import json
from typing import Any

from vibecodekit_mql5.prompt_architect.recommend import recommend_preset


def _indicator_summary(config: dict[str, Any]) -> str:
    indicators = config.get("strategy", {}).get("indicators", [])
    lines = []
    for indicator in indicators:
        params = indicator.get("params", {}) if isinstance(indicator, dict) else {}
        params_text = ", ".join(f"{key}={value}" for key, value in params.items()) or "default"
        lines.append(f"- {indicator.get('type')}: {indicator.get('condition')} ({params_text})")
    return "\n".join(lines) if lines else "- none"


def _non_goals(config: dict[str, Any]) -> str:
    items = config.get("strategy", {}).get("non_goals", [])
    return "\n".join(f"- {item}" for item in items) if items else "- none"


def render_prompt(config: dict[str, Any]) -> str:
    """Render a deterministic MQL5 implementation prompt."""
    strategy = config["strategy"]
    risk = config["risk"]
    execution = config["execution"]
    sltp = config["sltp"]
    recommendation = recommend_preset(config)
    return f"""# {config['name']} — MQL5 EA technical prompt

## Goal

Build an MQL5 Expert Advisor for `{config['symbol']}` on `{config['timeframe']}` using `{config['trading_method']}`.

## Trading logic

- Direction: `{config['direction']}`
- Entry: {strategy['entry_logic']}
- Exit: {strategy['exit_logic']}
- Indicators:
{_indicator_summary(config)}

## Risk and execution constraints

- Lot mode: `{risk['lot_mode']}`
- Max open positions: `{risk['max_open_positions']}`
- Max spread: `{execution['max_spread_points']}` points
- Slippage: `{execution['slippage_points']}` points
- SL/TP mode: `{sltp['mode']}`

## Scaffold recommendation

Use `mql5-build --preset {recommendation['preset']} --stack {recommendation['stack']} --name {config['name']} --output ./work/`.

## Required vibecodekit gates

```bash
mql5-lint <ea.mq5>
mql5-compile <ea.mq5>
mql5-permission --ea <ea.mq5> --mode <mode>
mql5-matrix --mode <mode>
```

## Implementation requirements

- Use broker-safe pip/point normalization.
- Keep secrets out of source code and generated prompts.
- Prefer existing vibecodekit libraries and scaffold conventions.
- Emit explicit errors for unsupported broker/account constraints.
"""


def render_vision(config: dict[str, Any]) -> str:
    """Render a deterministic vision document."""
    risk = config["risk"]
    recommendation = recommend_preset(config)
    return f"""# Vision: {config['name']}

## One-line goal

{config['strategy']['description']}

## KPIs

- Risk per trade: `{risk.get('risk_percent', 'fixed lot')}`
- Max drawdown: `{risk.get('max_drawdown_percent', 'not specified')}`
- Max open positions: `{risk['max_open_positions']}`

## Non-goals

{_non_goals(config)}

## Stack

- Symbol: `{config['symbol']}`
- Timeframe: `{config['timeframe']}`
- Broker mode: `{config['broker_mode']}`
- Recommended preset: `{recommendation['preset']}`
- Recommended stack: `{recommendation['stack']}`
"""


def requirements_data(config: dict[str, Any]) -> dict[str, Any]:
    """Build machine-readable REQ-* traceability data."""
    return {
        "schema_version": "1.0",
        "ea": config["name"],
        "requirements": [
            {
                "id": "REQ-001",
                "source": "symbol",
                "statement": f"EA must trade {config['symbol']} on {config['timeframe']}.",
                "gate": "layer1_source_lint",
            },
            {
                "id": "REQ-002",
                "source": "risk",
                "statement": "EA must enforce configured lot mode and risk caps.",
                "gate": "layer4_checklist",
            },
            {
                "id": "REQ-003",
                "source": "execution",
                "statement": "EA must block entries when spread or execution constraints fail.",
                "gate": "layer7_broker_safety",
            },
            {
                "id": "REQ-004",
                "source": "sltp",
                "statement": "EA must implement explicit stop/exit policy.",
                "gate": "layer3_ap_lint",
            },
            {
                "id": "REQ-005",
                "source": "strategy",
                "statement": "EA entry and exit logic must match the normalized strategy.",
                "gate": "layer5_methodology",
            },
        ],
    }


def render_requirements(config: dict[str, Any]) -> str:
    """Render requirements as stable JSON text."""
    return json.dumps(requirements_data(config), indent=2)


def render_blueprint(config: dict[str, Any]) -> str:
    """Render a deterministic blueprint document."""
    recommendation = recommend_preset(config)
    return f"""# Blueprint: {config['name']}

## Architecture

Use `mql5-build --preset {recommendation['preset']} --stack {recommendation['stack']} --name {config['name']}`.

## Data flow

1. OnTick guard checks risk, spread, session, and news constraints.
2. Indicator layer calculates signals from normalized strategy settings.
3. Execution layer opens/closes positions according to broker mode.
4. Protection layer enforces drawdown, daily loss, and max-position caps.

## Includes

- CPipNormalizer for point/pip safety
- CRiskGuard for risk and drawdown checks
- CMagicRegistry for isolated order management
- CSpreadGuard when spread filtering is enabled

## Invariants

- No hardcoded secrets.
- No unbounded martingale/grid loops.
- No live/proprietary account deployment without permission pipeline pass.
- Missing evidence must fail closed in quality matrix.

## Verification

```bash
mql5-lint <ea.mq5>
mql5-compile <ea.mq5>
mql5-permission --ea <ea.mq5> --mode <mode>
mql5-matrix --mode <mode> --html matrix.html
```
"""
