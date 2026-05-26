# vibecodekit-mql5-ea

A CLI-first, fail-closed methodology kit for MQL5 Expert Advisor development on
MetaTrader 5.

- **15-minute hands-on tour:** [`docs/QUICKSTART.md`](docs/QUICKSTART.md) (English) ·
  [`docs/QUICKSTART.vi.md`](docs/QUICKSTART.vi.md) (Tiếng Việt)
- **AI coding agents (Devin / Claude Code / Cursor / Codex):** read [`AGENTS.md`](AGENTS.md)
- **What the gates actually report on a fresh scaffold:** [`docs/reference-ea/REPORT.md`](docs/reference-ea/REPORT.md)

> **Honest disclaimer.** `Trader-17`, the `8×8 quality matrix`, the `AP-XX`
> anti-pattern IDs, the `7-layer permission pipeline`, and the `RRI personas`
> are **project-defined heuristics** designed by this kit. They are opinionated
> guardrails — not industry standards, not certifications, and not substitutes
> for live-account validation.

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

| Category | What you get | Notes |
|----------|--------------|-------|
| Scaffold presets | 17 strategy templates (22 preset × stack combos): stdlib, scalping, trend, dca, grid, ml-onnx, hft-async, news-trading, etc. | `mql5-build --list` |
| MQL5 libraries | `CPipNormalizer` (cross-broker pip math), `CRiskGuard`, `CMagicRegistry`, `CSpreadGuard`, `CMfeMaeLogger`, `COnnxLoader`, `CAsyncTradeManager` | shipped in [`Include/`](Include/) |
| CLI tools | Build, lint, compile, backtest, walk-forward, Monte Carlo, multi-broker, permission gate, RRI / Prompt Architect, review utilities | run any with `--help`; the five you'll use most: `mql5-build`, `mql5-lint`, `mql5-trader-check`, `mql5-permission`, `mql5-compile` |
| Test suite | Local baseline `pytest tests/ -q` → **169 passed, 2 skipped** when Wine/MetaEditor smoke deps are unavailable | regression harness, not user surface |
| MCP servers | `metaeditor-bridge`, `mt5-bridge` (read-only market/account info), `algo-forge-bridge` | thin JSON-RPC adapters |
| Reference docs | Methodology, broker engineering, ONNX, anti-pattern catalogue | [`docs/`](docs/) |

## Empirical reference numbers

When the kit's gates run against a **freshly scaffolded EA with no strategy
written yet**:

| Gate | Result on bare scaffold |
|---|---|
| `mql5-lint` | 0 critical, 4 warnings (placeholder template artefacts) |
| `mql5-trader-check` | 11 / 17 PASS, 6 N-A → **FAIL** (gate requires ≥ 15) |
| `mql5-permission --mode PERSONAL` | **FAIL** at layer 4 (Trader-17 fail-fast) |
| `mql5-matrix` (standalone, no evidence) | 0 / 64 PASS — CLI floor, not a measurement |
| `mql5-rri-bt` (no `--report`) | 56 / 64 PASS — structural maximum, not a measurement |

The full machine-readable snapshot lives at
[`docs/reference-ea/REPORT.md`](docs/reference-ea/REPORT.md). Regenerate with
`bash scripts/tools/build_reference_report.sh`. A bare scaffold is **expected
to fail** the permission gate — the gate has teeth and demands real evidence
(working strategy + walk-forward + multi-broker + Monte Carlo + overfit
check) before passing.

## Documentation

- **For users:**
  - [Quickstart (English)](docs/QUICKSTART.md) / [Quickstart (Tiếng Việt)](docs/QUICKSTART.vi.md) — 15-minute hands-on tour with screenshots
  - [Build EA Guide](docs/GUIDE-BUILD-EA.md) — Step-by-step pipeline (Vietnamese)
  - [Complete Guide](docs/GUIDE-COMPLETE.md) — Full workflow and command reference
  - [New Session Guide](docs/GUIDE-NEW-SESSION.md) — Demo on Devin/Codex/Claude Code
  - [Reference-EA report](docs/reference-ea/REPORT.md) — Honest empirical gate numbers
- **For AI agents:**
  - [`AGENTS.md`](AGENTS.md) — CLI surface, output schema, gate semantics, rule_id → doc anchor table
- **For contributors (internal sprint docs):**
  - [Audit Report](docs/AUDIT-REVIEW.md), [Plan v5](docs/PLAN-v5.md), and `docs/phase-*-spec.md` — these record the kit's own development milestones; users do not need them

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
