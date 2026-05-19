# vibecodekit-mql5-ea

Vibecode methodology kit for MQL5 Expert Advisor development on MetaTrader 5.

> **Status:** Phase 0-F in progress. Current verified local gate: 169 passed, 2 skipped
> (Wine/MetaEditor-dependent smoke tests), 46 CLI tools, 17 scaffold presets / 22 preset×stack combinations.

## Quick start

```bash
# Install
pip install -e ".[dev]"

# Run tests
pytest tests/ -q
# → 169 passed, 2 skipped locally when Wine/MetaEditor are unavailable

# List all scaffold presets
mql5-build --list
# → 17 presets / 22 preset×stack combinations

# Build an EA
mql5-build --preset stdlib --stack netting --name MyEA --output ./output

# Lint
mql5-lint output/MyEA/MyEA.mq5

# Permission pipeline
mql5-permission --ea output/MyEA/MyEA.mq5 --mode PERSONAL --json
```

## Features

| Category | Count | Description |
|----------|-------|-------------|
| CLI Tools | 46 | Build, lint, compile, backtest, walk-forward, Monte Carlo, permissions, reviews, deploy |
| Scaffold Presets | 17 / 22 stacks | stdlib, scalping, trend, dca, grid, ml-onnx, hft-async, news-trading, etc. |
| MQL5 Libraries | 7 | CPipNormalizer, CRiskGuard, CMagicRegistry, CSpreadGuard, COnnxLoader, CAsyncTradeManager, CMfeMaeLogger |
| Tests | 171 collected | Phase 0-F acceptance tests (169 pass, 2 Wine/MetaEditor skips in local Linux smoke) |
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
- [Complete Guide](docs/GUIDE-COMPLETE.md) — Full user/team workflow and command reference
- [New Session Guide](docs/GUIDE-NEW-SESSION.md) — Demo on Devin/Codex/Claude Code
- [Audit Report](docs/AUDIT-REVIEW.md) — Bug fixes and review history
- [Plan v5](docs/PLAN-v5.md) — Original 1089-line spec

## CLI command groups

### Core build + quality

| Command | Purpose |
|---------|---------|
| `mql5-build --list` | Discover all 17 presets and valid stacks |
| `mql5-build --preset <preset> --stack <stack> --name <EA>` | Render scaffold and rename `EAName` placeholders |
| `mql5-lint <file-or-dir>` | Detect 8 critical and 5 warning anti-pattern classes |
| `mql5-pip-normalize <paths> [--fix]` | Detect/fix hardcoded pip math |
| `mql5-compile <file.mq5>` | Compile via MetaEditor/Wine when configured |

### Validation + deployment gates

| Command | Purpose |
|---------|---------|
| `mql5-backtest <report.xml>` | Parse MT5 Strategy Tester XML |
| `mql5-walkforward <is.xml> <oos.xml>` | Validate IS/OOS degradation |
| `mql5-monte-carlo <report.xml>` | Simulate drawdown robustness |
| `mql5-multibroker <reports...>` | Check cross-broker stability |
| `mql5-trader-check --ea <file.mq5>` | Run Trader-17 pre-deploy checklist |
| `mql5-permission --ea <file.mq5> --mode <PERSONAL|TEAM|ENTERPRISE>` | Run fail-fast permission pipeline |
| `mql5-broker-safety --ea <file.mq5>` | Run Layer 7 pip/broker safety gate |
| `mql5-deploy-vps --ea <file.ex5>` | Generate VPS deployment checklist |
| `mql5-canary --terminal-log <log>` | Analyze post-deploy terminal logs |

### Methodology, review, and planning

| Command | Purpose |
|---------|---------|
| `mql5-rri --mode <mode>` | Generate Reverse Requirements Interview questions |
| `mql5-rri-bt --personas all` | Backtest-focused RRI review and 64-cell matrix summary |
| `mql5-rri-rr --persona all` | Risk-reward-focused RRI questions |
| `mql5-rri-chart --persona all` | Chart/indicator-focused RRI questions |
| `mql5-matrix --mode <mode> [--html report.html]` | Render 8×8 quality matrix |
| `mql5-review --ea <file.mq5>` | 7-perspective adversarial review |
| `mql5-eng-review --ea <file.mq5>` | Engineering invariant review |
| `mql5-cso --ea <file.mq5>` | Security audit |
| `mql5-ceo-review --ea <file.mq5>` | Scope/business decision review |
| `mql5-investigate --ea <file.mq5> --symptom "..."` | Root-cause investigation |
| `mql5-second-opinion --ea <file.mq5> --focus risk` | Generate external LLM review prompt |
| `mql5-prompt-architect --config ea-settings.yaml --rri-plan rri-plan.md --pipeline pipeline.json` | Convert normalized EA settings into RRI plan and next pipeline commands |
| `mql5-prompt-architect --config ea-settings.yaml --llm-provider prompt-only --llm-output codegen-prompt.md` | Prepare a safe optional LLM codegen prompt without network calls |
| `mql5-prompt-architect --run-pipeline pipeline.json [--execute]` | Validate, dry-run, or execute the deterministic Prompt Architect pipeline plan |

### Advanced tech + repo tooling

| Command | Purpose |
|---------|---------|
| `mql5-onnx-export --model <model>` / `mql5-onnx-embed --onnx <model.onnx>` | ONNX export/embed helpers |
| `mql5-async-build --name <EA>` | HFT async scaffold helper |
| `mql5-cloud-optimize --ea <file.mq5> --mode <mode> --budget <usd>` | Cloud Network optimization cost gate |
| `mql5-method-hiding-check --ea <file.mq5>` | Detect MQL5 method hiding risks |
| `mql5-llm-context --variant <cloud-api|embedded-onnx|self-hosted>` | LLM bridge context helper |
| `mql5-forge-init --ea <file.mq5>` / `mql5-forge-pr` | Algo Forge workspace and candidate ranking |
| `mql5-scan`, `mql5-survey`, `mql5-doctor`, `mql5-audit` | Repo scan, preset taxonomy, install health, conformance audit |
| `mql5-vision`, `mql5-blueprint`, `mql5-tip`, `mql5-refine` | Vision/blueprint/TIP/diff-classification workflow |
| `mql5-install --target <MQL5-dir> [--dry-run]` | Install Include/scaffold overlay into another MT5 project |
| `mql5-ship --version <semver> --dry-run` | Release tag workflow preview |

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
