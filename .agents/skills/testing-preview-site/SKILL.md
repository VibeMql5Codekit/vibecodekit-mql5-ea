---
name: testing-vibecodekit-mql5-ea
description: Test the vibecodekit-mql5-ea preview site and CLI tools end-to-end. Use when verifying preview site UI, scaffold generator, lint checker, or CLI tool changes.
---

# Testing vibecodekit-mql5-ea

## Prerequisites

- Python 3 with pytest installed
- Preview site deployed to devinapps.com (static HTML, no backend)
- Repo cloned at `/home/ubuntu/repos/vibecodekit-mql5-ea`
- Install: `pip install -e ".[dev]"`

## Devin Secrets Needed

None — no secrets required for testing. The preview site is public and CLI tools run locally.

## Preview Site URL

The preview site is deployed as a static frontend. Check for the deployment URL in PR comments or use the `deploy` tool with `command="frontend"` pointing to the preview directory.

## Test Procedure

### 1. CLI Tools (Shell — No Recording Needed)

Run these from the repo root:

```bash
cd /home/ubuntu/repos/vibecodekit-mql5-ea

# Full test suite
pytest tests/ -q
# Expected: 107 passed, 2 skipped (Wine/MetaEditor deps), 0 failed

# Lint CLI on fixture
mql5-lint tests/fixtures/ap_01_no_sl.mq5
# Expected: AP-01 detected, exit code 1

# Build presets count
python -c "import sys; sys.path.insert(0,'scripts'); from vibecodekit_mql5.build import list_presets; print(len(list_presets()))"
# Expected: 17
```

### 2. Scaffold Stack Validation

Test that `--stack` is validated per-preset (not just accepted blindly):

```bash
# Single-stack preset with wrong default — should reject with helpful error
mql5-build --preset dca --name Test --output /tmp/test-stack 2>&1
# Expected: exit 2, "Invalid stack 'netting' for preset 'dca'. Available: hedging"

# Single-stack preset with correct stack — should succeed
mql5-build --preset dca --stack hedging --name Test --output /tmp/test-stack
# Expected: exit 0, "Rendered dca/hedging"

# Multi-stack preset with invalid stack — lists all valid options
mql5-build --preset stdlib --stack nonexistent --name Bad --output /tmp/test-stack 2>&1
# Expected: exit 2, "Available: hedging, netting, python-bridge"

# Non-standard stacks (service-llm-bridge has cloud-api, embedded-onnx-llm, self-hosted-ollama)
mql5-build --preset service-llm-bridge --stack netting --name Bad --output /tmp/test-stack 2>&1
# Expected: exit 2, "Available: cloud-api, embedded-onnx-llm, self-hosted-ollama"
```

### 3. Permission Pipeline Testing

```bash
# Test permission orchestrator
python -c "
import sys; sys.path.insert(0, 'scripts')
from vibecodekit_mql5.permission.orchestrator import run_permission_pipeline
import json
r = run_permission_pipeline('scaffolds/stdlib/netting/EAName.mq5', mode='PERSONAL')
print(json.dumps(r, indent=2))
"
# Note: layer4 requires >= 15/17 PASS (not 10). Scaffold gets ~12 so layer4 will fail.
```

### 4. Forge Fitness Evaluation

```bash
# Test evaluate_fitness with backtest JSON keys
python -c "
import sys; sys.path.insert(0, 'scripts')
from vibecodekit_mql5.forge_pr import evaluate_fitness
cfg = {'primary': 'profit_factor', 'secondary': 'sharpe_ratio',
       'constraints': {'max_drawdown_pct': 30, 'min_trades': 100}}
# Use maximal_drawdown_pct (the key from real backtest JSON output)
metrics = {'profit_factor': 1.52, 'sharpe_ratio': 1.34,
           'maximal_drawdown_pct': 10.23, 'total_trades': 728}
print(evaluate_fitness(metrics, cfg))
# Expected: positive score (e.g. 1.448), NOT -1.0
"
```

### 5. Preview Site (Browser — Record This)

Maximize browser before recording:
```bash
sudo apt-get install -y wmctrl 2>/dev/null
wmctrl -r :ACTIVE: -b add,maximized_vert,maximized_horz
```

#### Navigation Test
- Click each of the 9 tabs: Overview, 6 Phases, MQL5 Libraries, CLI Tools, 19 Scaffolds, Anti-Patterns, Tests, Try It, Architecture
- Verify each tab switches content correctly

#### Scaffold Generator ("Try It" tab)
1. Select preset, stack, type EA name
2. Click "Generate Scaffold"
3. Verify output contains EA name, 3 includes, strategy placeholder

#### Lint Checker ("Try It" tab)
1. Default code has 3 violations
2. Click "Run Lint Check"
3. Verify: AP-01, AP-15, AP-20 detected, "3 critical, 0 warnings"

## Common Issues

- The 2 skipped tests require Wine + MetaEditor — expected on Linux
- Scaffold AP-05 warnings (> 6 inputs) are expected for templates
- The preview site is purely client-side JS — no API calls, no backend
- `PYTHONPATH=scripts` or `pip install -e .` required for CLI module imports
- No CI runners may be configured on new repos — check Settings → Actions
- Backtest JSON output uses `maximal_drawdown_pct` key, but internal BacktestMetrics dataclass uses `max_drawdown_pct` — evaluate_fitness handles both
- Layer4 permission threshold is >= 15/17 PASS (matching trader_check.py standalone CLI)
- CAsyncTradeManager uses CTrade::Result() to get MqlTradeResult.request_id for async tracking (not ResultOrder())
- Some presets only have one stack (e.g. dca→hedging, scalping→hedging) — default `--stack netting` will fail for these. The CLI now shows available stacks in the error message.
- service-llm-bridge uses non-standard stacks: cloud-api, embedded-onnx-llm, self-hosted-ollama (not netting/hedging/python-bridge)
