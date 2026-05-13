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
- For mobile testing: `pip install playwright && python -m playwright install chromium`

## Devin Secrets Needed

None — no secrets required for testing. The preview site is public and CLI tools run locally.

## Preview Site URL

The preview site is deployed as a static frontend. Check for the deployment URL in PR comments or use the `deploy` tool with `command="frontend"` pointing to the preview directory.

**CDN Cache Workaround:** After deploying, the CDN may serve stale content. Append `?nocache=<unique-param>` to the URL to force fresh content (e.g. `?nocache=fix1`). Verify with curl that your CSS changes are present before testing.

## Test Procedure

### 1. CLI Tools (Shell — No Recording Needed)

Run these from the repo root:

```bash
cd /home/ubuntu/repos/vibecodekit-mql5-ea

# Full test suite
pytest tests/ -q
# Expected: 148 passed, 2 skipped (Wine/MetaEditor deps), 0 failed

# Lint CLI on fixture
mql5-lint tests/fixtures/ap_01_no_sl.mq5
# Expected: AP-01 detected, exit code 1

# Build presets count
mql5-build --list
# Expected: 17 presets listed
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
python -c "
import sys; sys.path.insert(0, 'scripts')
from vibecodekit_mql5.permission.orchestrator import run_permission_pipeline
import json
r = run_permission_pipeline('scaffolds/stdlib/netting/EAName.mq5', mode='PERSONAL')
print(json.dumps(r, indent=2))
"
# Note: layer4 requires >= 15/17 PASS (not 10). Scaffold gets ~12 so layer4 will fail.
```

### 4. Phase C — Methodology Validation

```bash
# RRI Personas: verify 25 questions each (was 12 before)
python -c "
import yaml
for p in ['trader','risk-auditor','broker-engineer','strategy-architect','devops','perf-analyst']:
    d = yaml.safe_load(open(f'docs/rri-personas/{p}.yaml'))
    print(f'{p}: {len(d["questions"])} questions')
"
# Expected: all 6 show 25

# RRI Templates: verify 8 files
ls docs/rri-templates/step-*.md.tmpl | wc -l
# Expected: 8

# Review scripts: verify not stubs
for f in review eng_review ceo_review cso investigate; do
  wc -l scripts/vibecodekit_mql5/review/${f}.py
done
# Expected: all > 30 LOC (was 13 LOC stubs)
```

### 5. Phase D — Tech 2024 Adversarial Tests

```bash
python -c "
from vibecodekit_mql5.onnx_export import detect_framework, validate_opset
from pathlib import Path
# Framework detection
for ext, expected in [('.pt','pytorch'),('.h5','tensorflow'),('.pkl','sklearn'),('.xyz','unknown')]:
    print(f'{ext} -> {detect_framework(Path(f\"m{ext}\"))} (expected {expected})')
# Opset validation
for opset in [17, 5, 99]:
    ok, msg = validate_opset(opset)
    print(f'opset {opset}: valid={ok}, msg={msg}')
"
# Expected: .pt=pytorch, .h5=tensorflow, .pkl=sklearn, .xyz=unknown
# opset 17 valid, 5 rejected 'too low', 99 rejected 'too high'

# Cost gate
python -c "
from vibecodekit_mql5.cloud_optimize import check_cost_gate
for mode, cost, expected in [('PERSONAL',10,False),('TEAM',30,True),('TEAM',100,False),('ENTERPRISE',200,True),('ENTERPRISE',600,False)]:
    r = check_cost_gate(mode, cost)
    print(f'{mode} \${cost}: allowed={r[\"allowed\"]} (expected {expected})')
"
# Expected: PERSONAL always blocked, TEAM <=$50 ok, ENTERPRISE <=$500 ok
```

### 6. Phase E — Polish & Ship

```bash
# scan.py on real repo
python -c "
from vibecodekit_mql5.scan import scan_project
from pathlib import Path
r = scan_project(Path('.'))
print(f'mq5={r[\"mq5_count\"]}, pyproject={r[\"has_pyproject\"]}, scaffolds={len(r[\"scaffolds\"])}')
"
# Expected: mq5_count > 0, has_pyproject=True, scaffolds >= 17

# audit.py conformance
python -c "
from vibecodekit_mql5.audit import run_audit
from pathlib import Path
r = run_audit(Path('.'))
print(f'total={r[\"total\"]}, passed={r[\"passed\"]}')
"
# Expected: total >= 40, passed > 30

# MCP tools count
python -c "
import importlib.util
for name, path, min_count in [('mt5','mcp/mt5-bridge/tools.py',10),('forge','mcp/algo-forge-bridge/tools.py',6)]:
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    print(f'{name}: {len(mod.TOOLS)} tools (min {min_count})')
"
# Expected: mt5 >= 10, forge >= 6

# CLI entries
python -c "
import tomllib
with open('pyproject.toml', 'rb') as f:
    cfg = tomllib.load(f)
print(f'CLI entries: {len(cfg[\"project\"][\"scripts\"])}')
"
# Expected: >= 40 (was 4 before Phase E)
```

