# vibecodekit-mql5-ea

Vibecode methodology kit for MQL5 Expert Advisor development on MetaTrader 5.

> **Status:** v1.0.0 — All 6 phases complete. 150 tests pass, 44 CLI tools, 17 scaffold presets.

## Quick start

```bash
# Install
pip install -e ".[dev]"

# Run tests
pytest tests/ -q
# → 150 passed

# List all scaffold presets
mql5-build --list
# → 17 presets × multiple stacks

# Build an EA
mql5-build --preset stdlib --stack netting --name MyEA --output ./output

# Lint
mql5-lint output/MyEA/MyEA.mq5

# Permission pipeline
PYTHONPATH=scripts python -c "
from vibecodekit_mql5.permission.orchestrator import run_permission_pipeline
import json; print(json.dumps(run_permission_pipeline('output/MyEA/MyEA.mq5', 'PERSONAL'), indent=2))
"
```

## Features

| Category | Count | Description |
|----------|-------|-------------|
| CLI Tools | 44 | Build, lint, compile, backtest, walk-forward, Monte Carlo, permissions, reviews, deploy |
| Scaffold Presets | 17 | stdlib, scalping, trend, dca, grid, ml-onnx, hft-async, news-trading, etc. |
| MQL5 Libraries | 7 | CPipNormalizer, CRiskGuard, CMagicRegistry, CSpreadGuard, COnnxLoader, CAsyncTradeManager, CMfeMaeLogger |
| Tests | 150 | Phase 0-E acceptance tests (150 pass, 0 skip) |
| MCP Servers | 3 | metaeditor-bridge, mt5-bridge (10 tools), algo-forge (6 tools) |
| Review Scripts | 5 | 7-perspective review, CSO audit, eng review, CEO review, investigate |
| RRI Personas | 6 | trader, risk-auditor, broker-engineer, strategy-architect, devops, perf-analyst (25 questions each) |
| Reference Docs | 28 | Cheatsheets, methodology guides, best practices |

## Phases

| Phase | Status | Tests | Description |
|-------|--------|-------|-------------|
| 0: Smoke | DONE | 5 | Wine setup, CI, xvfb, pytest, YAML |
| A: Core Foundation | DONE | 37 | CPipNormalizer, CRiskGuard, CMagicRegistry, lint (13 AP), build, pip-normalize |
| B: Test & Validation | DONE | 31 | Backtest, Monte Carlo, multibroker, trader-17, walk-forward, overfit, MFE/MAE |
| C: Methodology | DONE | 21 | 6 RRI personas, 8 templates, 5 review scripts, 7-layer permission, 8×8 matrix |
| D: Tech 2024-2025 | DONE | 23 | ONNX export/embed, async build, cloud cost gate, method hiding, LLM bridge, forge |
| E: Polish & Ship | DONE | 33 | 12 scripts, scan, 50-point audit, MCP servers, worked example, canary |

## Documentation

- [Build EA Guide](docs/GUIDE-BUILD-EA.md) — Step-by-step pipeline (Vietnamese)
- [New Session Guide](docs/GUIDE-NEW-SESSION.md) — Demo on Devin/Codex/Claude Code
- [Audit Report](docs/AUDIT-REVIEW.md) — Bug fixes and review history
- [Plan v5](docs/PLAN-v5.md) — Original 1089-line spec

## Preview Site

Interactive demo: https://vibecodekit-mql5-ea-preview-wpyifglq.devinapps.com

Bilingual (Vietnamese / English), responsive mobile layout.

## Wine + MetaEditor Setup (for compile)

```bash
sudo WINEPREFIX=$HOME/.wine-mql5 bash scripts/setup-wine-metaeditor.sh
source ~/.mql5-env
mql5-compile path/to/EA.mq5
```

## License

MIT
