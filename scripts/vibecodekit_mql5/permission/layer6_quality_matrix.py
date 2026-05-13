#!/usr/bin/env python3
"""Permission Layer 6: quality_matrix — 8×8 quality assessment."""
from __future__ import annotations

import re
from pathlib import Path

DIMS = [
    "reliability", "performance", "security",
    "maintainability", "testability", "portability",
    "usability", "compliance",
]

AXES = [
    "error_handling", "resource_mgmt", "input_validation",
    "code_structure", "documentation", "configurability",
    "broker_compat", "risk_control",
]

CHECKS: dict[tuple[str, str], tuple[str, float]] = {
    ("reliability", "error_handling"):
        (r"(?:GetLastError|ResultRetcode|TRADE_RETCODE)", 1.0),
    ("reliability", "resource_mgmt"):
        (r"(?:OnDeinit|delete\s|ArrayFree)", 1.0),
    ("reliability", "risk_control"):
        (r"(?:CRiskGuard|StopLoss|SL)", 1.0),
    ("performance", "resource_mgmt"):
        (r"(?:ArrayResize.*reserve|StringConcatenate)", 0.5),
    ("performance", "code_structure"):
        (r"(?:static\s|const\s)", 0.5),
    ("security", "input_validation"):
        (r"(?:NormalizeDouble|MathMax|MathMin)", 1.0),
    ("security", "risk_control"):
        (r"(?:MaxPos|max_positions|DailyLoss)", 1.0),
    ("maintainability", "code_structure"):
        (r"(?:class\s+\w+|#include\s)", 1.0),
    ("maintainability", "documentation"):
        (r"(?:#property\s+description|//\+--)", 0.5),
    ("testability", "configurability"):
        (r"(?:input\s+\w+|extern\s+\w+)", 1.0),
    ("portability", "broker_compat"):
        (r"(?:CPipNormalizer|Digits|_Digits)", 1.0),
    ("portability", "configurability"):
        (r"(?:AccountInfoInteger|SymbolInfoDouble)", 0.5),
    ("usability", "documentation"):
        (r"(?:Comment\(|Print(?:Format)?\()", 0.5),
    ("compliance", "risk_control"):
        (r"(?:CRiskGuard|CMagicRegistry)", 1.0),
    ("compliance", "broker_compat"):
        (r"(?:CSpreadGuard|SPREAD)", 0.5),
    ("compliance", "input_validation"):
        (r"(?:#property\s+strict)", 1.0),
}


def check(ea_path: str, **kwargs: object) -> dict:
    """Run 8×8 quality matrix. Returns scores per dim."""
    p = Path(ea_path)
    if not p.exists():
        return {"pass": False, "layer": 6, "name": "quality_matrix",
                "details": f"File not found: {ea_path}"}

    content = p.read_text(encoding="utf-8", errors="replace")
    scores: dict[str, float] = {d: 0.0 for d in DIMS}
    max_scores: dict[str, float] = {d: 0.0 for d in DIMS}

    for (dim, _axis), (pattern, weight) in CHECKS.items():
        max_scores[dim] += weight
        if re.search(pattern, content):
            scores[dim] += weight

    pcts: dict[str, int] = {}
    for d in DIMS:
        pcts[d] = int(100 * scores[d] / max_scores[d]) if max_scores[d] else 100

    avg = sum(pcts.values()) // len(pcts)
    ok = avg >= 40 and all(v >= 20 for v in pcts.values())

    return {"pass": ok, "layer": 6, "name": "quality_matrix",
            "details": f"avg={avg}% ({', '.join(f'{d}={v}%' for d, v in pcts.items())})",
            "scores": pcts, "average": avg}