### 7. Forge Fitness Evaluation

```bash
python -c "
import sys; sys.path.insert(0, 'scripts')
from vibecodekit_mql5.forge_pr import evaluate_fitness
cfg = {'primary': 'profit_factor', 'secondary': 'sharpe_ratio',
       'constraints': {'max_drawdown_pct': 30, 'min_trades': 100}}
metrics = {'profit_factor': 1.52, 'sharpe_ratio': 1.34,
           'maximal_drawdown_pct': 10.23, 'total_trades': 728}
print(evaluate_fitness(metrics, cfg))
"
# Expected: positive score (e.g. 1.448), NOT -1.0
```

### 8. Preview Site (Browser — Record This)

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

### 9. Mobile Responsive Testing (Playwright CDP)

Use Playwright to simulate mobile viewport and programmatically verify no overflow:

```python
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:29229")
        context = browser.contexts[0]
        page = context.pages[0]
        
        await page.goto("<PREVIEW_URL>?nocache=<unique>")
        await page.wait_for_load_state("networkidle")
        await page.set_viewport_size({"width": 375, "height": 812})
        await asyncio.sleep(1)
        
        # Click target tab (e.g. CLI)
        await page.locator("nav button", has_text="Công cụ CLI").click()
        await asyncio.sleep(1)
        
        # Programmatic overflow check
        result = await page.evaluate("""() => {
            const body = document.body;
            const html = document.documentElement;
            return {
                hasHorizontalScroll: body.scrollWidth > body.clientWidth || html.scrollWidth > html.clientWidth,
                bodyWidth: body.scrollWidth,
                viewportWidth: window.innerWidth
            };
        }""")
        print(result)
        # Expected: hasHorizontalScroll = false, bodyWidth <= viewportWidth

asyncio.run(main())
```

**Key tabs to test at 375px:**
- CLI tab: 12 cards with `<pre><code>` blocks — longest is `mql5-build --preset stdlib --stack netting --name MyEA`
- Architecture tab: 2 large ASCII diagrams in `<pre>` blocks
- Any tab with tables: should be wrapped in `<div class="table-wrap">` for horizontal scroll

**Desktop regression check (1280px):** Verify card grid shows multi-column layout (not forced single-column).

## Bilingual (VI/EN) Testing

- Click VI/EN toggle buttons in header
- All elements with class `i18n` should switch language (including nav buttons)
- Verify scaffold generator and lint checker output text switches language

## Common Issues

- The 2 skipped tests require Wine + MetaEditor — expected on Linux
- Scaffold AP-05 warnings (> 6 inputs) are expected for templates
- The preview site is purely client-side JS — no API calls, no backend
- `PYTHONPATH=scripts` or `pip install -e .` required for CLI module imports
- No CI runners may be configured on new repos — check Settings > Actions
- Backtest JSON output uses `maximal_drawdown_pct` key, but internal BacktestMetrics dataclass uses `max_drawdown_pct` — evaluate_fitness handles both
- Layer4 permission threshold is >= 15/17 PASS (matching trader_check.py standalone CLI)
- CAsyncTradeManager uses CTrade::Result() to get MqlTradeResult.request_id for async tracking (not ResultOrder())
- Phase C: RRI personas have 25 questions each (expanded from 12)
- Phase D: onnx_export validates opset 11-20, rejects outside range
- Phase D: cloud_optimize cost gates: PERSONAL=blocked, TEAM<=$50, ENTERPRISE<=$500
- Phase E: 12 scripts (scan, vision, blueprint, tip, survey, doctor, audit, canary, ship, refine, install, second_opinion) all 51-100 LOC
- Phase E: mt5-bridge has 10 tools (4 original + 6 new), algo-forge has 6 tools (3 original + 3 new)
- 44 CLI entry points registered in pyproject.toml
- CDN caching: After deploying preview site updates, append `?nocache=<unique>` to URL to bypass edge cache. Verify CSS changes are present with `curl -s <URL> | grep '<css-property>'` before testing.
- Mobile overflow: CSS grid items default to `min-width: auto` — cards with long `<pre>` content need `min-width: 0; overflow: hidden` to prevent expanding beyond viewport.
- Playwright CDP: Connect to `http://localhost:29229` for programmatic browser control. Use `set_viewport_size` for mobile simulation rather than Chrome DevTools device toolbar.
